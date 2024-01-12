from .task import Task
from threading import Thread
import requests

from server.blackboard import BlackBoard

import logging
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

def argToStr(arg):
  try:
    return str(arg)
  except:
    return "argument of type " + str(type(arg)) + " cannot be converted to string"

class SrcfulAPICallTask(Task):
  def __init__(self, eventTime: int, bb: BlackBoard):
    super().__init__(eventTime, bb)
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
      log.debug("post")
      try:
        data = self._data()    
        if data != None:
            log.debug("{} {}".format(self.post_url, argToStr(data)))
            self.reply = requests.post(self.post_url, data=data)
        else:
          json = self._json()
          if json != None:
            log.debug("{} {}".format(self.post_url, argToStr(json)))
            self.reply = requests.post(self.post_url, json=json)
          else:
            log.debug("{} {}".format(self.post_url, "no data or json"))
            self.reply = requests.post(self.post_url)
      except requests.exceptions.RequestException as e:
        log.exception(e)
        self.reply = requests.Response()

    if (self.t == None):
      self.t = Thread(target=post)
      self.t.start()
      self.time = eventTime + 1000
      log.debug("Started post thread")
      return self
    elif self.t.is_alive() == False:
      self.t = None
      if self.reply.status_code == 200:
        log.debug("Thead is finished: calling _on200")
        self._on200(self.reply)
      else:
        log.debug("Thead is finished: calling _onError")
        retryDelay = self._onError(self.reply)
        if retryDelay > 0:
          self.time = eventTime + retryDelay
          return self
    else:
      # wait some more
      log.debug("Waiting for reply")
      self.time = eventTime + 1000
      return self
