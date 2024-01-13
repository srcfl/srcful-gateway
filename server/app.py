import queue
import sys
import time
from server.tasks.checkForWebRequestTask import CheckForWebRequest
import server.web.server
from server.tasks.openInverterTask import OpenInverterTask
from server.inverters.InverterTCP import InverterTCP

from server.bootstrap import Bootstrap
from server.wifi.scan import WifiScanner

from server.blackboard import BlackBoard


def mainLoop(tasks: queue.PriorityQueue, bb: BlackBoard):
  # here we could keep track of statistics for different types of tasks
  # and adjust the delay to keep the within a certain range

  def addTask(task):
    if task.time < bb.time_ms():
      print('task is in the past adjusting time')
      task.time = bb.time_ms() + 100
    tasks.put(task)

  while True:
    task = tasks.get()
    delay = (task.time - bb.time_ms()) / 1000
    if delay > 0.01:
      time.sleep(delay)

    newTask = task.execute(bb.time_ms())

    if newTask != None:
      try:
        for e in newTask:
          addTask(e)
      except TypeError:
        addTask(newTask)


def main(webHost: tuple[str, int], inverter: InverterTCP.Setup|None = None, bootstrapFile: str|None = None):

  bb = BlackBoard()

  webServer = server.web.server.Server(webHost, bb)
  print("Server started http://%s:%s" % (webHost[0], webHost[1]))

  tasks = queue.PriorityQueue()

  bootstrap = Bootstrap(bootstrapFile)

  bb.inverters.addListener(bootstrap)

  try:
    s = WifiScanner()
    ssids = s.getSSIDs()
    print(f'Scanned SSIDs: {ssids}')
  except Exception as e:
    print(e)

  # put some initial tasks in the queue
  if inverter is not None:
    tasks.put(OpenInverterTask(bb.startTime, bb, InverterTCP(inverter)))

  for task in bootstrap.getTasks(bb.startTime + 500, bb):
    tasks.put(task)

  tasks.put(CheckForWebRequest(bb.startTime + 1000, bb, webServer))

  try:
    mainLoop(tasks, bb)
  except KeyboardInterrupt:
    pass
  except Exception as e:
    print("Unexpected error:", sys.exc_info()[0])
    print(e)
  finally:
    for i in bb.inverters.lst:
      i.close()
    webServer.close()
    print("Server stopped.")

# this is for debugging purposes only
if __name__ == "__main__":
  import logging
  logging.basicConfig()
  #handler = logging.StreamHandler(sys.stdout)
  #logging.root.addHandler(handler)
  logging.root.setLevel(logging.INFO)
  #main(('localhost', 5000), ("localhost", 502, "huawei", 1), 'bootstrap.txt')
  main(('localhost', 5000), None, 'bootstrap.txt')
