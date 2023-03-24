from typing import Callable
from http.server import BaseHTTPRequestHandler, HTTPServer


def requestHandlerFactory(stats: dict, timeMSFunc:Callable, chipInfoFunc:Callable):

  class MyHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
      super(MyHandler, self).__init__(*args, **kwargs)

    def do_GET(self):
      freqReads = stats['freqReads']
      energyHarvested = stats['harvests']
      energyTransported = 0
      if 'harvestTransports' in stats:
        energyTransported = stats['harvestTransports']
      startTime = stats['startTime']
      self.send_response(200)
      self.send_header("Content-type", "text/html")
      self.end_headers()
      self.wfile.write(
          bytes("<html><head><title>Srcful Energy Gateway</title></head>", "utf-8"))
      self.wfile.write(bytes("<p>Request: %s</p>" % self.path, "utf-8"))
      self.wfile.write(bytes("<body>", "utf-8"))
      self.wfile.write(bytes(f"<h1>Srcful Energy Gateway</h1>", "utf-8"))
      self.wfile.write(bytes(f"<h2>{stats['name']}</h2>", "utf-8"))

      self.wfile.write(bytes(f"<p>chipInfo: {chipInfoFunc()}</p>", "utf-8"))

      elapsedTime = timeMSFunc() - startTime

      # convert elapsedTime to days, hours, minutes, seconds in a tuple
      days, remainder = divmod(elapsedTime // 1000, 60*60*24)
      hours, remainder = divmod(remainder, 60*60)
      minutes, seconds = divmod(remainder, 60)

      # output the gateway current uptime in days, hours, minutes, seconds
      self.wfile.write(bytes(
          f"<p>Uptime (days, hours, minutes, seconds): {(days, hours, minutes, seconds)}</p>", "utf-8"))

      self.wfile.write(
          bytes(f"<p>freqReads: {freqReads} in {elapsedTime} ms<br/>", "utf-8"))
      self.wfile.write(bytes(
          f"average freqReads: {freqReads / elapsedTime * 1000} per second<br/>", "utf-8"))
      self.wfile.write(
          bytes(f"last freq: {stats['lastFreq']} Hz</p>", "utf-8"))

      self.wfile.write(bytes(
          f"<p>energyHarvested: {energyHarvested} in {elapsedTime} ms</br>", "utf-8"))
      self.wfile.write(bytes(
          f"average energyHarvested: {energyHarvested / elapsedTime * 1000} per second</p>", "utf-8"))

      self.wfile.write(bytes(
          f"<p>energyTransported: {energyTransported} in {elapsedTime} ms</br>", "utf-8"))
      self.wfile.write(bytes(
          f"average energyTransported: {energyTransported / elapsedTime * 1000} per second</p>", "utf-8"))
      
      self.wfile.write(bytes(
          f"ALL: {stats}</p>", "utf-8"))

      self.wfile.write(bytes("</body></html>", "utf-8"))

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