import logging
from typing import List, Union
from server.app.blackboard import BlackBoard
from server.devices.Device import Device, DeviceMode, DeviceCommand, DeviceCommandType
from server.tasks.harvest import Harvest
from server.tasks.harvestTransport import DefaultHarvestTransportFactory
from server.tasks.itask import ITask
from .harvestableTask import HarvestableTask
from server.control.fuse_protection import handle_fuse_limit, State
from server.control.control import handle_self_consumption
from server.devices.DeeDecoder import DeeDecoder, SungrowDeeDecoder

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def logg_status(decoder: SungrowDeeDecoder, state: State, battery_power: int, event_time: int):
    logger.info('--------------------------------')
    logger.info(f"Event time: {event_time} Discharging battery")
    logger.info(f"State: {state}")
    logger.info(f"Grid power: {decoder.grid_power}")
    logger.info(f"Grid power limit: {decoder.grid_power_limit}")
    logger.info(f"Instantaneous battery power: {decoder.instantaneous_battery_power}")
    logger.info(f"Target battery power: {battery_power}")
    logger.info('--------------------------------')


class PowerLimitControllerTask(HarvestableTask):
    def __init__(self, event_time: int, bb: BlackBoard, device: Device):
        super().__init__(event_time, bb, device)
        self.is_initialized = False
        self.fuse_check_interval = 5000  # ms
        self.self_consumption_check_interval = 500  # ms
        self.last_fuse_check_action_time = 0
        self.last_self_consumption_check_action_time = 0

    def execute(self, event_time) -> Union[List[ITask], ITask, None]:
        start_time = event_time

        if self.device is None:
            logger.error(f"Device not found: {self.device.get_SN()}")
            return None

        # if not inited check here
        if not self.is_initialized:
            if self.device.profile.init_device(self.device):
                logging.info(f"Successfully initialized device {self.device.get_SN()}")
                self.is_initialized = True
            else:
                logging.error(f"Failed to initialize device {self.device.get_SN()}")

        # harvest data and store in barn (in control mode we do not want the mega harvest)
        harvest = self.collect_harvest_data(start_time, force_verbose=False)
        elapsed_time_ms = self.bb.time_ms() - start_time

        # check import/export limits
        decoder: SungrowDeeDecoder = self.device.get_dee_decoder()

        decoder.decode(self.device.get_last_harvest_data())

        # Initialize variables
        fuse_check_state = State.NO_ACTION

        if event_time - self.last_fuse_check_action_time >= self.fuse_check_interval:
            battery_power, fuse_check_state = handle_fuse_limit(decoder.l1_current,
                                                                decoder.l2_current,
                                                                decoder.l3_current,
                                                                decoder.l1_voltage,
                                                                decoder.grid_current_limit,
                                                                decoder.instantaneous_battery_power,
                                                                decoder.battery_soc,
                                                                decoder.battery_max_charge_discharge_power)
            self.last_fuse_check_action_time = event_time

        if fuse_check_state == fuse_check_state.NO_ACTION:
            if self.device.get_mode() == DeviceMode.SELF_CONSUMPTION:
                # Fuse check passed, we can continue with self consumption
                if event_time - self.last_self_consumption_check_action_time >= self.self_consumption_check_interval:
                    battery_power, self_consumption_check_state = handle_self_consumption(decoder.grid_power,
                                                                                          0,  # grid power limit is 0 in self consumption mode
                                                                                          decoder.instantaneous_battery_power,
                                                                                          decoder.battery_soc,
                                                                                          decoder.battery_max_charge_discharge_power,
                                                                                          decoder.min_battery_soc,
                                                                                          decoder.max_battery_soc)
                    if self_consumption_check_state != State.NO_ACTION:
                        self.device.profile.set_battery_power(self.device, battery_power)
                        self.last_self_consumption_check_action_time = event_time
            elif self.device.get_mode() == DeviceMode.CONTROL:
                # We are in control mode, execute commands
                if self.is_initialized:  # if in control mode, execute commands
                    while self.device.has_commands():
                        command: DeviceCommand = self.device.pop_command()  # pop each command from the device
                        if command.command_type == DeviceCommandType.SET_BATTERY_POWER:
                            self.device.profile.set_battery_power(self.device, command.values[0])

        else:
            # Fuse check failed, we need to adjust the battery power to the new limit
            self.device.profile.set_battery_power(self.device, battery_power)
            logg_status(decoder, fuse_check_state, battery_power, event_time)

        # deinit check here
        if self.device.get_mode() == DeviceMode.READ:
            # if self.is_initialized:
            if self.device.profile.deinit_device(self.device):
                logging.info(f"Successfully deinitialized device {self.device.get_SN()}")
                self.is_initialized = False
            else:
                logging.error(f"Failed to deinitialize device {self.device.get_SN()}")

            logging.info(f"Device {self.device.get_SN()} is in read mode, go to harvest")

            # Create final transport before switching to harvest mode
            transports = self.create_final_transport(event_time, self.bb.settings.harvest.endpoints)
            harvest_task = Harvest(event_time, self.bb, self.device, DefaultHarvestTransportFactory())

            return [harvest_task] + transports

        # Check if it's time to transport the harvest
        transport = self._create_transport(self.bb.time_ms() + elapsed_time_ms * 2, self.bb.settings.harvest.endpoints)

        self.time = self.bb.time_ms() + 500

        if len(transport) > 0:
            return [self] + transport
        return self
