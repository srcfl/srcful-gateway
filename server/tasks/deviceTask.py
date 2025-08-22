
import logging
from typing import Any, List, Union
from server.tasks.harvest import Harvest
from server.tasks.itask import ITask
from server.tasks.openDevicePerpetualTask import DevicePerpetualTask
from server.app.blackboard import BlackBoard
from .task import Task
from .harvestTransport import ITransportFactory
from server.devices.ICom import DeviceMode, ICom
from server.devices.supported_devices.data_models import DERData, PVData, BatteryData, MeterData, Value
import requests


logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)

def post_to_mqtt_service(data, device_sn):
    response = requests.post(
        "http://localhost:8090/publish",
        json=data,
        timeout=2,
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code == 200:
        logger.debug(f"Published harvest data to MQTT for device {device_sn}")
    else:
        logger.warning(f"Failed to publish harvest data: {response.status_code}")

def publish_to_mqtt(timestamp: int, device_id: str, device_sn: str, der_data: DERData):
    # Publish to individual channel data to separate MQTT topics
    ders: List[PVData | BatteryData | MeterData] = der_data.get_ders()
    for der in ders:
        data = {
            "topic": f"{der.type}/{device_sn}",
            "payload": der.to_dict(verbose=False)
        }
        post_to_mqtt_service(data, device_sn) 


class DeviceTask(Task):
    '''Encapsulates basic device state behavior reading or controlling and the transport of harvest data'''

    def __init__(self, event_time: int, bb: BlackBoard, device: ICom, transport_factory: ITransportFactory):
        super().__init__(event_time, bb)
        self.device = device
        self.transport_factory = transport_factory
        self.last_transport_time = bb.time_ms()
        self.harvest_count = 0
        self.total_harvest_time_ms = 0
        self.packet_count = 0
        self.data_points_count = 0
        self.last_device_state = self.device.get_device_mode()
        self.barn: dict[int, dict[str, Any]] = {}

        self.harvester = Harvest()
        # self.controller = Controller(event_time, bb, device)

    def execute(self, event_time: int) -> Union[List[ITask], ITask, None]:

        tasks = self._handle_device_not_open(event_time)
        if len(tasks) > 0:
            return tasks

        self._handle_state_transition(self.last_device_state, self.device.get_device_mode())

        try:
            next_event_time, tasks = self._handle_state(event_time)
        except Exception as e:
            logger.error(f"Error harvesting from device {self.device.get_SN()}")
            next_event_time = self.bb.time_ms() + 5000  # we try again in 5 seconds

        self.adjust_time(next_event_time)

        elapsed_time_ms = self.bb.time_ms() - event_time
        transport = self._create_transport(self.bb.time_ms() + elapsed_time_ms * 2, self.bb.settings.harvest.endpoints)
        if len(transport) > 0:
            return tasks + transport
        return tasks
    

    def _handle_device_not_open(self, event_time: int) -> List[ITask]:
        if not self.device.is_open():
            logger.info("Device is closed make the final transport if there is anything in the barn")
            # self.bb.devices.remove(self.device)
            # self.bb.add_warning("Device unexpectedly closed, removing from blackboard and starting a new open device perpetual task")

            transports = self._create_transport(event_time, self.bb.settings.harvest.endpoints, force_transport=True)

            #  if the devices is not disconnected by the user, we need to start a new open device perpetual to try to reconnect
            if not self.device.is_disconnected():

                logger.info("Disconnecting device from harvest task")
                self.device.disconnect()

                open_inverter = DevicePerpetualTask(event_time + 30000, self.bb, self.device.clone())
                transports.append(open_inverter)

            return transports
        return []

    def _handle_state(self, event_time: int) -> tuple[int, List[ITask]]:
        next_event_time = event_time + 250
        try:
            if self.device.get_device_mode() == DeviceMode.READ:
                start_time = self.bb.time_ms()
                next_event_time, harvest = self.harvester.harvest(event_time, self.device, self.bb)
                end_time = self.bb.time_ms()

                if harvest:
                    self.harvest_count += 1
                    self.barn[self.bb.time_ms()] = harvest
                    
                    # Publish harvest data to MQTT (non-blocking)
                    try:
                        device_sn = self.device.get_SN()
                        device_id = self.bb.crypto_state().serial_number.hex()

                        decoded_harvest = self.device.dict_to_ders(harvest)
                        
                        if decoded_harvest.pv:
                            decoded_harvest.pv.timestamp = start_time
                            decoded_harvest.pv.delta = end_time - start_time
                        if decoded_harvest.battery:
                            decoded_harvest.battery.timestamp = start_time
                            decoded_harvest.battery.delta = end_time - start_time
                        if decoded_harvest.meter:
                            decoded_harvest.meter.timestamp = start_time
                            decoded_harvest.meter.delta = end_time - start_time
                        
                        # Simple POST to MQTT container
                        publish_to_mqtt(self.bb.time_ms(), device_id, device_sn, decoded_harvest)

                    except Exception as mqtt_error:
                        # Don't fail the harvest if MQTT publishing fails
                        logger.error(f"Error publishing harvest data to MQTT: {mqtt_error}")

            elif self.device.get_device_mode() == DeviceMode.CONTROL:
                # self.controller.execute(event_time)
                logger.info("Control mode not implemented yet")
                pass
            else:
                logger.error(f"Invalid device mode {self.device.get_device_mode()}")
        except ICom.ConnectionException as e:
            logger.error(f"Error harvesting from device {self.device.get_SN()}")
            self.device.disconnect()

            clone = self.device.clone()
            open_inverter = DevicePerpetualTask(self.bb.time_ms() + 30000, self.bb, clone)
            transports = self._create_transport(self.bb.time_ms(), self.bb.settings.harvest.endpoints, force_transport=True)

            return next_event_time, [open_inverter] + transports # we return the open_inverter to indicate that we are closing the device and need to reconnect

        
        return next_event_time, [self]  # we return self to indicate that we are ready to use the device again


    def _handle_state_transition(self, from_mode: DeviceMode, to_mode: DeviceMode):
        if from_mode != to_mode:
            if from_mode == DeviceMode.READ and to_mode == DeviceMode.CONTROL:
                # handle read to control state transition
                pass
            elif from_mode == DeviceMode.CONTROL and to_mode == DeviceMode.READ:
                # handle control to read state transition
                pass

        self.last_device_state = to_mode


    def _create_transport_headers(self, device: ICom) -> dict:
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

                headers = self._create_transport_headers(self.device)

                transport = self.transport_factory(event_time + 100, self.bb, self.barn, headers)
                transport.post_url = endpoint
                ret.append(transport)

                self.packet_count += 1
                self.data_points_count += len(self.barn)

            if self.bb.time_ms() % 60000 == 0:
                logger.info("A total of [%s] data points were harvested from device [%s] in the last minute and [%s] packets were sent", self.data_points_count, self.device.get_SN(), self.packet_count)
                self.packet_count = 0
                self.data_points_count = 0

            self.last_transport_time = self.bb.time_ms()
            self.barn = {}
            self.total_harvest_time_ms = 0

        return ret