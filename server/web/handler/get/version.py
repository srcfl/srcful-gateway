import json
from ..handler import GetHandler
from ..requestData import RequestData


class Handler(GetHandler):
    def schema(self):
        return self.create_schema("returns the version of the firmware.", 
                                  returns={"version": "string in the format major.minor.patch"})

    def do_get(self, data: RequestData):
        ret = {"version": data.bb.get_version()}

        return 200, json.dumps(ret)
