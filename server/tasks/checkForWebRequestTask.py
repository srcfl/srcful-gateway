from threading import Thread

from server.web.server import Server
from server.blackboard import BlackBoard

from .task import Task


class CheckForWebRequest(Task):
    def __init__(self, envent_time: int, bb: BlackBoard, web_server: Server):
        super().__init__(envent_time, bb)
        self.web_server = web_server

    def execute(self, event_time):
        if self.web_server.request_queue_size() > 0:
            # launch a new thread to handle the request
            t = Thread(target=self.web_server.handle_request)
            t.start()

        self.time = 1000
        self.time += self.bb.time_ms() + 1000
        return [self]
