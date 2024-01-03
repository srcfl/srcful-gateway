import requests
import settings

# these tests are meant to be run against the local server
# you would also need an inverter (or the simulator) running


def test_hello():

    url = settings.api_url + "hello"

    headers = {'user-agent': 'vscode-restclient'}

    response = requests.request("GET", url, headers=headers)

    assert response.status_code == 200
    assert response.headers['content-type'] == 'application/json'
    assert response.json()['message'] == 'hello world from srcful!'

def test_uptime():
    
        url = settings.api_url + "uptime"
    
        headers = {'user-agent': 'vscode-restclient'}
    
        response = requests.request("GET", url, headers=headers)
    
        assert response.status_code == 200
        assert response.headers['content-type'] == 'application/json'
        assert response.json()['msek'] > 0


def test_name():

    url = settings.api_url + "name"

    headers = {'user-agent': 'vscode-restclient'}

    response = requests.request("GET", url, headers=headers)

    assert response.status_code == 200
    assert response.headers['content-type'] == 'application/json'
    assert len(response.json()['name'].split(" ")) == 3

def test_crypto():

    url = settings.api_url + "crypto"

    headers = {'user-agent': 'vscode-restclient'}

    response = requests.request("GET", url, headers=headers)

    assert response.status_code == 200
    assert response.headers['content-type'] == 'application/json'

    j = response.json()
    assert 'deviceName' in j
    assert 'serialNumber' in j
    assert 'publicKey' in j
    assert 'publicKey_pem' in j

def test_running_inverter():
    # requires an inverter to be running
    url = settings.api_url + "inverter"

    headers = {'user-agent': 'vscode-restclient'}

    response = requests.request("GET", url, headers=headers)

    assert response.status_code == 200
    assert response.headers['content-type'] == 'application/json'

    j = response.json()
    assert 'connection' in j
    assert j['connection'] == 'TCP' or j['connection'] == 'RTU'
    assert 'type' in j
    assert 'address' in j   # this could be dependant on TCP connection
    assert 'port' in j
    assert 'status' in j

def test_network():
    url = settings.api_url + "network"

    headers = {'user-agent': 'vscode-restclient'}

    response = requests.request("GET", url, headers=headers)

    assert response.status_code == 200
    assert response.headers['content-type'] == 'application/json'

    j = response.json()
    assert 'connections' in j
    assert len(j['connections']) > 0

def test_modbus_raw():
    url = settings.api_url + "inverter/modbus/holding/40000?size=2"

    headers = {'user-agent': 'vscode-restclient'}

    response = requests.request("GET", url, headers=headers)

    assert response.status_code == 200
    assert response.headers['content-type'] == 'application/json'

    j = response.json()
    assert 'register' in j
    assert 'raw_value' in j
    assert 'size' in j
    assert j['size'] == 2
    assert j['register'] == 40000
    assert j['raw_value'] == '00000000'

