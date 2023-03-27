import queue
import time
from server.tasks.checkForWebRequestTask import CheckForWebRequest
import server.web.server

from server.tasks.task import Task
from server.tasks.harvest import Harvest

import time

from server.inverters.inverter import Inverter
from server.inverters.InverterTCP import InverterTCP

import server.crypto.crypto as crypto


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

  
  webServer = server.web.server.Server(webHost, stats, time_ms, getChipInfo)
  print("Server started http://%s:%s" % (webHost[0], webHost[1]))

  #inverter_ip = "10.130.1.235" # for solarEdge inverter in the lab at LNU
  #inverter_ip = "srcfull-inverter" # for testing with docker container service
  #inverter_type = "solaredge"

  tasks = queue.PriorityQueue()
  # docker compose service name
  inverter = InverterTCP(inverter)
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
    webServer.close()
    print("Server stopped.")


