import requests
import settings
import json


def test_pause_command():
    url = settings.api_url + "inverter/modbus"
    payload = {"commands": [{"type": "pause", "duration": 1000}]}
    payload = json.dumps(payload)
    headers = {
        'user-agent': "vscode-restclient",
        'content-type': "application/json"
        }

    response = requests.request("POST", url, data=payload, headers=headers)

    assert response.status_code == 200
    assert response.headers['content-type'] == 'application/json'
    assert response.json()['status'] == 'ok'

def test_write_command():
    url = settings.api_url + "inverter/modbus"
    payload = {"commands": [{"type": "write", "startingAddress": 40069, "values": [0x00, 0x00]}]}
    payload = json.dumps(payload)
    headers = {
        'user-agent': "vscode-restclient",
        'content-type': "application/json"
        }

    response = requests.request("POST", url, data=payload, headers=headers)

    assert response.status_code == 200
    assert response.headers['content-type'] == 'application/json'
    assert response.json()['status'] == 'ok'

def test_write_pause_write_command():
    url = settings.api_url + "inverter/modbus"
    payload = {"commands": [{"type": "write", "startingAddress": 40069, "values": [0x00, 0x00]},
                            {"type": "pause", "duration": 1000},
                            {"type": "write", "startingAddress": 40069, "values": [0x00, 0x00]}]}
    payload = json.dumps(payload)
    headers = {
        'user-agent': "vscode-restclient",
        'content-type': "application/json"
        }

    response = requests.request("POST", url, data=payload, headers=headers)

    assert response.status_code == 200
    assert response.headers['content-type'] == 'application/json'
    assert response.json()['status'] == 'ok'