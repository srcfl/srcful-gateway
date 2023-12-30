import requests
import settings

def deleteInverter():
    return "Inverter deleted"

def getInverter():
    url = settings.api_url + "inverter"
    headers = {'user-agent': 'vscode-restclient'}

    response = requests.request("GET", url, headers=headers)

    return response

def postInverter(inverterSettings):
    url = settings.api_url + "invertertcp"
    headers = {'user-agent': 'vscode-restclient'}

    # remao host to ip
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

    currentInverter = getInverter()

    assert currentInverter.json()['status'] == 'open'

    # restore previous inverter
    postInverter(previousInverter.json())