import json
from ..handler import GetHandler
from ..requestData import RequestData
from ....inverters.supported_inverters.profiles import InverterProfiles

class Handler(GetHandler):
    def schema(self):
        return self.create_schema("returns the supported inverters", 
                                  returns={"inverters": "list of names of supported inverters"})

    def do_get(self, data: RequestData):
        supported_inverters = InverterProfiles().get_supported_inverters()
        ret = {"inverters": supported_inverters}

        return 200, json.dumps(ret)