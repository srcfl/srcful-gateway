from .task import Task
from .srcfulAPICallTask import SrcfulAPICallTask
from server.inverters.inverter import Inverter
from server.blackboard import BlackBoard

import server.crypto.crypto as atecc608b
import requests

import logging
log = logging.getLogger(__name__)


class Harvest(Task):
  def __init__(self, eventTime: int, stats: dict, inverter: Inverter):
    super().__init__(eventTime, stats)
    self.inverter = inverter
    self.stats['lastHarvest'] = 'n/a'
    self.stats['harvests'] = 0
    self.barn = {}
    self.transport = None

    # incremental backoff stuff
    self.backoff_time = 1000  # start with a 1-second backoff
    self.max_backoff_time = 256000  # max ~4.3-minute backoff


  def execute(self, eventTime) -> Task | list[Task]:
    if self.inverter.isTerminated():
      return None
    
    try:
      harvest = self.inverter.readHarvestData()
      #self.stats['lastHarvest'] = harvest
      #self.stats['harvests'] += 1
      self.barn[eventTime] = harvest

      self.backoff_time = max(self.backoff_time - self.backoff_time * 0.1, 1000)

    except Exception as e:

      if self.backoff_time == self.max_backoff_time:
        log.info('Max backoff time reached, trying to close and reopen inverter at: %s:%s', self.inverter.getAddress(), self.inverter.getPort())
        if self.inverter.isOpen():
          self.inverter.close()
        else:
          self.inverter.open()
      else:
        log.debug('Handling exeption reading harvest: %s', str(e))
        self.backoff_time = min(self.backoff_time * 2, self.max_backoff_time)
        log.info('Incrementing backoff time to: %s', self.backoff_time)

    self.time = eventTime + self.backoff_time

    # check if it is time to transport the harvest
    if ((len(self.barn) >= 10 and len(self.barn) % 10 == 0) and (self.transport == None or self.transport.reply != None)):
      self.transport = HarvestTransport(eventTime + 100, self.stats, self.barn, self.inverter.getType())
      self.barn.clear()
      return [self, self.transport]

    return self


class HarvestTransport(SrcfulAPICallTask):

  def __init__(self, eventTime: int, bb: BlackBoard, barn: dict, inverter_type: str):
    super().__init__(eventTime, bb)
    #self.stats['lastHarvestTransport'] = 'n/a'
    #if 'harvestTransports' not in self.stats:
    #  self.stats['harvestTransports'] = 0
    self.barn_ref = barn
    self.barn = dict(barn)
    self.inverter_type = inverter_type

  def _data(self):
    atecc608b.initChip()
    JWT = atecc608b.buildJWT(self.barn, self.inverter_type)
    atecc608b.release()
    return JWT

  def _on200(self, reply):
    print("Response:", reply)
    #self.stats['harvestTransports'] += 1

  def _onError(self, reply: requests.Response):
    log.warning('Error in harvest transport: %s', str(reply))
    return 0
