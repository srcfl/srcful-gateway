import requests
import settings

def get_notification_list():
    url = settings.API_URL + "notification"

    headers = {"user-agent": "vscode-restclient"}

    response = requests.request("GET", url, headers=headers, timeout=settings.REQUEST_TIMEOUT)

    return response

def test_notification_message():

    response = get_notification_list()
    if len(response.json()["ids"]) > 0:
        id = response.json()["ids"][0]

        url = settings.API_URL + f"notification/{id}"

        headers = {"user-agent": "vscode-restclient"}

        response = requests.request("DELETE", url, headers=headers, timeout=settings.REQUEST_TIMEOUT)

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        
        assert "id" in response.json()
        assert response.json()["id"] == str(id)

