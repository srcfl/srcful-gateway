
import logging
from typing import Any, List, Union
from server.tasks.harvest import Harvest
from server.tasks.itask import ITask
from server.tasks.openDevicePerpetualTask import DevicePerpetualTask
from server.app.blackboard import BlackBoard
from .task import Task
from .harvestTransport import ITransportFactory
from server.devices.ICom import DeviceMode, ICom, HarvestDataType
from server.devices.supported_devices.data_models import DERData, PVData, BatteryData, MeterData, Value


logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)


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
        self.last_reading_ms = bb.time_ms()

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
        transport = self._create_transport(event_time=self.bb.time_ms() + elapsed_time_ms * 2, 
                                           endpoints=self.bb.settings.harvest.endpoints, 
                                           force_transport=True) # Bypass the every n seconds 
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
    
    def _handle_harvest(self, event_time: int):
        start_time = self.bb.time_ms()
        next_event_time, harvest = self.harvester.harvest(event_time, self.device, self.bb)
        end_time = self.bb.time_ms()

        if harvest:
            self.harvest_count += 1
            self.barn[self.bb.time_ms()] = harvest
            
            # Publish harvest data to MQTT (non-blocking)
            try:
                device_sn = self.device.get_SN()
                # device_id = self.bb.crypto_state().serial_number.hex()

                der_data = self.device.harvest_to_ders(harvest)
                
                if der_data.pv:
                    der_data.pv.timestamp = start_time
                    der_data.pv.delta = end_time - start_time
                    topic = f"{der_data.pv.type}/{device_sn}/{der_data.format}/{der_data.version}"
                    payload = der_data.pv.to_dict(verbose=False)
                    self.bb.mqtt_service.publish(topic, payload)

                if der_data.battery:
                    der_data.battery.timestamp = start_time
                    der_data.battery.delta = end_time - start_time
                    topic = f"{der_data.battery.type}/{device_sn}/{der_data.format}/{der_data.version}"
                    payload = der_data.battery.to_dict(verbose=False)
                    self.bb.mqtt_service.publish(topic, payload)

                if der_data.meter:
                    der_data.meter.timestamp = start_time
                    der_data.meter.delta = end_time - start_time
                    topic = f"{der_data.meter.type}/{device_sn}/{der_data.format}/{der_data.version}"
                    payload = der_data.meter.to_dict(verbose=False)
                    self.bb.mqtt_service.publish(topic, payload)

                # Temporary stuff - publish full decoded data
                # all_decoded = self.device.harvest_to_decoded_dict(harvest)
                # topic = f"decoded/{device_sn}/json/v1"
                # self.bb.mqtt_service.publish(topic, all_decoded)
                
                logger.debug(f"Published harvest data for device {device_sn} to MQTT")
                logger.debug(f"Current BB Time: {self.bb.time_ms()}")
                logger.debug(f"This reading was {self.bb.time_ms() - self.last_reading_ms} ms")
                self.last_reading_ms = self.bb.time_ms()

            except Exception as mqtt_error:
                # Don't fail the harvest if MQTT publishing fails
                logger.error(f"Error publishing harvest data to MQTT: {mqtt_error}")
                
        return next_event_time

    def _handle_state(self, event_time: int) -> tuple[int, List[ITask]]:
        next_event_time = event_time + 100
        try:
            if self.device.get_device_mode() == DeviceMode.READ:
                next_event_time = self._handle_harvest(event_time)

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

                transport = self.transport_factory(event_time + 20, self.bb, self.barn, headers)
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