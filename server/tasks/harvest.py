
import logging
from typing import List, Union
from server.tasks.itask import ITask
from server.tasks.openDevicePerpetualTask import DevicePerpetualTask
from server.blackboard import BlackBoard
from .task import Task
from .harvestTransport import ITransportFactory
from server.devices.ICom import ICom

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)


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

    def execute(self, event_time) -> Union[List[ITask], ITask, None]:

        start_time = event_time
        elapsed_time_ms = 1000

        if not self.device.is_open():
            logger.info("Device is closed make the final transport if there is anything in the barn")
            # self.bb.devices.remove(self.device)
            # self.bb.add_warning("Device unexpectedly closed, removing from blackboard and starting a new open device perpetual task")

            
            transports = self._create_transport(1, event_time, self.bb.settings.harvest.endpoints)

            #  if the devices is not terminated, we need to start a new open device perpetual to try to reconnect
            if not self.device.is_disconnected():
                open_inverter = DevicePerpetualTask(event_time + 30000, self.bb, self.device.clone())
                transports.append(open_inverter)
            
            return transports
    
        try:
            harvest = self.device.read_harvest_data(force_verbose=len(self.barn) == 0)
            end_time = self.bb.time_ms()

            elapsed_time_ms = end_time - start_time
            logger.debug("Harvest from [%s] took %s ms", self.device.get_SN(), elapsed_time_ms)

            self.min_backoff_time = max(elapsed_time_ms * 2, 1000)

            self.barn[event_time] = harvest

            self.backoff_time = max(self.backoff_time - self.backoff_time * 0.1, self.min_backoff_time)
            self.backoff_time = min(self.backoff_time, self.max_backoff_time)

        except Exception as e:
            
            # To-Do: Solarmanv5 can raise ConnectionResetError, so handle it!
            logger.debug("Handling exeption reading harvest: %s", str(e))
            logger.debug("Kill everything, transport what is left and reopen in 30 seconds")
            
            self.device.disconnect()
            
            open_inverter = DevicePerpetualTask(event_time + 30000, self.bb, self.device.clone())
            transports = self._create_transport(1, event_time, self.bb.settings.harvest.endpoints)
    
            return [open_inverter] + transports
            
        self.time = event_time + self.backoff_time

        # check if it is time to transport the harvest
        transport = self._create_transport(10, event_time + elapsed_time_ms * 2, self.bb.settings.harvest.endpoints)
        if len(transport) > 0:
            return [self] + transport
        return self
    
    def _create_headers(self, device: ICom) -> dict:
        headers = {"model": ""}
        headers["dtype"] = device.get_harvest_data_type().value
        headers["sn"] = device.get_SN()
        headers["model"] = device.get_name().lower()
        return headers

    def _create_transport(self, limit: int, event_time: int, endpoints: list[str]) -> List[ITask]:
        ret: List[ITask] = []
        if (len(self.barn) > 0 and len(self.barn) % limit == 0):
            for endpoint in endpoints:
                logger.info("Creating transport for %s", endpoint)
                
                headers = self._create_headers(self.device)
                    
                transport = self.transport_factory(event_time + 100, self.bb, self.barn, headers)
                transport.post_url = endpoint
                ret.append(transport)

            self.barn = {}
        return ret