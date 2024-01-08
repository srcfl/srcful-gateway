import json
import logging
from ..handler import GetHandler
from ..requestData import RequestData
from server.wifi.scan import WifiScanner

logger = logging.getLogger(__name__)

class Handler(GetHandler):
  
  def schema(self):
        return {'type': 'get',
                'description': 'Get the list of wifi SSIDs since the last scan. Scanning can be initiated with the GET /wifi/scan endpoint.',
                'returns': {'ssids': "list of SSID strings ['ssid1', 'ssid2', ...]"}
                }

  def doGet(self, request_data: RequestData):
    try:
      s = WifiScanner()
      ssids = s.getSSIDs()
      return 200, json.dumps({"ssids": ssids}) 
    except Exception as e:
        logger.error(e)
        return 400, json.dumps({"error": str(e)})
   
  
class ScanHandler(GetHandler):
  def schema(self):
        return {'type': 'get',
                'description': 'Initiates a new scan of available wifi networks. Returns immediately and the scan results will be available after 5 to 10 seconds. The scan results can be retrieved with the GET /wifi endpoint.',
                'returns': {'status': "scan initiated"}
                }

  def doGet(self, request_data: RequestData):
    try:
      s = WifiScanner()
      s.scan()
      return 200, json.dumps({"status": "scan initiated"})
    except Exception as e:
        logger.error(e)
        return 400, json.dumps({"error": str(e)})
