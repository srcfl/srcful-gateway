from .task import Task
from server.inverters.inverter import Inverter
from .harvest import Harvest


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
  def __init__(self, eventTime: int, stats: dict, inverter:Inverter):
    super().__init__(eventTime, stats)
    self.inverter = inverter

  def execute(self, eventTime):
    try:
      if self.inverter.open():
        if 'inverter' in self.stats and self.stats['inverter'] != None:
          self.stats['inverter'].close()
        self.stats['inverter'] = self.inverter
        print("Inverter opened")
        return [ReadFreq(eventTime + 1300, self.stats, self.inverter), Harvest(eventTime + 10000, self.stats, self.inverter)]
      else:
        print("Could not open inverter")
        return None
    except Exception as e:
      print('exception error opening inverter:', e)
      self.time = eventTime + 3000
      return self
