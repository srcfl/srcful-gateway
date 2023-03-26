from typing import Callable
from http.server import BaseHTTPRequestHandler, HTTPServer
from .get import root


def requestHandlerFactory(stats: dict, timeMSFunc:Callable, chipInfoFunc:Callable):

  class MyHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
      super(MyHandler, self).__init__(*args, **kwargs)

    def do_GET(self):

      htlm = root.Handler().doGet(self.stats, self.timeMSFunc, self.chipInfoFunc)
      html_bytes = bytes(htlm, "utf-8")

      self.send_response(200)
      self.send_header("Content-type", "text/html")
      self.send_header("Content-Length", len(html_bytes))
      self.end_headers()
      
      self.wfile.write(html_bytes)
      

  return MyHandler

class Server:
  _webServer:HTTPServer = None

  def __init__(self, webHost:tuple[str, int], stats:dict, timeMSFunc:Callable, chipInfoFunc:Callable):
    self._webServer = HTTPServer(webHost, requestHandlerFactory(stats, timeMSFunc, chipInfoFunc))
    self._webServer.socket.setblocking(False)

  def close(self):
    if self._webServer:
      self._webServer.server_close()
      self._webServer = None

  def request_queue_size(self)->int:
    return self._webServer.request_queue_size
  
  def handle_request(self):
    self._webServer.handle_request()

  def __del__(self):
    self.close()