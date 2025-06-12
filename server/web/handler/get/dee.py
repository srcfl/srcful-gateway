import json
import logging
from ..handler import GetHandler
from ..requestData import RequestData
from server.devices.DeeDecoder import SungrowDeeDecoder

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
        settings = {}

        for device in data.bb.devices.lst:
            last_harvest_data = device.get_last_harvest_data()
            dee_decoder: SungrowDeeDecoder = device.get_dee_decoder()

            settings = {
                "grid_power_limit": dee_decoder.grid_power_limit,
                "battery_power_limit": dee_decoder.battery_max_charge_discharge_power,
            }

            if dee_decoder:
                dees = dees + dee_decoder.decode(last_harvest_data)

        return 200, json.dumps({"status": "success", "settings": settings, "data": {"dee": dees}})
