import json
import logging

from server.network.scan import WifiScanner

from ..handler import GetHandler
from ..requestData import RequestData


logger = logging.getLogger(__name__)


class Handler(GetHandler):
    def schema(self):
        return {
            "type": "get",
            "description": "Get the list of wifi SSIDs since the last scan. Scanning can be initiated with the GET /wifi/scan endpoint.",
            "returns": {"ssids": "list of SSID strings ['ssid1', 'ssid2', ...]"},
        }

    def do_get(self, data: RequestData):
        try:
            s = WifiScanner()
            ssids = s.get_ssids()
            return 200, json.dumps({"ssids": ssids})
        except Exception as e:
            logger.error(e)
            return 400, json.dumps({"error": str(e)})


class ScanHandler(GetHandler):
    def schema(self):
        return {
            "type": "get",
            "description": "Initiates a new scan of available wifi networks. Returns immediately and the scan results will be available after 5 to 10 seconds. The scan results can be retrieved with the GET /wifi endpoint.",
            "returns": {"status": "scan initiated"},
        }

    def do_get(self, data: RequestData):
        try:
            s = WifiScanner()
            s.scan()
            return 200, json.dumps({"status": "scan initiated"})
        except Exception as e:
            logger.error(e)
            return 400, json.dumps({"error": str(e)})
