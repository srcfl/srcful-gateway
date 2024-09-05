import requests
import settings
import json

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

    assert response.headers["content-type"] == "application/json"
    if settings.DO_TEST_CRYPTO:
        assert response.status_code == 200    
        assert len(response.json()["name"].split(" ")) == 3
    else:
        assert response.status_code == 500


def test_crypto():
    url = settings.API_URL + "crypto"

    headers = {"user-agent": "vscode-restclient"}

    response = requests.request("GET", url, headers=headers, timeout=settings.REQUEST_TIMEOUT)

    assert response.headers["content-type"] == "application/json"

    if settings.DO_TEST_CRYPTO:
        assert response.status_code == 200

        j = response.json()
        assert "deviceName" in j
        assert "serialNumber" in j
        assert "publicKey" in j
        assert "chipDeathCount" in j
    else:
        assert response.status_code == 500


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
    assert j["connection"] == "TCP" or j["connection"] == "RTU" or j["connection"] == "SUNSPEC"
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


# def test_modbus_raw():
#     url = settings.API_URL + "inverter/modbus/holding/40000?size=2"

#     headers = {"user-agent": "vscode-restclient"}

#     response = requests.request("GET", url, headers=headers, timeout=settings.REQUEST_TIMEOUT)

#     assert response.status_code == 200
#     assert response.headers["content-type"] == "application/json"

#     j = response.json()
#     assert "register" in j
#     assert "raw_value" in j
#     assert "size" in j
#     assert j["size"] == 2
#     assert j["register"] == 40000
#     assert len(j["raw_value"]) == len("00000000")


def test_logger():
    url = settings.API_URL + "logger"

    headers = {"user-agent": "vscode-restclient"}

    response = requests.request("GET", url, headers=headers, timeout=settings.REQUEST_TIMEOUT)

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    assert "server.tasks.openDeviceTask" in response.json()


def test_supported():
    url = settings.API_URL + "inverter/supported"

    headers = {"user-agent": "vscode-restclient"}

    response = requests.request("GET", url, headers=headers, timeout=settings.REQUEST_TIMEOUT)

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"

    solaredge = {'name': 'solaredge', 'dname': 'SolarEdge', 'proto': 'mb'}
    sungrow = {'name': 'sungrow', 'dname': 'Sungrow', 'proto': 'mb'}
    sungrow_hybrid = {'name': 'sungrow_hybrid', 'dname': 'Sungrow Hybrid', 'proto': 'mb'}
    fronius = {'name': 'fronius', 'dname': 'Fronius', 'proto': 'mb'}
    huawei = {'name': 'huawei', 'dname': 'Huawei', 'proto': 'mb'}
    goodwe = {'name': 'goodwe', 'dname': 'GoodWe', 'proto': 'mb'}
    growatt = {'name': 'growatt', 'dname': 'Growatt', 'proto': 'mb'}
    deye = {'name': 'deye', 'dname': 'Deye', 'proto': 'sol'}
    deye_hybrid = {'name': 'deye_hybrid', 'dname': 'Deye Hybrid', 'proto': 'sol'}
    sma = {'name': 'sma', 'dname': 'SMA', 'proto': 'mb'}
    lqt40s = {'name': 'lqt40s', 'dname': 'LQT40S', 'proto': 'mb'}

    inverters = [solaredge, sungrow, sungrow_hybrid, fronius, huawei, goodwe, growatt, deye, deye_hybrid, sma, lqt40s]

    for inverter in inverters:
        assert inverter in response.json()['inverters']


def get_notification_list():
    url = settings.API_URL + "notification"

    headers = {"user-agent": "vscode-restclient"}

    response = requests.request("GET", url, headers=headers, timeout=settings.REQUEST_TIMEOUT)

    return response

def test_notification_list():
    response = get_notification_list()

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    
    assert "ids" in response.json()

def test_get_settings():
    url = settings.API_URL + "settings"
    headers = {"user-agent": "vscode-restclient"}

    response = requests.get(url, headers=headers, timeout=settings.REQUEST_TIMEOUT)

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"

    # Check that the response is a valid JSON object
    try:
        json_response = response.json()
        assert isinstance(json_response, dict)
    except json.JSONDecodeError:
        assert False, "Response is not valid JSON"

def test_notification_message():

    response = get_notification_list()
    if len(response.json()["ids"]) > 0:
        id = response.json()["ids"][0]

        url = settings.API_URL + f"notification/{id}"

        headers = {"user-agent": "vscode-restclient"}

        response = requests.request("GET", url, headers=headers, timeout=settings.REQUEST_TIMEOUT)

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        
        assert "message" in response.json()
        assert "type" in response.json()
        assert "timestamp" in response.json()
        assert "id" in response.json()
        assert response.json()["id"] == id
        assert response.json()["type"] in ["error", "warning", "info"]