from threading import Thread

from server.web.server import Server
from server.blackboard import BlackBoard

from .task import Task

import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class CheckForWebRequest(Task):
    def __init__(self, event_time: int, bb: BlackBoard, web_server: Server):
        super().__init__(event_time, bb)
        self.web_server = web_server
        logger.setLevel(logging.INFO)

    def execute(self, event_time):
        
        if self.web_server.request_pending():
            logger.debug('request received')
            # launch a new thread to handle the request
            t = Thread(target=self.web_server.handle_request)
            t.start()
        else:
            logger.debug('no request received')

        self.time = self.bb.time_ms() + 250
        return [self]
