import requests
import settings
import time

def deleteInverter():
    return "Inverter deleted"

def getInverter():
    url = settings.API_URL + "inverter"
    headers = {'user-agent': 'vscode-restclient'}

    response = requests.request("GET", url, headers=headers)

    return response

def postInverter(inverterSettings):

    if 'status' in inverterSettings and inverterSettings['status'] == 'no inverter':
        return  

    url = settings.API_URL + "device"
    headers = {'user-agent': 'vscode-restclient'}

    # remap host to ip
    if 'host' in inverterSettings:
        inverterSettings['ip'] = inverterSettings['host']

    response = requests.request("POST", url, headers=headers, json=inverterSettings)

    return response

def test_postInverter():
    previousInverter = getInverter()

    deleteInverter()

    inverter_settings = {settings.INVERTER_CONNECTION: {
        "ip": settings.INVERTER_HOST,
        "device_type": settings.INVERTER_TYPE,
        "slave_id": settings.INVERTER_ADDRESS,
        "port": settings.INVERTER_PORT
    }}

    response = postInverter(inverter_settings)

    assert response.status_code == 200

    # wait for inverter to connect
    time.sleep(3)

    currentInverter = getInverter()

    assert currentInverter.json()['status'] == 'open'

    # restore previous inverter
    postInverter(previousInverter.json())