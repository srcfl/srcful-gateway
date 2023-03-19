from .task import Task
from .srcfulapitask import SrcfulAPICallTask
from inverters.inverter import Inverter

class HarvestTransport(SrcfulAPICallTask):
  # this is just generated code for now
  def __init__(self, eventTime: int, stats: dict, barn: dict):
    super().__init__(eventTime, stats)
    self.stats['lastHarvest'] = 'n/a'
    self.barn_ref = barn
    self.barn = dict(barn)

  def _query(self):
    return """
    mutation {
      harvestTransport(
        id: "1",
        harvest: %s,
      ) {
        id
      }
    }
    """ % (self.barn)

  def _on200(self, reply):
    self.stats['lastHarvestTransport'] = reply.json()['data']['harvestTransport']['id']
    self.stats['harvestTransports'] += 1

  def onError(self, reply):
    self._on200(reply)
    #print('error transporting harvest')
    #self.stats['lastHarvestTransport'] = 'error'

class Harvest(Task):
  def __init__(self, eventTime: int, stats: dict, inverter: Inverter):
    super().__init__(eventTime, stats)
    self.inverter = inverter
    self.stats['lastHarvest'] = 'n/a'
    self.barn = {}


  def execute(self, eventTime) -> Task or list[Task]:
    try:
      harvest = self.inverter.read()
      self.stats['lastHarvest'] = harvest
      self.stats['harvestReads'] += 1
      self.barn[eventTime] = harvest
    except :
      print('error reading harvest')
      self.time = eventTime + 2000
      self.stats['lastHarvest'] = 'error'
      return self
    
    self.time = eventTime + 1000

    # check if it is time to transport the harvest  
    if ((len(self.barn) >= 10 and len(self.barn) % 10 == 0) and (self.transport == None or self.transport.response != None)):

      self.transport =  HarvestTransport(eventTime + 100, self.stats, self.barn)
      self.barn.clear()
      return [self, self.transport]

    return self