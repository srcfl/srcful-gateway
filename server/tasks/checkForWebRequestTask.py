from threading import Thread

from server.web.server import Server
from server.blackboard import BlackBoard

from .task import Task


class CheckForWebRequest(Task):
    def __init__(self, event_time: int, bb: BlackBoard, web_server: Server):
        super().__init__(event_time, bb)
        self.web_server = web_server

    def execute(self, event_time):
        while self.web_server.request_queue_size() > 0:
            # launch a new thread to handle the request
            t = Thread(target=self.web_server.handle_request)
            t.start()

        self.time = self.bb.time_ms() + 250
        return [self]
