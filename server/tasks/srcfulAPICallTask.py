from .task import Task
from threading import Thread
import requests

import logging
log = logging.getLogger(__name__)

class SrcfulAPICallTask(Task):
  def __init__(self, eventTime: int, stats: dict):
    super().__init__(eventTime, stats)
    self.t = None
    self.reply = None
    self.post_url = "https://testnet.srcful.dev/gw/data/"

  def _json(self):
    '''override to return the json to send to the server, json argument in post method'''
    return None

  def _data(self):
    '''override to return the data to send to the server, data argument in post method'''
    return None

  def _on200(self, reply: requests.Response):
    # throw not implemented exception
    raise NotImplementedError

  def _onError(self, reply: requests.Response) -> int:
    '''return 0 to stop retrying, otherwise return the number of milliseconds to wait before retrying'''
    # throw not implemented exception
    raise NotImplementedError

  def execute(self, eventTime):

    def post():
      try:
        data = self._data()
        if data != None:
            self.reply = requests.post(self.post_url, data=data)
        else:
          json = self._json()
          if json != None:
            self.reply = requests.post(self.post_url, json=json)
          else:
            self.reply = requests.post(self.post_url)
      except requests.exceptions.RequestException as e:
        log.exception(e)
        self.reply = requests.Response()

    if (self.t == None):
      self.t = Thread(target=post)
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
