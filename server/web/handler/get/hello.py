import json
from ..handler import GetHandler
from ..requestData import RequestData

class Handler(GetHandler):
    def doGet(self, request_data: RequestData):
        ret = {'message': 'hello world from srcful!'}

        return 200, json.dumps(ret)