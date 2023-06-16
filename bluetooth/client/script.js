const connectButton = document.getElementById("connect-button");
const sendMessageButton = document.getElementById("send-message");
const inverterForm = document.getElementById("inverter-form");
const wifiForm = document.getElementById("wifi-form");
const walletForm = document.getElementById("wallet-form");
const internetConnectionStatus = document.getElementById(
  "internet-connection-status"
);

let device;
let server;
let service;
let characteristic;



let messageQueue = [];
let sendingMessage = false;

let gatewayName = null;
let gatewayNameCheckInterval;
let gatewayNameCheckCount = 0;

const output = document.getElementById("output");

const serviceUuid = 'a07498ca-ad5b-474e-940d-16f1fbe7e8cd';
const characteristicUuid = '51ff12bb-3ed8-46e5-b4f9-d64e2fec021b';

function log(message) {
  console.log(message);
  output.innerHTML += message + '\n';
}

connectButton.addEventListener("click", () => {
  if (!device || !device.gatt.connected) {
    connect()
      .then(() => {
        log("Connected");
        sendMessageButton.disabled = false;
        connectButton.textContent = "Disconnect";
        inverterForm.style.display = "block";
        walletForm.style.display = "block";
        wifiForm.style.display = "block";
      })
      .catch((error) => {
        log(error);
      });
  } else {
    disconnect();
    log("Disconnected");
    sendMessageButton.disabled = true;
    connectButton.textContent = "Connect";
    inverterForm.style.display = "none";
    walletForm.style.display = "none";
    wifiForm.style.display = "none";
  }

});

sendMessageButton.addEventListener("click", () => {
  const endpoint = "/api/hello"; // Replace with your desired endpoint

  sendMessage(endpoint, "GET", "")
    .catch((error) => {
      log(error);
    });
});


async function connect() {
  try {
    device = await navigator.bluetooth.requestDevice({
      filters: [{ services: [serviceUuid] }],
    });

    server = await device.gatt.connect();
    service = await server.getPrimaryService(serviceUuid);
    characteristic = await service.getCharacteristic(characteristicUuid);

    // Enable notifications for the characteristic
    await characteristic.startNotifications();
    characteristic.addEventListener('characteristicvaluechanged', handleCharacteristicValueChanged);

    startGatewayNameCheck();

  } catch (error) {
    log("Failed to connect");
    throw error;
  }
}


async function processMessageQueue() {
  if (sendingMessage || messageQueue.length === 0) {
    return;
  }
  sendingMessage = true;

  const dataToSend = messageQueue.shift();
  try {
    const sendDataBuffer = new TextEncoder().encode(dataToSend);
    await characteristic.writeValue(sendDataBuffer);
    log("Message sent");
  } catch (error) {
    log("Failed to send message");
    throw error;
  } finally {
    sendingMessage = false;
  }

  if (messageQueue.length > 0) {
    await processMessageQueue();
  }
}

function startGatewayNameCheck() {
  if (gatewayNameCheckInterval === undefined) {
    getGatewayName();
    gatewayNameCheckCount = 1
    gatewayNameCheckInterval = setInterval(() => {
      if (device && device.gatt.connected && gatewayNameCheckCount < 5) {
        getGatewayName();
        gatewayNameCheckCount++;
        updateInternetConnectionStatus();
      } else {
        stopGatewayNameCheck();
      }
    }, 20000);
    updateInternetConnectionStatus();
  }
}

function stopGatewayNameCheck() {
  if (gatewayNameCheckInterval !== undefined) {
    clearInterval(gatewayNameCheckInterval);
    gatewayNameCheckInterval = undefined;
    gatewayNameCheckCount = 0;
    updateInternetConnectionStatus();
  }
}

