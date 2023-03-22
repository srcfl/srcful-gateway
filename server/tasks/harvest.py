from .task import Task
from .srcfulAPICallTask import SrcfulAPICallTask
from inverters.inverter import Inverter
import crypto.crypto as atecc608b

class Harvest(Task):
  def __init__(self, eventTime: int, stats: dict, inverter: Inverter):
    super().__init__(eventTime, stats)
    self.inverter = inverter
    self.stats['lastHarvest'] = 'n/a'
    self.stats['harvests'] = 0
    self.barn = {}
    self.transport = None


  def execute(self, eventTime) -> Task or list[Task]:
    try:
      harvest = self.inverter.read()
      self.stats['lastHarvest'] = harvest
      self.stats['harvests'] += 1
      self.barn[eventTime] = harvest
    except :
      print('error reading harvest')
      self.time = eventTime + 2000
      self.stats['lastHarvest'] = 'error'
      return self
    
    self.time = eventTime + 1000

    # check if it is time to transport the harvest  
    if ((len(self.barn) >= 10 and len(self.barn) % 10 == 0) and (self.transport == None or self.transport.reply != None)):
      #print("transporting harvest..." + str(len(self.barn)))
      self.transport =  HarvestTransport(eventTime + 100, self.stats, self.barn)
      self.barn.clear()
      return [self, self.transport]

    return self
  
class HarvestTransport(SrcfulAPICallTask):
  # this is just generated code for now
  def __init__(self, eventTime: int, stats: dict, barn: dict):
    super().__init__(eventTime, stats)
    self.stats['lastHarvestTransport'] = 'n/a'
    if 'harvestTransports' not in self.stats:
      self.stats['harvestTransports'] = 0
    self.barn_ref = barn
    self.barn = dict(barn)

  def _data(self):
    atecc608b.initChip()

    # Print pubKey to console
    # this is for testing?
    #atecc608b.getPublicKey()

    JWT = atecc608b.buildJWT(self.barn)
    # print(JWT)

    atecc608b.release()
    return JWT

  def _on200(self, reply):
    #self.stats['lastHarvestTransport'] = reply.json()['data']['harvestTransport']['id']
    #print("transported harvest..." + str(len(self.barn)))
    print("Response:", reply)
    self.stats['harvestTransports'] += 1

  def _onError(self, reply):
    print("Response:", reply)
    self._on200(reply)
    return 0
    #print('error transporting harvest')
    #self.stats['lastHarvestTransport'] = 'error'