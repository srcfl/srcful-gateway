
import logging
from typing import List
from server.tasks.openDevicePerpetualTask import DevicePerpetualTask
from server.blackboard import BlackBoard
from .task import Task
from .harvestTransport import ITransportFactory
from server.inverters.ICom import ICom

log = logging.getLogger(__name__)


class Harvest(Task):
    def __init__(self, event_time: int, bb: BlackBoard, device: ICom, transport_factory: ITransportFactory):
        super().__init__(event_time, bb)
        self.device = device
        self.barn = {}
        
        # incremental backoff stuff
        self.min_backoff_time = 1000
        self.backoff_time = self.min_backoff_time  # start with a 1-second backoff
        self.max_backoff_time = 256000 # max ~4.3-minute backoff
        self.transport_factory = transport_factory

    def execute(self, event_time) -> Task | list[Task]:

        start_time = event_time
        elapsed_time_ms = 1000

        if not self.device.is_open():
            log.info("This should never happen unless the device is unexpectedly closed. Inverter is terminated make the final transport if there is anything in the barn")
            self.device.disconnect()
            self.bb.devices.remove(self.device)
            self.bb.add_warning("Device unexpectedly closed, removing from blackboard and starting a new open device perpetual task")
            open_inverter = DevicePerpetualTask(event_time + 30000, self.bb, self.device.clone())
            transports = self._create_transport(1, event_time, self.bb.settings.harvest._endpoints)
            return [open_inverter] + transports
        
        try:
            harvest = self.device.read_harvest_data(force_verbose=len(self.barn) == 0)
            end_time = self.bb.time_ms()

            elapsed_time_ms = end_time - start_time
            log.debug("Harvest from [%s] took %s ms", self.device.get_SN(), elapsed_time_ms)

            self.min_backoff_time = max(elapsed_time_ms * 2, 1000)

            self.barn[event_time] = harvest

            self.backoff_time = max(self.backoff_time - self.backoff_time * 0.1, self.min_backoff_time)
            self.backoff_time = min(self.backoff_time, self.max_backoff_time)

        except Exception as e:
            
            # To-Do: Solarmanv5 can raise ConnectionResetError, so handle it!
            log.debug("Handling exeption reading harvest: %s", str(e))
            log.debug("Kill everything, transport what is left and reopen in 30 seconds")
            
            self.device.disconnect()
            self.bb.devices.remove(self.device)
            self.bb.add_error("Exception reading harvest, device unexpectedly closed")
            open_inverter = DevicePerpetualTask(event_time + 30000, self.bb, self.device.clone())
            transports = self._create_transport(1, event_time, self.bb.settings.harvest._endpoints)
    
            return [open_inverter] + transports
            
        self.time = event_time + self.backoff_time

        # check if it is time to transport the harvest
        transport = self._create_transport(10, event_time + elapsed_time_ms * 2, self.bb.settings.harvest._endpoints)
        if len(transport) > 0:
            return [self] + transport
        return self

    def _create_transport(self, limit: int, event_time: int, endpoints: list[str]) -> List[Task]:
        ret = []
        if (len(self.barn) > 0 and len(self.barn) % limit == 0):
            for endpoint in endpoints:
                log.info("Creating transport for %s", endpoint)
                
                headers = {"model": ""}
                headers["dtype"] = self.device.get_harvest_data_type()
                headers["sn"] = self.device.get_SN()
                
                if self.device.get_profile():
                    headers["model"] = self.device.get_profile().name.lower()
                    
                transport = self.transport_factory(event_time + 100, self.bb, self.barn, headers)
                transport.post_url = endpoint
            self.barn = {}
            ret.append(transport)
        return ret