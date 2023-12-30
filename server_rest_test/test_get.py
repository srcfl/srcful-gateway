import requests
import settings

# these tests are meant to be run against the local server
# you would also need an inverter (or the simulator) running




def test_get_hello():

    url = settings.api_url + "hello"

    headers = {'user-agent': 'vscode-restclient'}

    response = requests.request("GET", url, headers=headers)

    print(response.text)

    assert response.status_code == 200
    assert response.headers['content-type'] == 'application/json'
    assert response.json()['message'] == 'hello world from srcful!'