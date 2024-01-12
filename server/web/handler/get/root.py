from typing import Callable


def cryptoStuff():
  return """<h1>Crypto API</h1>
  <p>Device Name: <span id="device-name"></span></p>
  <p>Serial Number: <span id="serial-number"></span></p>
  <p>Public Key: <span id="public-key"></span></p>
  <p>Public Key PEM:</p>
  <textarea id="public-key-pem" rows="10" cols="50"></textarea>
  
  <script>
    async function fetchCryptoData() {
      const response = await fetch('/api/crypto');
      const data = await response.json();
      document.getElementById('device-name').textContent = data.deviceName;
      document.getElementById('serial-number').textContent = data.serialNumber;
      document.getElementById('public-key').textContent = data.publicKey;
      document.getElementById('public-key-pem').textContent = formatPEM(data.publicKey_pem);
    }

    function formatPEM(pem) {
      let result = "-----BEGIN PUBLIC KEY-----";
      for (let i = 0; i < pem.length; i += 64) {
        result += pem.slice(i, i + 64) + \"\\n\";
      }
      result += "-----End PUBLIC KEY-----";
      return result;
    }

    fetchCryptoData();
  </script>"""


def inverterForm():
  return """
  <h1>Inverter Form</h1>

<form id="inverter-form">
  <label>
    <input type="radio" name="preferred_protocol" value="tcp" onclick="methodSelected('tcp')" checked="checked" /> TCP/IP
  </label>

  <br />
  <label>
    <input type="radio" name="preferred_protocol" value="rtu" onclick="methodSelected('rtu')" /> RTU
  </label>

  <br /><br />
  <div id="tcp-div">
    <label id="ip-label" for="ip">Inverter IP:</label>
    <input type="text" id="ip" name="ip" value="192.168.50.162"><br><br>

    <label id="port-label" for="port">Inverter Port:</label>
    <input type="text" id="port" name="port" value="502"><br><br>
  </div>

  <div id="rtu-div" style="display:none;">
    <label id="serial-label" for="serial">Serial Port:</label>
    <input type="text" id="serial" name="serial" value="/dev/serial0"><br><br>

    <label id="baudrate-label" for="baudrate">Baudrate:</label>
    <input type="text" id="baudrate" name="baudrate" value="9600"><br><br>

    <label id="bytesize-label" for="bytesize">Byte Size:</label>
    <input type="text" id="bytesize" name="bytesize" value="8"><br><br>

    <label id="stopbits-label" for="stopbits">Stop Bits:</label>
    <input type="text" id="stopbits" name="stopbits" value="1"><br><br>

    <label id="parity-label" for="parity">Parity:</label>
    <input type="text" id="parity" name="parity" value="N"><br><br>
  </div>

  <label for="type">Inverter Type:</label>
  <input type="text" id="type" name="type" value="lqt40s"><br><br>

  <label for="address">Inverter Address:</label>
  <input type="text" id="address" name="address" value="1"><br><br>

  <button type="submit">Submit</button>
</form>

<script>
  const form = document.querySelector('#inverter-form');
  const tcpDiv = document.querySelector('#tcp-div');
  const rtuDiv = document.querySelector('#rtu-div');

  const methodSelected = (method) => {
    if (method === 'rtu') {
      tcpDiv.style.display = "none";
      rtuDiv.style.display = "block";
    } else {
      rtuDiv.style.display = "none";
      tcpDiv.style.display = "block";
    }
  }

  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    const selectedRadio = document.querySelector('input[name="preferred_protocol"]:checked').value;
    console.log(selectedRadio)

    const formData = new FormData(form);
    let data = {}
    let endPoint = '/api/inverter'
    if (selectedRadio === 'tcp') {
      data = {
        ip: formData.get('ip'),
        port: formData.get('port'),
        type: formData.get('type'),
        address: formData.get('address')
      };
      endPoint += 'tcp';
    } else {
      data = {
        port: formData.get('serial'),
        baudrate: formData.get('baudrate'),
        bytesize: formData.get('bytesize'),
        stopbits: formData.get('stopbits'),
        parity: formData.get('parity'),
        type: formData.get('type'),
        address: formData.get('address')
      };
      endPoint += 'rtu';
    }

    const response = await fetch(endPoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    });
    console.log(endPoint);
    console.log(data);

    if (response.ok) {
      console.log('Inverter data submitted successfully!');
    } else {
      console.error('Failed to submit inverter data:', response.status);
    }
  });
</script>
  """

from ..handler import GetHandler

from ..requestData import RequestData

class Handler(GetHandler):
  def doGet(self, request_data: RequestData):
    #stats = request_data.stats
    #freqReads = stats['freqReads'] if 'freqReads' in stats else 0
    #energyHarvested = stats['harvest'] if 'harvest' in stats else 0
    #energyTransported = 0
    #if 'harvestTransports' in stats:
    #  energyTransported = stats['harvestTransports']
    startTime = request_data.bb.startTime

    ret = "<html><head><title>Srcful Energy Gateway</title></head>"
    ret += "<body>"
    ret += "<h1>Srcful Energy Gateway 0.0.6</h1>"
    #ret += f"<h2>{stats['name']}</h2>"

    ret += f"<p>chipInfo: {request_data.bb.getChipInfo()}</p>"

    elapsedTime = request_data.bb.time_ms() - startTime

    # convert elapsedTime to days, hours, minutes, seconds in a tuple
    days, remainder = divmod(elapsedTime // 1000, 60 * 60 * 24)
    hours, remainder = divmod(remainder, 60 * 60)
    minutes, seconds = divmod(remainder, 60)

    # output the gateway current uptime in days, hours, minutes, seconds
    ret += f"<p>Uptime (days, hours, minutes, seconds): {(days, hours, minutes, seconds)}</p>"

    ret += inverterForm()

    ret += cryptoStuff()

    #ret += f"<p>freqReads: {freqReads} in {elapsedTime} ms<br/>"
    #ret += f"average freqReads: {freqReads / elapsedTime * 1000} per second</p>"

    #ret += f"last freq: {stats['lastFreq'] if 'lastFreq' in stats else 0} Hz</p>"

    #ret += f"<p>energyHarvested: {energyHarvested} in {elapsedTime} ms</br>"
    #ret += f"average energyHarvested: {energyHarvested / elapsedTime * 1000} per second</p>"

    #ret += f"<p>energyTransported: {energyTransported} in {elapsedTime} ms</br>"
    #ret += f"average energyTransported: {energyTransported / elapsedTime * 1000} per second</p>"

    #ret += f"ALL: {stats}</p>"

    ret += "</body></html>"

    return 200, ret
