import json

class Settings:

    class Harvest:

        def __init__(self):
            self._endpoints = []

        def add_endpoint(self, endpoint: str):
            self._endpoints.append(endpoint)

        def remove_endpoint(self, endpoint: str):
            self._endpoints.remove(endpoint)

        def clear_endpoints(self):
            self._endpoints.clear()

        @property
        def endpoints(self):
            # return a copy of the list
            return self._endpoints.copy()


    def __init__(self):
        self._harvest = self.Harvest()

    @property
    def harvest(self) -> Harvest:
        return self._harvest

    def to_json(self):
        dict = {'settings': {'harvest': {'endpoints': self.harvest._endpoints}}}
        return json.dumps(dict, indent=4)

    def from_json(self, json_str: str):
        dict = json.loads(json_str)
        self.harvest.clear_endpoints()
        for endpoint in dict['settings']['harvest']['endpoints']:
            self.harvest.add_endpoint(endpoint)

