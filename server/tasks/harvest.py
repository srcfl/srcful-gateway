from .task import Task
from .srcfulAPICallTask import SrcfulAPICallTask
from server.inverters.inverter import Inverter
import server.crypto.crypto as atecc608b
import requests

class Harvest(Task):
  def __init__(self, eventTime: int, stats: dict, inverter: Inverter):
    super().__init__(eventTime, stats)
    self.inverter = inverter
    self.stats['lastHarvest'] = 'n/a'
    self.stats['harvests'] = 0
    self.barn = {}
    self.transport = None

  def execute(self, eventTime) -> Task | list[Task]:
    try:
      harvest = self.inverter.read()
      self.stats['lastHarvest'] = harvest
      self.stats['harvests'] += 1
      self.barn[eventTime] = harvest
    except Exception as e:
      print('error reading harvest', e)
      return None
    
    self.time = eventTime + 1000

    # check if it is time to transport the harvest  
    if ((len(self.barn) >= 10 and len(self.barn) % 10 == 0) and (self.transport == None or self.transport.reply != None)):
      self.transport =  HarvestTransport(eventTime + 100, self.stats, self.barn)
      self.barn.clear()
      return [self, self.transport]

    return self
  
class HarvestTransport(SrcfulAPICallTask):
  
  def __init__(self, eventTime: int, stats: dict, barn: dict):
    super().__init__(eventTime, stats)
    self.stats['lastHarvestTransport'] = 'n/a'
    if 'harvestTransports' not in self.stats:
      self.stats['harvestTransports'] = 0
    self.barn_ref = barn
    self.barn = dict(barn)

  def _data(self):
    atecc608b.initChip()
    JWT = atecc608b.buildJWT(self.barn)
    atecc608b.release()
    return JWT

  def _on200(self, reply):
    print("Response:", reply)
    self.stats['harvestTransports'] += 1

  def _onError(self, reply:requests.Response):
    print("Response:", reply)
    self._on200(reply)
    return 0