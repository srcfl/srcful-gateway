import re
import json
import queue
from typing import Callable
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import unquote_plus

from . import get
from . import post


def requestHandlerFactory(stats: dict, timeMSFunc: Callable, chipInfoFunc: Callable, tasks: queue.Queue):

  class Handler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):


      self.api_get = {'crypto': get.crypto.Handler(),
                      'hello': get.hello.Handler(),
                      'name': get.name.Handler(),
                      'logger': get.logger.Handler(),
                      'inverter/modbus/holding/{address}': get.modbus.HoldingHandler()}
      self.api_post = {'invertertcp': post.inverterTCP.Handler(),
                       'inverterrtu': post.inverterRTU.Handler(),
                       'wifi': post.wifi.Handler(),
                       'initialize': post.initialize.Handler(),
                       'logger': post.logger.Handler(),
                       'inverter/modbus': post.modbus.Handler(),
                       'logger': post.logger.Handler()}

      self.api_get = Handler.convert_keys_to_regex(self.api_get)
      self.api_post = Handler.convert_keys_to_regex(self.api_post)
      self.tasks = tasks
      super(Handler, self).__init__(*args, **kwargs)

      

    @staticmethod
    def query2Dict(query_string: str):
      return Handler.post2Dict(query_string)

    @staticmethod
    def post2Dict(post_data: str):
      if "=" not in post_data:
        return {}
      return {unquote_plus(k): unquote_plus(v) for k, v in (x.split('=') for x in post_data.split('&'))}

    @staticmethod
    def convert_keys_to_regex(api_dict):
        regex_dict = {}
        for key, value in api_dict.items():
            key = re.sub(r'\{(.+?)\}', r'(?P<\1>.+)', key)
            regex_dict[re.compile('^' + key + '$')] = value
        return regex_dict

    @staticmethod
    def getAPIHandler(path: str, api_root: str, api_handler_regex: dict):
      if path.startswith(api_root):
        for pattern, handler in api_handler_regex.items():
            match = pattern.match(path[len(api_root):])
            if match:
                return handler, match.groupdict()
      return None, None

    @staticmethod
    def getData(headers: dict, rfile):
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

    def sendApiResponse(self, code: int, response: str):
      self.send_response(code)
      self.send_header("Content-type", "application/json")
      response = bytes(response, "utf-8")
      self.send_header("Content-Length", len(response))
      self.end_headers()
      self.wfile.write(response)

    def pre_do(self, path:str):
      parts = path.split('?')
      query_string = parts[1] if len(parts) > 1 else ""
      return parts[0], Handler.query2Dict(query_string)


    def do_POST(self):
      path, query = self.pre_do(self.path)

      handler, params = Handler.getAPIHandler(path, "/api/", self.api_post)
      if handler is not None:
        post_data = Handler.getData(self.headers, self.rfile)

        code, response = handler.doPost(post_data, params, stats, tasks)
        self.sendApiResponse(code, response)
        return
      else:
        self.send_response(404)
        self.end_headers()
        return

    def do_GET(self):

      path, query = self.pre_do(self.path)

      handler, params = Handler.getAPIHandler(path, "/api/", self.api_get)
      if handler is not None:
        code, response = handler.doGet(stats, params, timeMSFunc, chipInfoFunc)
        self.sendApiResponse(code, response)
      else:
        # check if we have a post handler
        handler, params = Handler.getAPIHandler(path, "/api/", self.api_post)
        if handler is not None:
          self.sendApiResponse(200, handler.jsonSchema())
          return
        else:
          htlm = get.root.Handler().doGet(stats, timeMSFunc, chipInfoFunc)
          html_bytes = bytes(htlm, "utf-8")

          self.send_response(200)
          self.send_header("Content-type", "text/html")
          self.send_header("Content-Length", len(html_bytes))
          self.end_headers()

          self.wfile.write(html_bytes)

  return Handler


class Server:
  _webServer: HTTPServer = None

  def __init__(self, webHost: tuple[str, int], stats: dict, timeMSFunc: Callable, chipInfoFunc: Callable):
    self.tasks = queue.Queue()
    self._webServer = HTTPServer(webHost, requestHandlerFactory(
        stats, timeMSFunc, chipInfoFunc, self.tasks))
    self._webServer.socket.setblocking(False)

  def close(self):
    if self._webServer:
      self._webServer.server_close()
      self._webServer = None

  def request_queue_size(self) -> int:
    return self._webServer.request_queue_size

  def handle_request(self):
    self._webServer.handle_request()

  def __del__(self):
    self.close()
