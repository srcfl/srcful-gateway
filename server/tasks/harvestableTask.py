import logging
from typing import List, Union, Optional
from abc import abstractmethod
from server.app.blackboard import BlackBoard
from server.devices.ICom import ICom
from server.devices.Device import Device
from server.tasks.harvestTransport import ITransportFactory, DefaultHarvestTransportFactory
from server.tasks.itask import ITask
from .task import Task

logger = logging.getLogger(__name__)


class HarvestableTask(Task):
    def __init__(self, event_time: int, bb: BlackBoard, device: Union[ICom, Device], transport_factory: Optional[ITransportFactory] = None):
        super().__init__(event_time, bb)
        self.device = device
        self.barn: dict[int, dict] = {}
        self.transport_factory: ITransportFactory = transport_factory or DefaultHarvestTransportFactory()
        self.last_transport_time = bb.time_ms()
        self.harvest_count = 0
        self.total_harvest_time_ms = 0
        self.packet_count = 0
        self.data_points_count = 0
        self.packet_counter_timestamp = event_time

    def collect_harvest_data(self, event_time: int, force_verbose: Optional[bool] = None) -> dict:
        """Collect harvest data and store it in the barn"""
        start_time = event_time
        
        if force_verbose is None:
            force_verbose = self.harvest_count % 10 == 0
            
        harvest = self.device.read_harvest_data(force_verbose=force_verbose)
        self.harvest_count += 1
        end_time = self.bb.time_ms()
        
        elapsed_time_ms = end_time - start_time
        self.total_harvest_time_ms += elapsed_time_ms
        
        # Store harvest data in barn
        self.barn[end_time] = harvest
        
        return harvest

    def _create_headers(self, device: Union[ICom, Device]) -> dict:
        headers = {"model": ""}
        headers["dtype"] = device.get_harvest_data_type().value
        headers["sn"] = device.get_SN()
        headers["model"] = device.get_name().lower()
        return headers

    def _create_transport(self, event_time: int, endpoints: list[str], force_transport: bool = False) -> List[ITask]:
        ret: List[ITask] = []

        if not force_transport:
            # check if the lowest time in the barn is more than 10 seconds old
            force_transport = self.bb.time_ms() - self.last_transport_time >= 10000

        if (len(self.barn) > 0 and force_transport):
            logger.info("Filling the barn took %s ms for [%s] to endpoint %s", self.total_harvest_time_ms, self.device.get_SN(), endpoints)
            for endpoint in endpoints:

                headers = self._create_headers(self.device)

                transport = self.transport_factory(event_time + 100, self.bb, self.barn, headers)
                transport.post_url = endpoint
                ret.append(transport)

                self.packet_count += 1
                self.data_points_count += len(self.barn)

            if self.bb.time_ms() >= self.packet_counter_timestamp + 60000:
                logger.info("A total of [%s] data points were harvested from device [%s] in the last minute and [%s] packets were sent", self.data_points_count, self.device.get_SN(), self.packet_count)
                self.packet_counter_timestamp = self.bb.time_ms()
                self.packet_count = 0
                self.data_points_count = 0

            self.last_transport_time = self.bb.time_ms()
            self.barn = {}
            self.total_harvest_time_ms = 0

        return ret

    def create_final_transport(self, event_time: int, endpoints: list[str]) -> List[ITask]:
        """Create a final transport when finishing the task"""
        return self._create_transport(event_time, endpoints, force_transport=True)

    @abstractmethod
    def execute(self, event_time) -> Union[List[ITask], ITask, None]:
        pass 