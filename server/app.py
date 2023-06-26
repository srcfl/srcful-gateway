import queue
import sys
import time
from server.tasks.checkForWebRequestTask import CheckForWebRequest
from server.tasks.checkForBluetoothRequestTask import CheckForBLERequest
import server.web.server
from server.tasks.openInverterTask import OpenInverterTask
from server.inverters.InverterTCP import InverterTCP
import server.crypto.crypto as crypto
from server.bootstrap import Bootstrap


def getChipInfo():
  crypto.initChip()

  device_name = crypto.getDeviceName()
  serial_number = crypto.getSerialNumber().hex()

  crypto.release()

  return 'device: ' + device_name + ' serial: ' + serial_number


def time_ms():
  return time.time_ns() // 1_000_000


def mainLoop(tasks: queue.PriorityQueue):
  # here we could keep track of statistics for different types of tasks
  # and adjust the delay to keep the within a certain range

  def addTask(task):
    if task.time < time_ms():
      print('task is in the past adjusting time')
      task.time = time_ms() + 100
    tasks.put(task)

  while True:
    task = tasks.get()
    delay = (task.time - time_ms()) / 1000
    if delay > 0.01:
      time.sleep(delay)

    newTask = task.execute(time_ms())

    if newTask != None:
      try:
        for e in newTask:
          addTask(e)
      except TypeError:
        addTask(newTask)


def main(webHost: tuple[str, int], inverter: InverterTCP.Setup|None = None, bootstrapFile: str|None = None):

  startTime = time_ms()
  stats = {'startTime': startTime, 'freqReads': 0,
           'energyHarvested': 0, 'webRequests': 0, 'name': 'deadbeef'}

  webServer = server.web.server.Server(webHost, stats, time_ms, getChipInfo)
  print("Server started http://%s:%s" % (webHost[0], webHost[1]))

  tasks = queue.PriorityQueue()

  bootstrap = Bootstrap(bootstrapFile)

  # put some initial tasks in the queue
  if inverter is not None:
    tasks.put(OpenInverterTask(startTime, stats, InverterTCP(inverter), bootstrap))

  # this is a hack to pass the bootstrap object to the post API that also creates open inverter tasks
  # this should really be handled better i.e. blackboard pattern with some observer pattern
  stats['bootstrap'] = bootstrap
  for task in bootstrap.getTasks(startTime + 500, stats):
    tasks.put(task)

  tasks.put(CheckForWebRequest(startTime + 1000, stats, webServer))

  try:
    mainLoop(tasks)
  except KeyboardInterrupt:
    pass
  except Exception as e:
    print("Unexpected error:", sys.exc_info()[0])
    print(e)
  finally:
    if 'inverter' in stats and stats['inverter'] is not None:
      stats['inverter'].close()
    webServer.close()
    print("Server stopped.")

# this is for debugging purposes only
if __name__ == "__main__":
  import logging
  logging.basicConfig()
  #handler = logging.StreamHandler(sys.stdout)
  #logging.root.addHandler(handler)
  logging.root.setLevel(logging.INFO)
  main(('localhost', 5000), ("localhost", 502, "huawei", 1))
