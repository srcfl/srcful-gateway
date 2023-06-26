from .task import Task
from server.inverters.inverter import Inverter
from .harvest import Harvest

import logging
log = logging.getLogger(__name__)


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
      return None

    self.time = eventTime + 100
    return self


class OpenInverterTask(Task):
  def __init__(self, eventTime: int, stats: dict, inverter: Inverter, bootstrap):
    super().__init__(eventTime, stats)
    self.inverter = inverter
    self.bootstrap = bootstrap

  def execute(self, eventTime):
    # Do this n times? 
    try:
      if self.inverter.open():
        if 'inverter' in self.stats and self.stats['inverter'] != None:
          self.stats['inverter'].terminate()
        self.stats['inverter'] = self.inverter
        if(self.bootstrap != None):
          self.bootstrap.appendInverter(self.inverter.getConfig())
        return [Harvest(eventTime + 10000, self.stats, self.inverter)]
      else:
        log.info('Failed to open inverter: %s', self.inverter.getType())
        return None
    except Exception as e:
      log.exception('Exception opening inverter: ')
      self.time = eventTime + 10000
      return self
