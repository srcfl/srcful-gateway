import settings
import requests
import json


def get_log_level(logger):
    url = settings.api_url + "logger"

    payload = {"logger": logger}

    headers = {'user-agent': 'vscode-restclient'}

    response = requests.request("GET", url, headers=headers, params=payload)

    return response.json()[logger]

def set_log_level(logger, level):
    url = settings.api_url + "logger"

    payload = {"logger": logger,
               "level": level}

    payload = json.dumps(payload)
    headers = {
        'user-agent': "vscode-restclient",
        'content-type': "application/json"
        }

    response = requests.request("POST", url, data=payload, headers=headers)

    return response

def test_logger_set_info():
    logger = "server.inverters.inverter"

    originial_level = get_log_level(logger).split(' ')[0] # removes the (inherited) part

    response = set_log_level(logger, "INFO")

    assert response.status_code == 200
    assert response.headers['content-type'] == 'application/json'
    assert response.json()['level'] == True

    assert get_log_level(logger) == "INFO"
    
    # reset to original level
    assert set_log_level(logger, originial_level).status_code == 200

