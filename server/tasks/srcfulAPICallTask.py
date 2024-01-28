from abc import ABC, abstractmethod 
import logging
from threading import Thread
import requests

from server.blackboard import BlackBoard

from .task import Task

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


def arg_2_str(arg):
    try:
        return str(arg)
    except Exception:
        return "argument of type " + str(type(arg)) + " cannot be converted to string"


class SrcfulAPICallTask(Task, ABC):
    def __init__(self, event_time: int, bb: BlackBoard):
        super().__init__(event_time, bb)
        self.t = None
        self.reply = None
        self.post_url = "https://testnet.srcful.dev/gw/data/"

    def _json(self) -> dict:
        """override to return the json to send to the server json argument in post"""
        return None

    def _data(self) -> any:
        """override to return the data to send to the server, data argument in post"""
        return None

    @abstractmethod
    def _on_200(self, reply: requests.Response):
        """override to handle the reply from the server"""""

    @abstractmethod
    def _on_error(self, reply: requests.Response) -> int:
        """return 0 to stop retrying,
        otherwise return the number of milliseconds to wait before retrying"""

    def execute_and_wait(self):
        """execute the task and block until finished"""
        self.execute(0)
        self.t.join()
        self.execute(0)

    def execute(self, event_time):

        # this is the function that will be executed in the thread
        def post():
            log.debug("post")
            try:
                # pylint: disable=assignment-from-none
                data = self._data()
                if data is not None:
                    log.debug("%s %s", self.post_url, arg_2_str(data))
                    self.reply = requests.post(self.post_url, data=data)
                else:
                    json = self._json()
                    if json is not None:
                        log.debug("%s %s", self.post_url, arg_2_str(json))
                        self.reply = requests.post(self.post_url, json=json)
                    else:
                        log.debug("%s %s", self.post_url, "no data or json")
                        self.reply = requests.post(self.post_url)
            except requests.exceptions.RequestException as e:
                log.exception(e)
                self.reply = requests.Response()

        if self.t is None:
            self.t = Thread(target=post)
            self.t.start()
            self.time = event_time + 1000
            log.debug("Started post thread")
            return self
        elif self.t.is_alive() is False:
            self.t = None
            if self.reply.status_code == 200:
                log.debug("Thead is finished: calling _on200")
                self._on_200(self.reply)
            else:
                log.debug("Thead is finished: calling _onError")
                retry_delay = self._on_error(self.reply)
                if retry_delay > 0:
                    self.time = event_time + retry_delay
                    return self
        else:
            # wait some more
            log.debug("Waiting for reply")
            self.time = event_time + 1000
            return self
