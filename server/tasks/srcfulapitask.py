from tasks.task import Task
from threading import Thread
import requests

class SrcfulAPICallTask(Task):
  def __init__(self, eventTime: int, stats: dict):
    super().__init__(eventTime, stats)
    self.t = None

  def _query(self):
    # throw not implemented exception
    NotImplementedError
  def _on200(self, reply):
    # throw not implemented exception
    NotImplementedError
  
  def onError(self, reply):
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
        self._onError(self.reply)
      self.time = eventTime + 10000
      return self
    else:
      # wait some more
      self.time = eventTime + 1000
      return self