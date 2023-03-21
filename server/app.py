import queue
from threading import Thread
import time

from tasks.task import Task
from tasks.harvest import Harvest

from http.server import BaseHTTPRequestHandler, HTTPServer
import time

from inverters.inverter import Inverter
from inverters.InverterTCP import InverterTCP

import crypto.crypto as crypto

#hostName = "127.0.0.1"  # for local
hostName = "0.0.0.0"  # for docker deployment

serverPort = 5000

#inverter_ip = "127.0.0.1" #for local


def getChipInfo():
  crypto.initChip()

  device_name = crypto.getDeviceName()
  serial_number = crypto.getSerialNumber()

  crypto.release()

  return 'device: ' + device_name + ' serial: ' + serial_number
  # return 'device: dret' + ' serial: 0xdeadbeef'


def MyServerFactory(stats: dict):

  class MyServer(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
      super(MyServer, self).__init__(*args, **kwargs)

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

      self.wfile.write(bytes(f"<p>chipInfo: {getChipInfo()}</p>", "utf-8"))

      elapsedTime = time_ms() - startTime

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

  return MyServer


def time_ms():
  return time.time_ns() // 1_000_000


class ReadFreq(Task):
  def __init__(self, eventTime: int, stats: dict, inverter: Inverter):
    super().__init__(eventTime, stats)
    self.inverter = inverter
    self.stats['lastFreq'] = 'n/a'

  def execute(self, eventTime) -> Task or list[Task]:
    try:
      freq = self.inverter.readFrequency()
      self.stats['lastFreq'] = freq
      self.stats['freqReads'] += 1
    except:
      print('error reading freq')
      self.time = eventTime + 1000
      self.stats['lastFreq'] = 'error'
      return self

    self.time = eventTime + 100
    return self


def gatewayNameQuery(id):
  return """
  {
    gatewayConfiguration {
      gatewayName(id:"%s") {
        name
      }
    }
  }
  """ % id


class CheckForWebRequest(Task):
  def __init__(self, eventTime: int, stats: dict, webServer: HTTPServer):
    super().__init__(eventTime, stats)
    self.webServer = webServer

  def execute(self, eventTime):
    self.stats['webRequests'] += 1
    if self.webServer.request_queue_size > 0:
      # launch a new thread to handle the request
      t = Thread(target=self.webServer.handle_request)
      t.start()

    self.time = eventTime + 1000
    return self


def mainLoop(tasks: queue.PriorityQueue):

  # here we could keep track of statistics for different types of tasks
  # and adjust the delay to keep the within a certain range

  def addTask(task):
    if task.time < time_ms():
      print('task is in the past')
      task.time = time_ms() + 100
    tasks.put(task)

  while True:
    task = tasks.get()
    delay = (task.time - time_ms()) / 1000
    if delay > 0:
      time.sleep(delay)

    # if time_ms() % 2000 == 0:
    # print(task.stats)

    newTask = task.execute(time_ms())

    if newTask != None:
      try:
        for e in newTask:
          addTask(e)
      except TypeError:
        addTask(newTask)


def main():

  startTime = time_ms()
  stats = {'startTime': startTime, 'freqReads': 0,
           'energyHarvested': 0, 'webRequests': 0, 'name': 'deadbeef'}

  webServer = HTTPServer((hostName, serverPort), MyServerFactory(stats))
  webServer.socket.setblocking(False)
  print("Server started http://%s:%s" % (hostName, serverPort))

  inverter_ip = "10.130.1.235" # for solarEdge inverter in the lab at LNU
  #inverter_ip = "srcfull-inverter" # for testing with docker container service
  inverter_type = "solaredge"

  tasks = queue.PriorityQueue()
  # docker compose service name
  inverter = InverterTCP(inverter_ip, inverter_type)
  inverter.open()

  # put some initial tasks in the queue
  tasks.put(Harvest(startTime, stats, inverter))
  tasks.put(CheckForWebRequest(startTime, stats, webServer))
  tasks.put(ReadFreq(startTime, stats, inverter))

  try:
    mainLoop(tasks)
  except KeyboardInterrupt:
    pass
  finally:
    inverter.close()
    webServer.server_close()
    print("Server stopped.")


if __name__ == "__main__":
  main()
