import requests
import settings
import json

def test_echo():
    url = settings.API_URL + "echo"

    payload = json.dumps("hello world")
    headers = {
        'Content-Type': 'application/json',
        'user-agent': 'vscode-restclient'
    }

    response = requests.request("POST", url, headers=headers, data=payload, timeout=settings.REQUEST_TIMEOUT)

    assert response.status_code == 200
    assert response.headers['content-type'] == 'application/json'

    j = response.json()
    assert 'echo' in j
    assert j['echo'] == 'hello world'

def test_wifi():
    if settings.WIFI_DO_TEST:
        url = settings.API_URL + "wifi"

        headers = {'user-agent': 'vscode-restclient'}

        payload = json.dumps({"ssid": settings.WIFI_SSID, "psk": settings.WIFI_PSK})

        response = requests.request("POST", url, headers=headers, data=payload, timeout=settings.REQUEST_TIMEOUT)

        assert response.status_code == 200
        assert response.headers['content-type'] == 'application/json'
        j = response.json()
        assert 'status' in j
        assert j['status'] == 'ok'

        # now we check the network settings and see if we can find a wireless connections
        url = settings.API_URL + "network"
        headers = {'user-agent': 'vscode-restclient'}
        response = requests.request("GET", url, headers=headers, timeout=settings.REQUEST_TIMEOUT)

        assert response.status_code == 200
        assert response.headers['content-type'] == 'application/json'
        j = response.json()
        
        found = False
        for connection in j['connections']:
            if '802-11-wireless' in connection:
                found = True
                break
        assert found == settings.WIFI_REAL_SETTINGS

def test_wifi_scan():
    url = settings.API_URL + "wifi/scan"

    headers = {'user-agent': 'vscode-restclient'}

    response = requests.request("GET", url, headers=headers, timeout=settings.REQUEST_TIMEOUT)

    assert response.status_code == 200
    assert response.headers['content-type'] == 'application/json'

    j = response.json()
    assert 'status' in j
    assert j['status'] == 'scan initiated'

def test_initialize():
    url = settings.API_URL + "initialize"

    payload = json.dumps({"wallet": 'abc123', 'dry_run': 'true'})
    headers = {
        'Content-Type': 'application/json',
        'user-agent': 'vscode-restclient'
    }

    response = requests.request("POST", url, headers=headers, data=payload, timeout=settings.REQUEST_TIMEOUT)

    assert response.status_code == 200
    assert response.headers['content-type'] == 'application/json'

    j = response.json()
    assert response.status_code == 200
    assert 'initialized' in j
    assert j['initialized'] is False
