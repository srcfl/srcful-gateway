import json
from ..handler import GetHandler

from ..requestData import RequestData
from server.wifi.wifi import getConnectionConfigs

class Handler(GetHandler):
  def doGet(self, request_data: RequestData):
    return 200, json.dumps({"connections": getConnectionConfigs()})