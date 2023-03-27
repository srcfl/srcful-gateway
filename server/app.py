import queue
import select
import sys
import time
from server.tasks.checkForWebRequestTask import CheckForWebRequest
import server.web.server

from server.tasks.openInverterTask import OpenInverterTask


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


  # put some initial tasks in the queue
  tasks.put(OpenInverterTask(startTime, stats, InverterTCP(inverter)))
  tasks.put(CheckForWebRequest(startTime, stats, webServer))

  try:
    mainLoop(tasks)
    #print("Sleeping for 10 seconds")
    #time.sleep(10)
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


