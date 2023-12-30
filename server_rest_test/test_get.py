import requests

# these tests are meant to be run against the local server


api_url = "http://localhost:5000/api/"

def test_get_hello():

    url = api_url + "hello"

    headers = {'user-agent': 'vscode-restclient'}

    response = requests.request("GET", url, headers=headers)

    print(response.text)

    assert response.status_code == 200
    assert response.headers['content-type'] == 'application/json'
    assert response.json()['message'] == 'hello world from srcful!'