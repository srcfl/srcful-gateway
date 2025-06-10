import json
import logging
from ..handler import GetHandler
from ..requestData import RequestData

log = logging.getLogger(__name__)


class Handler(GetHandler):

    def schema(self) -> dict:
        return self.create_schema(
            "Get the local data for all distributed energy entities connected to the gateway",
            returns={
                'dee': "object with all the datas",
            }
        )
    
    def do_get(self, data: RequestData):

        dees = []

        for device in data.bb.devices.lst:
            last_harvest_data = device.get_last_harvest_data()
            dee_decoder = device.get_dee_decoder()
            if dee_decoder:
                dees = dees + dee_decoder.decode(last_harvest_data)

        return 200, json.dumps({"status":"success", "data":{"dee":dees}})



