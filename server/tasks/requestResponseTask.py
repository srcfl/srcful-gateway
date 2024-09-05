import json
import logging
from typing import Dict, Any

from server.blackboard import BlackBoard
from server.tasks.task import Task
import server.crypto.crypto as crypto
from server.web import handler
from server.web.server import Endpoints
from .configurationMutationTask import ConfigurationMutationTask

logger = logging.getLogger(__name__)

class RequestTask(Task):
    SUBKEY = "request"
    

    def __init__(self, event_time: int, bb: BlackBoard, id, handler: handler.Handler, data: handler.RequestData):
        super().__init__(event_time, bb)
        self.request_data = data
        self.handler = handler
        self.id = id

    def execute(self, event_time):
        
        code, response = self.handler.do(self.request_data)
        response = {
            "code": code,
            "response": response
        }

        return ResponseTask(self.bb.time_ms() + 200, self.bb, self.id, response)

class ResponseTask(ConfigurationMutationTask):
    SUBKEY = "response"
    
    def __init__(self, event_time: int, bb: BlackBoard, id, response_data: Dict[str, Any]):
        logger.info("ResponseTask init %s", response_data)
        response_data['timestamp'] = int(bb.time_ms() / 1000)
        response_data['id'] = id
        super().__init__(event_time, bb, self.SUBKEY, response_data)

    def _on_200(self, reply):
        super()._on_200(reply)
        if self.is_saved:
            logger.info(f"Response for request {self.data['id']} sent successfully")
        else:
            logger.warning(f"Failed to send response for request {self.data['id']}")

    def _on_error(self, reply):
        super()._on_error(reply)
        logger.error(f"Error sending response for request {self.data['id']}")
        return 30000  # Retry after 30 seconds


def handle_request(bb: BlackBoard, request_data: Dict[str, Any]):
    try:
        method = request_data.get('method', '').upper()
        path = request_data.get('path', '')
        headers = request_data.get('headers', {})
        body = request_data.get('body', {})
        query = request_data.get('query', {})
        timestamp = request_data.get('timestamp', 0)
        id = request_data['id']
    except Exception as e:
        # find the missing keys
        missing_keys = [key for key in ['method', 'path', 'headers', 'body', 'query', 'timestamp', 'id'] if key not in request_data]
        return ResponseTask(bb.time_ms() + 500, bb, -1, {"error": f"Missing keys: {missing_keys}"})
    try:

        if timestamp < int(bb.time_ms() / 1000) - 60 * 1:
            return ResponseTask(bb.time_ms() + 500, bb, id, {"error": f"Request too old"})

        # Create a RequestData object
        endpoints = Endpoints()

        path, query = endpoints.pre_do(path)

        if method == 'GET':
            endpoints_dict = endpoints.api_get
        elif method == 'POST':
            endpoints_dict = endpoints.api_post
        elif method == 'DELETE':
            endpoints_dict = endpoints.api_delete
        else:
            return ResponseTask(bb.time_ms() + 500, bb, id, {"error": f"Method {method} not allowed"})
        
        api_handler, params = endpoints.get_api_handler(path, "/api/", endpoints_dict)
        rdata = handler.RequestData(bb, params, query, body)
        return RequestTask(bb.time_ms() + 500, bb, id, api_handler, rdata)

    except Exception as e:
        logger.exception(f"Error handling request: {e}")
        return ResponseTask(bb.time_ms() + 500, bb, id, {"error": f"Error handling request: {e}"})

def handle_request_task(bb: BlackBoard, data: Dict[str, Any]):
    if data['subKey'] == RequestTask.SUBKEY:
        request_data = json.loads(data['data'])
        return handle_request(bb, request_data)
