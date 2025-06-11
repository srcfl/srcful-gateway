import logging
from typing import List, Union
from server.app.blackboard import BlackBoard
from server.devices.Device import Device, DeviceMode, DeviceCommand, DeviceCommandType
from server.tasks.harvest import Harvest
from server.tasks.harvestTransport import DefaultHarvestTransportFactory
from server.tasks.itask import ITask
from .harvestableTask import HarvestableTask
from server.control.control import check_import_export_limits, State
from server.devices.DeeDecoder import DeeDecoder, SungrowDeeDecoder

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class PowerLimitControllerTask(HarvestableTask):
    def __init__(self, event_time: int, bb: BlackBoard, device: Device):
        super().__init__(event_time, bb, device)
        self.is_initialized = False
        self.last_action_time = 0

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
        state = State.NO_ACTION

        # check import/export limits every 5 seconds
        if event_time - self.last_action_time >= 5000:
            battery_power, state = check_import_export_limits(decoder.grid_power,
                                                              decoder.grid_power_limit,
                                                              decoder.instantaneous_battery_power,
                                                              decoder.battery_soc,
                                                              decoder.battery_max_charge_discharge_power,
                                                              decoder.min_battery_soc,
                                                              decoder.max_battery_soc)

        if state == State.DISCHARGE_BATTERY:
            logger.info('--------------------------------')
            logger.info(f"Event time: {event_time} Discharging battery")
            logger.info(f"State: {state}")
            logger.info(f"Grid power: {decoder.grid_power}")
            logger.info(f"Grid power limit: {decoder.grid_power_limit}")
            logger.info(f"Instantaneous battery power: {decoder.instantaneous_battery_power}")
            logger.info(f"Target battery power: {battery_power}")
            logger.info('--------------------------------')

            self.device.profile.set_battery_power(self.device, -battery_power)
            bb_message = f"Discharging battery to {battery_power} W to reduce import"
            logger.info(bb_message)
            self.bb.add_warning(bb_message)
            self.last_action_time = event_time
        elif state == State.CHARGE_BATTERY:
            logger.info('--------------------------------')
            logger.info(f"Event time: {event_time} Charging battery")
            logger.info(f"State: {state}")
            logger.info(f"Grid power: {decoder.grid_power}")
            logger.info(f"Grid power limit: {decoder.grid_power_limit}")
            logger.info(f"Instantaneous battery power: {decoder.instantaneous_battery_power}")
            logger.info(f"Target battery power: {battery_power}")
            logger.info('--------------------------------')

            self.device.profile.set_battery_power(self.device, battery_power)
            bb_message = f"Charging battery to {battery_power} W to reduce export"
            logger.info(bb_message)
            self.bb.add_warning(bb_message)
            self.last_action_time = event_time
        elif state == State.NO_ACTION:
            pass  # do nothing

        if self.is_initialized:  # if in control mode, execute commands
            while self.device.has_commands():
                command: DeviceCommand = self.device.pop_command()  # pop each command from the device
                if command.command_type == DeviceCommandType.SET_BATTERY_POWER:
                    self.device.profile.set_battery_power(self.device, command.values[0])

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
