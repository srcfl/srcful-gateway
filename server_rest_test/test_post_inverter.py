import requests
import settings
import time

def deleteInverter():
    return "Inverter deleted"

def getInverter():
    url = settings.api_url + "inverter"
    headers = {'user-agent': 'vscode-restclient'}

    response = requests.request("GET", url, headers=headers)

    return response

def postInverter(inverterSettings):

    if 'status' in inverterSettings and inverterSettings['status'] == 'no inverter':
        return  

    url = settings.api_url + "invertertcp"
    headers = {'user-agent': 'vscode-restclient'}

    # remap host to ip
    if 'host' in inverterSettings:
        inverterSettings['ip'] = inverterSettings['host']

    response = requests.request("POST", url, headers=headers, json=inverterSettings)

    return response

def test_postInverter():
    previousInverter = getInverter()

    deleteInverter()

    inverter_settings = {
        "host": settings.inverter_host,
        "type": settings.inverter_type,
        "address": settings.inverter_address,
        "port": settings.inverter_port
    }

    response = postInverter(inverter_settings)

    assert response.status_code == 200

    # wait for inverter to connect
    time.sleep(3)

    currentInverter = getInverter()

    assert currentInverter.json()['status'] == 'open'

    # restore previous inverter
    postInverter(previousInverter.json())