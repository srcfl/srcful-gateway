import logging
from server.app.blackboard import BlackBoard
from server.devices.Device import Device, DeviceMode, DeviceCommand, DeviceCommandType
from server.tasks.harvest import Harvest
from server.tasks.harvestTransport import DefaultHarvestTransportFactory
from .task import Task
from server.control.control import check_import_export_limits, State
from server.devices.DeeDecoder import DeeDecoder, SungrowDeeDecoder

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class PowerLimitControllerTask(Task):
    def __init__(self, event_time: int, bb: BlackBoard, device: Device):
        super().__init__(event_time, bb)
        self.device: Device = device
        self.is_initialized = False

    def execute(self, event_time):

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

        # harvest data
        self.device.read_harvest_data(force_verbose=False)

        # check import/export limits
        decoder: SungrowDeeDecoder = self.device.get_dee_decoder()

        decoder.decode(self.device.get_last_harvest_data())

        # check import/export limits every 5 seconds
        if event_time % 5000 == 0:
            logger.info('--------------------------------')
            logger.info(f"State: {state}")
            logger.info(f"Battery power: {battery_power}")
            logger.info(f"Grid power: {decoder.grid_power}")
            logger.info(f"Grid power limit: {decoder.grid_power_limit}")
            logger.info(f"Instantaneous battery power: {decoder.instantaneous_battery_power}")
            logger.info(f"Battery SOC: {decoder.battery_soc}")
            logger.info(f"Battery max charge discharge power: {decoder.battery_max_charge_discharge_power}")
            logger.info(f"Min battery SOC: {decoder.min_battery_soc}")
            logger.info(f"Max battery SOC: {decoder.max_battery_soc}")
            logger.info('--------------------------------')

            battery_power, state = check_import_export_limits(decoder.grid_power,
                                                              decoder.grid_power_limit,
                                                              decoder.instantaneous_battery_power,
                                                              decoder.battery_soc,
                                                              decoder.battery_max_charge_discharge_power,
                                                              decoder.min_battery_soc,
                                                              decoder.max_battery_soc)

        if state == State.DISCHARGE_BATTERY:
            self.device.profile.set_battery_power(self.device, -battery_power)
            bb_message = f"Discharging battery to {battery_power} W to reduce import"
            logger.info(bb_message)
            self.bb.add_warning(bb_message)
        elif state == State.CHARGE_BATTERY:
            self.device.profile.set_battery_power(self.device, battery_power)
            bb_message = f"Charging battery to {battery_power} W to reduce export"
            logger.info(bb_message)
            self.bb.add_warning(bb_message)
        elif state == State.NO_ACTION:
            if self.is_initialized:
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

            return Harvest(event_time, self.bb, self.device, DefaultHarvestTransportFactory())

        self.time = event_time + 500
        return self
