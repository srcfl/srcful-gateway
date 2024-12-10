
import logging
import json
from ..handler import GetHandler
from ..requestData import RequestData
from server.devices.inverters.enphase_scanner import scan_for_enphase_device

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class MdnsScanHandler(GetHandler):
    def schema(self):
        return {
            "type": "get",
            "description": "Scans the network for devices using multicast dns",
            "returns": {"devices": "a list of JSON Objects: {'host': host ip, 'port': host port}."}
        }
        
        
    def do_get(self, data: RequestData):
        """Scan the network for devices using multicast dns."""
        devices = scan_for_enphase_device()
        return 200, json.dumps({"devices": devices})
