# a simple echo endpoint that returns the data it received

import json

from ..handler import PostHandler
from ..requestData import RequestData

class Handler(PostHandler):
    def doPost(self, request_data: RequestData):
        ret = {'echo': request_data.data}

        return 200, json.dumps(ret)