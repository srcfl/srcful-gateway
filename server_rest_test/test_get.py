import requests
import settings

# these tests are meant to be run against the local server
# you would also need an inverter (or the simulator) running


def test_hello():
    url = settings.API_URL + "hello"

    headers = {"user-agent": "vscode-restclient"}

    response = requests.request("GET", url, headers=headers, timeout=settings.REQUEST_TIMEOUT)

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    assert response.json()["message"] == "hello world from srcful!"


def test_version():
    url = settings.API_URL + "version"

    headers = {"user-agent": "vscode-restclient"}

    response = requests.request("GET", url, headers=headers, timeout=settings.REQUEST_TIMEOUT)

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"

    # assert we get a reply containting 2 dots
    assert response.json()["version"].count(".") == 2


def test_uptime():
    url = settings.API_URL + "uptime"

    headers = {"user-agent": "vscode-restclient"}

    response = requests.request("GET", url, headers=headers, timeout=settings.REQUEST_TIMEOUT)

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    assert response.json()["msek"] > 0


def test_name():
    url = settings.API_URL + "name"

    headers = {"user-agent": "vscode-restclient"}

    response = requests.request("GET", url, headers=headers, timeout=settings.REQUEST_TIMEOUT)

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    assert len(response.json()["name"].split(" ")) == 3


def test_crypto():
    url = settings.API_URL + "crypto"

    headers = {"user-agent": "vscode-restclient"}

    response = requests.request("GET", url, headers=headers, timeout=settings.REQUEST_TIMEOUT)

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"

    j = response.json()
    assert "deviceName" in j
    assert "serialNumber" in j
    assert "publicKey" in j
    assert "publicKey_pem" in j


def test_wifi():
    url = settings.API_URL + "wifi"

    headers = {"user-agent": "vscode-restclient"}

    response = requests.request("GET", url, headers=headers, timeout=settings.REQUEST_TIMEOUT)

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"

    j = response.json()
    assert "ssids" in j
    assert len(j["ssids"]) > 0


def test_wifi_scan():
    url = settings.API_URL + "wifi/scan"

    headers = {"user-agent": "vscode-restclient"}

    response = requests.request("GET", url, headers=headers, timeout=settings.REQUEST_TIMEOUT)

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"

    j = response.json()
    assert "status" in j
    assert j["status"] == "scan initiated"


def test_running_inverter():
    # requires an inverter to be running
    url = settings.API_URL + "inverter"

    headers = {"user-agent": "vscode-restclient"}

    response = requests.request("GET", url, headers=headers, timeout=settings.REQUEST_TIMEOUT)

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"

    j = response.json()
    assert "connection" in j
    assert j["connection"] == "TCP" or j["connection"] == "RTU"
    assert "type" in j
    assert "address" in j  # this could be dependant on TCP connection
    assert "port" in j
    assert "status" in j


def test_network():
    url = settings.API_URL + "network"

    headers = {"user-agent": "vscode-restclient"}

    response = requests.request("GET", url, headers=headers, timeout=settings.REQUEST_TIMEOUT)

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"

    j = response.json()
    assert "connections" in j
    assert len(j["connections"]) > 0


def test_local_address():
    url = settings.API_URL + "network/address"

    headers = {"user-agent": "vscode-restclient"}

    response = requests.request("GET", url, headers=headers, timeout=settings.REQUEST_TIMEOUT)

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"

    j = response.json()
    assert "ip" in j
    assert "port" in j
    assert j["ip"].count(".") == 3
    for part in j["ip"].split("."):
        assert 0 <= int(part) <= 255

    assert str(j["port"]) in settings.API_URL or j["port"] == 80
    assert not settings.IP_DO_TEST_AGAINST_API_URL or (j["ip"] in settings.API_URL) # this could be flaky


def test_modbus_raw():
    url = settings.API_URL + "inverter/modbus/holding/40000?size=2"

    headers = {"user-agent": "vscode-restclient"}

    response = requests.request("GET", url, headers=headers, timeout=settings.REQUEST_TIMEOUT)

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"

    j = response.json()
    assert "register" in j
    assert "raw_value" in j
    assert "size" in j
    assert j["size"] == 2
    assert j["register"] == 40000
    assert j["raw_value"] == "00000000"


def test_logger():
    url = settings.API_URL + "logger"

    headers = {"user-agent": "vscode-restclient"}

    response = requests.request("GET", url, headers=headers, timeout=settings.REQUEST_TIMEOUT)

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    assert "server.tasks.openInverterTask" in response.json()


def test_supported():
    url = settings.API_URL + "inverter/supported"

    headers = {"user-agent": "vscode-restclient"}

    response = requests.request("GET", url, headers=headers, timeout=settings.REQUEST_TIMEOUT)

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    
    assert ['SOLAREDGE', 'SolarEdge'] in response.json()['inverters']
    assert ['SUNGROW', 'Sungrow'] in response.json()['inverters']
    assert ['GROWATT', 'Growatt'] in response.json()['inverters']
    assert ['HUAWEI', 'Huawei'] in response.json()['inverters']
    assert ['GOODWE', 'Goodwe'] in response.json()['inverters']
