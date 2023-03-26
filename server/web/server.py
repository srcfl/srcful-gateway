import json
from typing import Callable
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import unquote_plus
from .get import root


def requestHandlerFactory(stats: dict, timeMSFunc:Callable, chipInfoFunc:Callable):

  class Handler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
      super(Handler, self).__init__(*args, **kwargs)

      self.api_get = {}
      self.api_post = {}

    @staticmethod
    def post2Dict(post_data:str):
      if "=" not in post_data:
        return {}
      return {unquote_plus(k): unquote_plus(v) for k, v in (x.split('=') for x in post_data.split('&'))}
    
    @staticmethod
    def getAPIHandler(path:str, api_root:str, api_handler:dict):
      if path.startswith(api_root):
        handler = api_handler.get(path[len(api_root):])
        if handler:
          return handler
      return None
    
    @staticmethod
    def getData(headers:dict, rfile):
      content_length = int(headers['Content-Length'])
      content = rfile.read(content_length).decode("utf-8")

      if content_length == 0 or len(content) == 0:
        return {}

      try:
        post_data = json.loads(content)
      except json.decoder.JSONDecodeError:
        post_data = Handler.post2Dict(content)
      except:
        post_data = {}
        
      return post_data

    def do_POST(self):
      handler = Handler.getAPIHandler(self.path, "/api", self.api_post)
      if handler is not None:
        post_data = Handler.getData(self.headers, self.rfile)
        
        code, response = handler.doPost(post_data)
        self.send_response(code)
        self.send_header("Content-type", "application/json")
        response = bytes(response, "utf-8")
        self.send_header("Content-Length", len(response))
        self.end_headers()
        self.wfile.write(response)
        return
      else:
        self.send_response(404)
        self.end_headers()
        return

    def do_GET(self):

      htlm = root.Handler().doGet(stats, timeMSFunc, chipInfoFunc)
      html_bytes = bytes(htlm, "utf-8")

      self.send_response(200)
      self.send_header("Content-type", "text/html")
      self.send_header("Content-Length", len(html_bytes))
      self.end_headers()
      
      self.wfile.write(html_bytes)
      

  return Handler

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