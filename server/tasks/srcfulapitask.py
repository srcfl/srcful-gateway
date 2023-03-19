from tasks.task import Task
from threading import Thread
import requests

class SrcfulAPICallTask(Task):
  def __init__(self, eventTime: int, stats: dict):
    super().__init__(eventTime, stats)
    self.t = None
    self.reply = None

  def _query(self):
    # throw not implemented exception
    NotImplementedError
  def _on200(self, reply):
    # throw not implemented exception
    NotImplementedError
  
  def _onError(self, reply) -> int:
    '''return 0 to stop retrying, otherwise return the number of milliseconds to wait before retrying'''
    # throw not implemented exception
    NotImplementedError
  
  def execute(self, eventTime):

    def post():
      self.reply=requests.post("https://api.srcful.dev/", json={"query": self._query()})

    if (self.t == None):
      self.t = Thread(target=post())
      self.t.start()
      self.time = eventTime + 1000
      return self
    elif self.t.is_alive() == False:
      self.t = None
      if self.reply.status_code == 200:
        self._on200(self.reply)
      else:
        retryDelay = self._onError(self.reply)
        if retryDelay > 0:
          self.time = eventTime + retryDelay
          return self
    else:
      # wait some more
      self.time = eventTime + 1000
      return self