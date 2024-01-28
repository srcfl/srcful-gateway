import requests
import settings
import threading
import time


def make_request(url, headers):
    response = requests.request("GET", url, headers=headers, timeout=20)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    assert response.json()["message"] == "hello world from srcful!"
    print(".", end="", flush=True)


def test_hello_threaded():
    url = settings.api_url + "hello"
    headers = {"user-agent": "vscode-restclient"}

    print("100 hello requests in parallel: ", end="")

    # create 100 threads
    threads = [
        threading.Thread(
            target=make_request, args=(url, headers)
        )
        for i in range(100)
    ]

    start_time = time.time()
    for i in range(len(threads)):
        threads[i].start()

    # wait for all threads to finish
    for i in range(len(threads)):
        threads[i].join()

    elapsed_time = time.time() - start_time
    print()
    print("elapsedTime: " + str(elapsed_time))


def test_hello():
    url = settings.api_url + "hello"

    headers = {"user-agent": "vscode-restclient"}

    start_time = time.time()

    print("100 hello requests in sequence: ", end="")
    for _i in range(100):
        response = requests.request("GET", url, headers=headers)

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        assert response.json()["message"] == "hello world from srcful!"
        print(".", end="", flush=True)

    elapsed_time = time.time() - start_time

    print()
    print("elapsedTime: " + str(elapsed_time))


test_hello_threaded()
