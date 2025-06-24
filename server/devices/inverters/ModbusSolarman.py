from typing import Optional
from server.devices.Device import Device
from server.devices.inverters.common import INVERTER_CLIENT_NAME
from .ModbusTCP import ModbusTCP
from ..ICom import ICom
from pysolarmanv5 import PySolarmanV5
from server.network.network_utils import HostInfo, NetworkUtils
import logging
from server.devices.profile_keys import ProtocolKey
from server.devices.supported_devices.profiles import ModbusDeviceProfiles
from server.devices.profile_keys import FunctionCodeKey


log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class ModbusSolarman(ModbusTCP):
    """
    ModbusSolarman device class

    Attributes:
        Required:
            ip (str): The IP address or hostname of the device.
            logger_sn (int): The serial number of the logger stick.
            port (int): The port number used for the Modbus connection.
            device_type (str): The type of the device (solaredge, huawei or fronius etc...).
            slave_id (int): The Modbus address of the device, typically used to identify the device on the network.

        Optional:
            mac (str, optional): The MAC address of the device. Defaults to "00:00:00:00:00:00" if not provided.
            sn (int, optional): The serial number of the inverter.
            verbose (int, optional): The verbosity level of the device. Defaults to 0.
    """

    CONNECTION = "SOLARMAN"

    @staticmethod
    def verbose_key() -> str:
        return "verbose"

    @property
    def VERBOSE(self) -> str:
        return self.verbose_key()

    @staticmethod
    def logger_sn_key() -> str:
        return "logger_sn"

    @property
    def LOGGER_SN(self) -> int:
        return self.logger_sn_key()

    @staticmethod
    def get_supported_devices(verbose: bool = True):
        supported_devices = []
        solarman_devices = [profile for profile in ModbusDeviceProfiles().get_supported_devices() if profile.protocol.value == ProtocolKey.SOLARMAN.value]
        log.info("Getting from ModbusSolarman")

        if verbose:
            for profile in solarman_devices:
                obj = {
                    ModbusTCP.device_type_key(): profile.name,
                    ModbusTCP.MAKER: profile.maker,
                    ModbusTCP.DISPLAY_NAME: profile.display_name,
                    ModbusTCP.PROTOCOL: profile.protocol.value
                }
                supported_devices.append(obj)
        else:
            for profile in solarman_devices:
                obj = {
                    ModbusTCP.MAKER: profile.maker,
                }
                if obj not in supported_devices:
                    supported_devices.append(obj)

        return {ModbusSolarman.CONNECTION: supported_devices}

    @staticmethod
    def get_config_schema():
        return {
            **ModbusTCP.get_config_schema(),
            **Device.get_config_schema(ModbusSolarman.CONNECTION),  # needed to set the correct connection type as ModbuTCP is also a concrete inverter class
            ModbusSolarman.logger_sn_key(): "int - Serial number of the logger stick",
        }

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.logger_sn = kwargs.get(self.logger_sn_key(), None)
        self.verbose = kwargs.get(self.verbose_key(), 0)

    def _connect(self, **kwargs) -> bool:

        self._create_client(**kwargs)

        try:
            if not self.client.sock:
                log.error("FAILED to open inverter: %s", self.get_config())
                return False
            if self.client.sock:
                self.mac = NetworkUtils.get_mac_from_ip(self.ip)
        except Exception as e:
            log.error("Error opening inverter: %s", self.get_config())
            return False

        if self.sn is None:
            self.sn = self._read_SN()

        return bool(self.client.sock) and self.sn is not None

    def _is_open(self) -> bool:
        try:
            return bool(self.client and self.client.sock)
        except Exception as e:
            log.error("Error checking if inverter is open: %s", self._get_type())
            log.error(e)
            return False

    def _close(self) -> None:
        try:
            self.client.disconnect()
            self.client.sock = None
            log.info("Closing client ModbusTCP %s with logger SN %s", self.mac, self.sn)
        except Exception as e:
            log.error("Close -> Error disconnecting inverter: %s", self._get_type())
            log.error(e)

    def _disconnect(self) -> None:
        self._close()
        self._isTerminated = True

    def clone(self, ip: str = None) -> 'ModbusSolarman':
        config = self.get_config()
        if ip:
            config[self.IP] = ip

        return ModbusSolarman(**config)

    def get_SN(self) -> str:
        return self.sn

    def get_logger_SN(self) -> str:
        return str(self.logger_sn)

    def get_client_name(self) -> str:
        return INVERTER_CLIENT_NAME + ".solarman." + self.get_name().lower()

    def get_config(self) -> dict:
        super_config = super().get_config()

        my_config = {
            self.LOGGER_SN: self.logger_sn,
            self.VERBOSE: self.verbose
        }

        return {**super_config, **my_config}

    def _get_connection_type(self) -> str:
        return ModbusSolarman.CONNECTION

    def _create_client(self, **kwargs) -> None:
        try:
            self.client = PySolarmanV5(address=self.ip,
                                       serial=self.logger_sn,
                                       port=self.port,
                                       mb_slave_id=self.slave_id,
                                       v5_error_correction=False,
                                       verbose=self.verbose,
                                       **kwargs)
        except Exception as e:
            log.error("Error creating client: %s", e)

    def _read_registers(self, function_code: FunctionCodeKey, scan_start: int, scan_range: int) -> list:
        resp = None

        with self._lock:
            if function_code == FunctionCodeKey.READ_INPUT_REGISTERS:
                resp = self.client.read_input_registers(register_addr=scan_start, quantity=scan_range)
            elif function_code == FunctionCodeKey.READ_HOLDING_REGISTERS:
                resp = self.client.read_holding_registers(register_addr=scan_start, quantity=scan_range)

            return resp

    def write_registers(self, starting_register: int, values: list) -> bool:
        with self._lock:
            try:
                self.client.write_multiple_holding_registers(starting_register, values)
                log.debug("OK - Writing Holdings: %s - %s", str(starting_register),  str(values))
                return True
            except Exception as e:
                log.error("Error writing registers: %s", e)
                return False

    def _clone_with_host(self, host: HostInfo) -> Optional[ICom]:

        if host.mac != self.mac:
            return None

        config = self.get_config()
        config[self.IP] = host.ip
        return ModbusSolarman(**config)
