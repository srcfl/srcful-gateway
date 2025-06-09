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
        ret = data.bb.crypto_state().to_dict(data.bb.chip_death_count)

        meter = {
            "production": 195,
            "consumption": 100,
        }

        battery = {
            "power": 95,
        }

        solar = {
            "power": 100,
        }

        return 200, json.dumps({"status":"success", "data":{"dee":[{"meter":meter}, {"battery":battery}, {"solar":solar}]}})



