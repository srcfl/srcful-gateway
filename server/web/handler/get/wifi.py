import json
import logging

from server.network.network_utils import NetworkUtils

from ..handler import GetHandler
from ..requestData import RequestData


logger = logging.getLogger(__name__)


class Handler(GetHandler):
    def schema(self):
        return {
            "type": "get",
            "description": "Get the list of wifi SSIDs since the last scan. Scanning can be initiated with the GET /wifi/scan endpoint.",
            "returns": {"ssids": "list of SSID strings ['ssid1', 'ssid2', ...]",
                        "connected": "name of connected ssid if any"},
        }

    def do_get(self, data: RequestData):
        try:
            network_state = data.bb.network_state()
            return 200, json.dumps(network_state['wifi'])
        except Exception as e:
            logger.error(e)
            return 400, json.dumps({"error": str(e)})


class ScanHandler(GetHandler):
    def schema(self):
        return {
            "type": "get",
            "description": "Scan for available wifi networks and return the list of SSIDs",
            "returns": {"ssids": "list of SSID strings ['ssid1', 'ssid2', ...]"},
        }

    def do_get(self, data: RequestData):
        try:
            res = NetworkUtils.get_wifi_ssids()
            if res:
                return 200, json.dumps({"ssids": res})
            else:
                return 500, json.dumps({"error": "Failed to initiate scan"})
        except Exception as e:
            logger.error(e)
            return 400, json.dumps({"error": str(e)})
