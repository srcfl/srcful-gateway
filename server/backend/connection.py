import requests

class Connection:

    def __init__(self, url: str, timeout: int):
        self.url = url
        self.timeout = timeout

    def post(self, query: str) -> dict:
        response = requests.post(self.url, json={"query": query}, timeout=self.timeout)
        response.raise_for_status()

        return response.json()
