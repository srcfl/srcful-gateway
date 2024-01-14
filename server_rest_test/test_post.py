import requests
import settings
import json

def test_echo():
    url = settings.api_url + "echo"

    payload = json.dumps("hello world")
    headers = {
    'Content-Type': 'application/json',
    'user-agent': 'vscode-restclient'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    assert response.status_code == 200
    assert response.headers['content-type'] == 'application/json'

    j = response.json()
    assert 'echo' in j
    assert j['echo'] == 'hello world'

def test_wifi():
    if settings.wifi_do_test:
        url = settings.api_url + "wifi"

        headers = {'user-agent': 'vscode-restclient'}

        payload = json.dumps({"ssid": settings.wifi_ssid, "psk": settings.wifi_psk})

        response = requests.request("POST", url, headers=headers, data=payload)

        assert response.status_code == 200
        assert response.headers['content-type'] == 'application/json'
        j = response.json()
        assert 'status' in j
        assert j['status'] == 'ok'

        # now we check the network settings and see if we can find a wireless connections
        url = settings.api_url + "network"
        headers = {'user-agent': 'vscode-restclient'}
        response = requests.request("GET", url, headers=headers)

        assert response.status_code == 200
        assert response.headers['content-type'] == 'application/json'
        j = response.json()
        
        found = False
        for connection in j['connections']:
            if '802-11-wireless' in connection:
                found = True
                break
        assert found == settings.wifi_real_settings

def test_wifi_scan():
    url = settings.api_url + "wifi/scan"

    headers = {'user-agent': 'vscode-restclient'}

    response = requests.request("GET", url, headers=headers)

    assert response.status_code == 200
    assert response.headers['content-type'] == 'application/json'

    j = response.json()
    assert 'status' in j
    assert j['status'] == 'scan initiated'
            
                


