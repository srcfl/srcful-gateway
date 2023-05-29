const connectButton = document.getElementById("connect-button");
const sendMessageButton = document.getElementById("send-message");
const inverterForm = document.getElementById("inverter-form");
const wifiForm = document.getElementById("wifi-form");

let device;
let server;
let service;
let characteristic;

const output = document.getElementById("output");

const serviceUuid = 'a07498ca-ad5b-474e-940d-16f1fbe7e8cd';
const characteristicUuid = '51ff12bb-3ed8-46e5-b4f9-d64e2fec021b';

function log(message) {
  console.log(message);
  output.innerHTML += message + '<br>';
}

connectButton.addEventListener("click", () => {
  if (!device || !device.gatt.connected) {
    connect()
      .then(() => {
        log("Connected");
        sendMessageButton.disabled = false;
        connectButton.textContent = "Disconnect";
        inverterForm.style.display = "block";
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

  } catch (error) {
    log("Failed to connect");
    throw error;
  }
}

function handleCharacteristicValueChanged(event) {
  const value = event.target.value;
  const decoder = new TextDecoder("utf-8");
  const receivedText = decoder.decode(value);

  log(`Received data (decoded): ${receivedText}`);
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
  const sendDataBuffer = new TextEncoder().encode(sendMessageData);

  try {
    await characteristic.writeValue(sendDataBuffer);
    log("Message sent");
  } catch (error) {
    log("Failed to send message");
    throw error;
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
}

wifiForm.addEventListener("submit", (event) => {
  event.preventDefault();

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


inverterForm.addEventListener("submit", (event) => {
  event.preventDefault();

  const ipAddress = document.getElementById("ip-address").value;
  const port = document.getElementById("port").value;
  const typeSelected = document.getElementById("inverter-type").value;
  const address = document.getElementById("inverter-address").value;

  const endpoint = "/api/inverter";
  const content = JSON.stringify({
    ssid: ssid,
    psk: psk,
    ip: ipAddress,
    port: port,
    type: typeSelected,
    address: address
  });

  sendMessage(endpoint, "POST", content).catch((error) => {
    log(error);
  });
});


