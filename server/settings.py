import json

class Settings:
            
    @property
    def SETTINGS(self):
        return "settings"
    
    

    class Harvest:

        @property
        def HARVEST(self):
            return "harvest"
        
        @property
        def ENDPOINTS(self):
            return "endpoints"

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
            return self._endpoints.copy()

    def __init__(self):
        self._harvest = self.Harvest()

    @property
    def harvest(self) -> Harvest:
        return self._harvest

    def to_json(self):
        dict = {
            self.SETTINGS: {
                self.harvest.HARVEST: {
                    self.harvest.ENDPOINTS: self.harvest._endpoints
                }
            }
        }
        return json.dumps(dict, indent=4)

    def from_json(self, json_str: str):
        dict = json.loads(json_str)
        self.harvest.clear_endpoints()
        for endpoint in dict[self.SETTINGS][self.harvest.HARVEST][self.harvest.ENDPOINTS]:
            self.harvest.add_endpoint(endpoint)