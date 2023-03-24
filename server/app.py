import argparse
import queue
import time
from tasks.checkForWebRequestTask import CheckForWebRequest
import web.server

from tasks.task import Task
from tasks.harvest import Harvest



import time

from inverters.inverter import Inverter
from inverters.InverterTCP import InverterTCP

import crypto.crypto as crypto


def getChipInfo():
  crypto.initChip()

  device_name = crypto.getDeviceName()
  serial_number = crypto.getSerialNumber().hex()

  crypto.release()

  return 'device: ' + device_name + ' serial: ' + serial_number
  # return 'device: dret' + ' serial: 0xdeadbeef'





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


def main(webHost:tuple[str, int], inverter:InverterTCP.Setup):

  startTime = time_ms()
  stats = {'startTime': startTime, 'freqReads': 0,
           'energyHarvested': 0, 'webRequests': 0, 'name': 'deadbeef'}

  
  print("Server started http://%s:%s" % (webHost[0], webHost[1]))

  #inverter_ip = "10.130.1.235" # for solarEdge inverter in the lab at LNU
  #inverter_ip = "srcfull-inverter" # for testing with docker container service
  #inverter_type = "solaredge"

  tasks = queue.PriorityQueue()
  # docker compose service name
  inverter = InverterTCP(inverter)
  inverter.open()

  webServer = web.server.Server(webHost, stats, time_ms, getChipInfo)

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
    webServer.close()
    print("Server stopped.")


if __name__ == "__main__":
  # parse arguments from command line
  parser = argparse.ArgumentParser(description='Srcful Energy Gateway')
  
  # port and host for the web server
  parser.add_argument('-wh', '--web_host', type=str, default='0.0.0.0', help='host for the web server.')
  parser.add_argument('-wp', '--web_port', type=int, default=5000, help='port for the web server.')

  # port, host and type for the inverter
  parser.add_argument('-ih', '--inverter_host', type=str, default='localhost', help='host for the inverter.')
  parser.add_argument('-ip', '--inverter_port', type=int, default=502, help='port for the inverter.')
  parser.add_argument('-it', '--inverter_type', type=str, default='solaredge', help='type of inverter (solaredge).')

  args = parser.parse_args()

  main((args.web_host, args.web_port), (args.inverter_host, args.inverter_port, args.inverter_type))