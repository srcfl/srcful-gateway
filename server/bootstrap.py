from .tasks.task import Task

from .inverters.InverterTCP import InverterTCP
from .inverters.InverterRTU import InverterRTU
from .tasks.openInverterTask import OpenInverterTask

import os

import logging
logger = logging.getLogger(__name__)

class BootstrapSaver():
  '''Abstract class for saving bootstrap tasks to a file'''
  def appendInverter(self, setup):
    '''Appends an inverter to the bootstrap file'''
    raise NotImplementedError("Subclass must implement abstract method")

class Bootstrap(BootstrapSaver):
  '''A bootstrap is a list of tasks that are executed on startup.'''
  def __init__(self, filename: str):
    self.filename = filename
    self.tasks = []
    self._createFileIfNotExists()

  
  # implementation of blackboard inverter observer
  def addInverter(self, inverter):
    self.appendInverter(inverter.getConfig())

  def removeInverter(self, inverter):
    logger.info('Removing inverter from bootstrap: {} not yet supported'.format(inverter.getConfig()))


  def _createFileIfNotExists(self):
    # create the directories and the file if it does not exist
    # log any errors
    if not os.path.exists(self.filename):

      try:
        os.makedirs(os.path.dirname(self.filename), exist_ok=True)
        with open(self.filename) as f:
          f.write('# This file contains the tasks that are executed on startup\n')
          f.write('# Each line contains a task name and its arguments\n')

      except Exception as e:
        logger.error('Failed to create file: {}'.format(self.filename))
        logger.error(e)


  def appendInverter(self, inverterArgs):
    self._createFileIfNotExists()

    # check if the setup already exists
    for task in self.getTasks(0, None):
      if isinstance(task, OpenInverterTask) and task.inverter.getConfig() == inverterArgs:
        return
    
    # append the setup to the file
    with open(self.filename, "w") as f:
      logger.info('Writing (w) inverter to bootstrap file: {}'.format(inverterArgs))
      f.write('OpenInverter {}\n'.format(" ".join(str(i) for i in inverterArgs)))

  def getTasks(self, eventTime, stats):
    self.tasks = []
    # read the file handle errors
    try:
      with open(self.filename, "r") as f:
        logger.info('Reading bootstrap file: {}'.format(self.filename))
        lines = f.readlines()
    except Exception as e:
      logger.error('Failed to read file: {}'.format(self.filename))
      logger.error(e)
      return self.tasks
    
    
    return self._processLines(lines, eventTime, stats)

  def _processLines(self, lines: list, eventTime, stats):
    # for each line, create a task and execute it
    for line in lines:
      line = line.strip()
      line = line.replace('\n', '')
      tokens = line.split(' ')

      # ignore empty lines, comments and lines without tokens
      if len(line) == 0 or line[0] == '#' or len(tokens) == 0:
        continue

      # get the task name
      taskName = tokens[0]

      # get the task arguments
      taskArgs = tokens[1:]

      # create the task
      task = self._createTask(taskName, taskArgs, eventTime, stats)
      if task is None:
        continue
      self.tasks.append(task)

    return self.tasks
  
  def _createTask(self, taskName: str, taskArgs: list, eventTime, bb):
    # currently we only support OpenInverter
    if taskName == 'OpenInverter':
      return self._createOpenInverterTask(taskArgs, eventTime, bb)
    else:
      logger.error('Unknown task: {} in file {}'.format(taskName, self.filename))
      return None
  
  def _createOpenInverterTask(self, taskArgs: list, eventTime, bb):
    # check the number of arguments
    if taskArgs[0] == 'TCP':
      ip = taskArgs[1]
      port = int(taskArgs[2])
      type = taskArgs[3]
      address = int(taskArgs[4])
      return OpenInverterTask(eventTime + 1000, bb, InverterTCP((ip, port, type, address)), self)
    elif taskArgs[0] == 'RTU':
      port = taskArgs[1]
      baudrate = int(taskArgs[2])
      bytesize = int(taskArgs[3])
      parity = taskArgs[4]
      stopbits = float(taskArgs[5])
      type = taskArgs[6]
      address = int(taskArgs[7])
      return OpenInverterTask(eventTime + 1000, bb, InverterRTU((port, baudrate, bytesize, parity, stopbits, type, address)), self)
  