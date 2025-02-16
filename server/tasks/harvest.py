
import logging
from typing import List, Union
from server.tasks.itask import ITask
from server.tasks.openDevicePerpetualTask import DevicePerpetualTask
from server.app.blackboard import BlackBoard
from .task import Task
from .harvestTransport import ITransportFactory
from server.devices.ICom import ICom

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)


class Harvest(Task):
    def __init__(self, event_time: int, bb: BlackBoard, device: ICom, transport_factory: ITransportFactory):
        super().__init__(event_time, bb)
        self.device = device
        self.barn: dict[int, dict] = {}
        
        self.backoff_time = 1000 # start with a 1-second backoff
        self.transport_factory = transport_factory
        self.last_transport_time = bb.time_ms()
        self.harvest_count = 0

    def execute(self, event_time) -> Union[List[ITask], ITask, None]:

        start_time = event_time
        elapsed_time_ms = 1000

        if not self.device.is_open():
            logger.info("Device is closed make the final transport if there is anything in the barn")
            # self.bb.devices.remove(self.device)
            # self.bb.add_warning("Device unexpectedly closed, removing from blackboard and starting a new open device perpetual task")

            
            transports = self._create_transport(event_time, self.bb.settings.harvest.endpoints, force_transport=True)

            #  if the devices is not terminated, we need to start a new open device perpetual to try to reconnect
            if not self.device.is_disconnected():
                
                logger.info("Disconnecting device from harvest task")
                self.device.disconnect()
                
                open_inverter = DevicePerpetualTask(event_time + 30000, self.bb, self.device.clone())
                transports.append(open_inverter)
            
            return transports
    
        try:
            harvest = self.device.read_harvest_data(force_verbose=self.harvest_count % 10 == 0)
            self.harvest_count += 1
            end_time = self.bb.time_ms()

            elapsed_time_ms = end_time - start_time
            self.backoff_time = self.device.get_backoff_time_ms(elapsed_time_ms, self.backoff_time)
            logger.debug("Harvest from [%s] took %s ms", self.device.get_SN(), elapsed_time_ms)


            self.barn[end_time] = harvest

        except Exception as e:
            
            # To-Do: Solarmanv5 can raise ConnectionResetError, so handle it!
            logger.debug("Handling exeption reading harvest: %s", str(e))
            logger.debug("Kill everything, transport what is left and reopen in 30 seconds")
            
            self.device.disconnect()
            
            open_inverter = DevicePerpetualTask(self.bb.time_ms() + 30000, self.bb, self.device.clone())
            transports = self._create_transport(self.bb.time_ms(), self.bb.settings.harvest.endpoints, force_transport=True)
    
            return [open_inverter] + transports
            
        self.time = self.bb.time_ms() + self.backoff_time

        # check if it is time to transport the harvest
        transport = self._create_transport(self.bb.time_ms() + elapsed_time_ms * 2, self.bb.settings.harvest.endpoints)
        if len(transport) > 0:
            return [self] + transport
        return self
    
    def _create_headers(self, device: ICom) -> dict:
        headers = {"model": ""}
        headers["dtype"] = device.get_harvest_data_type().value
        headers["sn"] = device.get_SN()
        headers["model"] = device.get_name().lower()
        return headers

    def _create_transport(self, event_time: int, endpoints: list[str], force_transport: bool = False) -> List[ITask]:
        ret: List[ITask] = []

        if not force_transport:
            # check if the lowest time in the barn is more than 10 seconds old
            force_transport =  self.bb.time_ms() - self.last_transport_time >= 10000

        if (len(self.barn) > 0 and force_transport):
            for endpoint in endpoints:
                logger.info("Creating transport for %s", endpoint)
                
                headers = self._create_headers(self.device)
                    
                transport = self.transport_factory(event_time + 100, self.bb, self.barn, headers)
                transport.post_url = endpoint
                ret.append(transport)

            self.last_transport_time = self.bb.time_ms()
            self.barn = {}
        return ret