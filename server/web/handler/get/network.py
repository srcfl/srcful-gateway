import json
from ..handler import GetHandler

from ..requestData import RequestData
from server.wifi.wifi import getConnectionConfigs

class Handler(GetHandler):

  def schema(self):
      return { 'type': 'get',
                      'description': 'Returns the list of networks',
                      'returns': {'connections': 'list of dicts, containing the configured networks.'}
                    }

  def doGet(self, request_data: RequestData):
    return 200, json.dumps({"connections": getConnectionConfigs()})