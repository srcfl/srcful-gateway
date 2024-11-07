from abc import ABC, abstractmethod 
import logging
import requests
from typing import List, Union, Tuple
from .itask import ITask
from server.blackboard import BlackBoard
from .task import Task


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


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
    def _on_200(self, reply: requests.Response) -> Union[List[ITask], ITask, None]:
        """override to handle the reply from the server"""""

    @abstractmethod
    def _on_error(self, reply: requests.Response) -> Union[int, Tuple[int, Union[List[ITask], ITask, None]]]:
        """return 0 to stop retrying,
        otherwise return the number of milliseconds to wait before retrying and possible tasks to add to the scheduler"""

    def execute(self, event_time):

        # this is the function that will be executed in the thread
        def post():
            # pylint: disable=assignment-from-none
            data = self._data()
            if data is not None:
                logger.debug("%s %s", self.post_url, arg_2_str(data))
                return requests.post(self.post_url, data=data, timeout=5)
            else:
                json = self._json()
                if json is not None:
                    logger.debug("%s %s", self.post_url, arg_2_str(json))
                    return requests.post(self.post_url, json=json, timeout=5)
                else:
                    logger.debug("%s %s", self.post_url, "no data or json")
                    return requests.post(self.post_url, timeout=5)

        try:
            response = post()
            self.reply = response
            if self.reply.status_code == 200:
                return self._on_200(response)
            else:
                ret = self._on_error(response)
                if isinstance(ret, tuple):
                    retry_delay, tasks = ret
                else:
                    retry_delay = ret
                    tasks = None
                if retry_delay > 0:
                    self.time = event_time + retry_delay
                    # add self to the returned tasks, can be None, a single task or a list of tasks
                    if tasks is None:
                        tasks = self
                    elif isinstance(tasks, list):
                        tasks.append(self)
                    else:
                        tasks = [tasks, self]
                
                return tasks
                
        except Exception as e:
            logger.error("Error in SrcfulAPICallTask")
            # logger.exception("Error in SrcfulAPICallTask %s", e)
            self.reply = requests.Response()
            retry_delay = self._on_error(self.reply)
            if retry_delay > 0:
                self.time = self.time + retry_delay
                return self
