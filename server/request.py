import requests
from threading import Thread

class ThreadedRESTRequest(Thread):
  def __init__(self):
    Thread.__init__(self)

  def get(self, url, headers=None):
    self.method = requests.get
    self.url = url
    self.data = None
    self.headers = headers
    self.response = None
    self.start()

  def post(self, url, data=None, json=None, headers=None):
    self.method = requests.post
    self.url = url
    self.data = data
    self.json = json
    self.headers = headers
    self.response = None
    self.start()

  def run(self):
    self.response = self.method(self.url, data=self.data, json=self.json, headers=self.headers)