function handleCharacteristicValueChanged(event) {
  const value = event.target.value;
  const decoder = new TextDecoder("utf-8");
  const receivedText = decoder.decode(value);

  log(`Received data (decoded): ${receivedText}`);

  const parts = receivedText.split("\r\n\r\n");
  const header = parts[0];
  const content = parts[1];

  // get the Location header key value
  const locationHeader = header.split("\r\n").find((line) => line.startsWith("Location:")); // Location: /api/name

  if (locationHeader != null) {
    const locationValue = locationHeader.split(": ")[1]; // /api/name

    if (locationValue === "/api/name") {
      const receivedJson = JSON.parse(content);

      // if the message is a gateway name, update the gateway name
      if (receivedJson.name) {
        gatewayName = receivedJson.name;
        log(`Gateway name: ${gatewayName}`);
        stopGatewayNameCheck();
        updateInternetConnectionStatus();
      }
    } else if (locationValue === "/api/wifi") {
      const receivedJson = JSON.parse(content);

      if (receivedJson.status) {
        log(`Wifi status recieved: ${receivedJson.status}`);
        if (receivedJson.status === "ok") {
          setTimeout(() => startGatewayNameCheck(), 10000);
        }
      }
    }
  }
}

function updateInternetConnectionStatus() {
  if (gatewayName) {
    internetConnectionStatus.textContent = "Connected";
    internetConnectionStatus.classList.remove("text-warning");
    internetConnectionStatus.classList.remove("text-danger");
    internetConnectionStatus.classList.add("text-success");
  } else if (gatewayNameCheckInterval != undefined) {
    dots = ".".repeat(gatewayNameCheckCount);
    internetConnectionStatus.textContent = "Checking" + dots;
    internetConnectionStatus.classList.remove("text-success");
    internetConnectionStatus.classList.remove("text-danger");
    internetConnectionStatus.classList.add("text-warning");
  } else {
    internetConnectionStatus.textContent = "Not connected";
    internetConnectionStatus.classList.remove("text-success");
    internetConnectionStatus.classList.remove("text-warning");
    internetConnectionStatus.classList.add("text-danger");
  }
}


async function sendMessage(endpoint, method, content) {
  log(`Attempting to send message to ${endpoint}`);
  if (!characteristic) {
    return;
  }

  // Construct the custom message format
  const messageType = "EGWTTP/1.1";
  const contentType = "text/json";
  const contentLength = new TextEncoder().encode(content).byteLength;

  const sendMessageData = `${method} ${endpoint} ${messageType}\r\nContent-Type: ${contentType}\r\nContent-Length: ${contentLength}\r\n\r\n${content}`;

  // Add the message data to the queue
  messageQueue.push(sendMessageData);

  // Process the queue
  await processMessageQueue();
}

function getGatewayName() {
  if (gatewayName == null) {
    const endpoint = "/api/name";
    const content = "";
    sendMessage(endpoint, "GET", content).catch((error) => {
      log(error);
    });
  }
}


function disconnect() {
  if (!device || !device.gatt.connected) {
    return;
  }

  if (characteristic) {
    characteristic.removeEventListener('characteristicvaluechanged', handleCharacteristicValueChanged);
    characteristic.stopNotifications();
  }

  device.gatt.disconnect();

  stopGatewayNameCheck();
}

wifiForm.addEventListener("submit", (event) => {
  event.preventDefault();

  stopGatewayNameCheck();
  gatewayName = null;
  updateInternetConnectionStatus()

  const ssid = document.getElementById("ssid").value;
  const psk = document.getElementById("password").value;

  const endpoint = "/api/wifi";
  const content = JSON.stringify({
    ssid: ssid,
    psk: psk
  });

  sendMessage(endpoint, "POST", content).catch((error) => {
    log(error);
  });
});

walletForm.addEventListener("submit", (event) => {
  event.preventDefault();
  const publicKey = document.getElementById("wallet-public-key").value;

  const endpoint = "/api/initialize";
  const content = JSON.stringify({
    wallet: publicKey
  });

  sendMessage(endpoint, "POST", content).catch((error) => {
    log(error);
  });
});


inverterForm.addEventListener("submit", (event) => {
  event.preventDefault();

  const ipAddress = document.getElementById("ip-address").value;
  const port = document.getElementById("port").value;
  const typeSelected = document.getElementById("inverter-type").value;
  const address = document.getElementById("inverter-address").value;

  const endpoint = "/api/inverter";
  const content = JSON.stringify({
    ip: ipAddress,
    port: port,
    type: typeSelected,
    address: address
  });

  sendMessage(endpoint, "POST", content).catch((error) => {
    log(error);
  });
});


