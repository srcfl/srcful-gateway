import requests
import settings
import threading
import time
import logging

log = logging.getLogger(__name__)


def make_request(url, headers):
    response = requests.request("GET", url, headers=headers, timeout=20)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    assert response.json()["message"] == "hello world from srcful!"

def test_hello_threaded():
    url = settings.api_url + "hello"
    headers = {"user-agent": "vscode-restclient"}

    log.info("100 hello requests in parallel: ")

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
    log.info()
    log.info("elapsedTime: %s", str(elapsed_time))


def test_hello():
    url = settings.api_url + "hello"

    headers = {"user-agent": "vscode-restclient"}

    start_time = time.time()

    log.info("100 hello requests in sequence: ")
    for _i in range(100):
        response = requests.request("GET", url, headers=headers)

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        assert response.json()["message"] == "hello world from srcful!"

    elapsed_time = time.time() - start_time

    log.info()
    log.info("elapsedTime: %s", str(elapsed_time))


test_hello_threaded()
