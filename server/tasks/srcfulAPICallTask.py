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
        self.reply = None
        self.post_url = "https://devnet.srcful.dev/gw/data"

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

    def execute(self, event_time):

        # this is the function that will be executed in the thread
        def post():
            # pylint: disable=assignment-from-none
            data = self._data()
            if data is not None:
                log.debug("%s %s", self.post_url, arg_2_str(data))
                return requests.post(self.post_url, data=data, timeout=5)
            else:
                json = self._json()
                if json is not None:
                    log.debug("%s %s", self.post_url, arg_2_str(json))
                    return requests.post(self.post_url, json=json, timeout=5)
                else:
                    log.debug("%s %s", self.post_url, "no data or json")
                    return requests.post(self.post_url, timeout=5)

        try:
            response = post()
            self.reply = response
            if self.reply.status_code == 200:
                self._on_200(response)
            else:
                retry_delay = self._on_error(response)
                if retry_delay > 0:
                    self.time = event_time + retry_delay
                    return self
                
        except Exception as e:
            self.reply = requests.Response()
            retry_delay = self._on_error(self.reply)
            if retry_delay > 0:
                self.time = event_time + retry_delay
                return self
            log.exception(e)
