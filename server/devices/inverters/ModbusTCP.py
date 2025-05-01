from typing import Optional
from server.devices.TCPDevice import TCPDevice
from server.devices.profile_keys import FunctionCodeKey
from .modbus import Modbus
from ..ICom import ICom, HarvestDataType
from pymodbus.client import ModbusTcpClient as ModbusClient
from pymodbus.exceptions import ModbusIOException
from pymodbus.pdu import ExceptionResponse
from pymodbus import pymodbus_apply_logging_config
from server.network.network_utils import HostInfo, NetworkUtils
from server.devices.supported_devices.profiles import ModbusDeviceProfiles, ModbusProfile, RegisterInterval
import logging
from server.devices.profile_keys import ProtocolKey
from server.devices.registerValue import RegisterValue
import time
import threading


log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

pymodbus_apply_logging_config("INFO")


class ModbusTCP(Modbus, TCPDevice):
    """
    ModbusTCP device class.

    Attributes:
        ip (str): The IP address or hostname of the device.
        mac (str, optional): The MAC address of the device. Defaults to "00:00:00:00:00:00" if not provided.
        port (int): The port number used for the Modbus connection.
        device_type (str): The type of the device (e.g., solaredge, huawei, fronius).
        slave_id (int): The Modbus address of the device, typically used to identify the device on the network.
    """

    CONNECTION = "TCP"
    _lock = threading.Lock()

    @staticmethod
    def ip_key() -> str:
        return "ip"

    @property
    def MAC(self) -> str:
        return self.mac_key()

    @staticmethod
    def mac_key() -> str:
        return "mac"

    @staticmethod
    def port_key() -> str:
        return "port"

    @staticmethod
    def get_supported_devices(verbose: bool = True):
        supported_devices = []
        modbus_devices = [profile for profile in ModbusDeviceProfiles().get_supported_devices() if profile.protocol.value == ProtocolKey.MODBUS.value]
        log.info("Getting from ModbusTCP")

        if verbose:
            for profile in modbus_devices:
                obj = {
                    ModbusTCP.device_type_key(): profile.name,
                    ModbusTCP.MAKER: profile.maker,
                    ModbusTCP.DISPLAY_NAME: profile.display_name,
                    ModbusTCP.PROTOCOL: profile.protocol.value
                }
                supported_devices.append(obj)
        else:
            for profile in modbus_devices:
                obj = {
                    ModbusTCP.MAKER: profile.maker,
                }

                if obj not in supported_devices and profile.maker != "Unknown":
                    supported_devices.append(obj)

        return {ModbusTCP.CONNECTION: supported_devices}

    @staticmethod
    def get_config_schema():
        return {
            **Modbus.get_config_schema(ModbusTCP.CONNECTION),
            ModbusTCP.mac_key(): "string - (Optional) MAC address of the device",
            ModbusTCP.device_type_key(): "string - type of the device",
            ModbusTCP.slave_id_key(): "int - Modbus address of the device",
        }

    # init but with kwargs
    def __init__(self, **kwargs) -> None:
        Modbus.__init__(self, **kwargs)

        # check if old keys are provided
        if "host" in kwargs:
            kwargs[self.ip_key()] = kwargs.pop("host")

        # get the kwargs, and default if not provided
        ip = kwargs.get(self.ip_key(), None)
        port = kwargs.get(self.port_key(), None)
        TCPDevice.__init__(self, ip, port)

        self.mac = kwargs.get(self.mac_key(), NetworkUtils.INVALID_MAC)
        self.client = None
        self.data_type = HarvestDataType.MODBUS_REGISTERS

    def _connect(self, **kwargs) -> bool:
        self._create_client(**kwargs)

        if not self.client.connect():
            log.error("FAILED to open Modbus TCP device: %s", self._get_type())
            return False

        # If the socket is open, we can get the MAC address from the ARP table
        if self.client.socket:
            self.mac = NetworkUtils.get_mac_from_ip(self.ip)

        # A short delay is necessary for some devices before a new connection can be established
        time.sleep(1)

        # If the serial number is not set, or if its set to the MAC address (for version < 0.18.16), read the serial number from the device
        if self.sn is None or self.sn == self.mac:
            log.info("Reading SN from device")
            self.sn = self._read_SN()

        # Special case for devices that does not have SN register defined in the profile
        # We also check if the frequency is valid if no serial number can be retrieved
        if self.sn is None and self._has_valid_frequency():
            log.info("Setting SN to MAC because SN register is not defined but frequency is valid")
            self.sn = self.mac

        return bool(self.client.socket) and self.mac != NetworkUtils.INVALID_MAC and self.sn is not None

    def _get_type(self) -> str:
        return self.device_type

    def _is_open(self) -> bool:
        return bool(self.client) and bool(self.client.socket)

    def _close(self) -> None:
        log.info("Closing client ModbusTCP %s", self.mac)
        self.client.close()

    def _disconnect(self) -> None:
        self._close()

    def clone(self, ip: str | None = None) -> 'ModbusTCP':
        config = self.get_config()
        if ip:
            config[self.IP] = ip

        return ModbusTCP(**config)

    def get_config(self) -> dict:

        return {
            **Modbus.get_config(self),
            **TCPDevice.get_config(self),
            self.MAC: self.mac,
        }

    def _get_connection_type(self) -> str:
        return ModbusTCP.CONNECTION

    def get_SN(self) -> str:
        return self.sn

    def _create_client(self, **kwargs) -> None:
        self.client = ModbusClient(host=self.ip, port=self.port, unit_id=self.slave_id, **kwargs)

    def _read_registers(self, function_code: FunctionCodeKey, scan_start: int, scan_range: int) -> list:
        resp = None

        with self._lock:
            if function_code == FunctionCodeKey.READ_INPUT_REGISTERS:
                log.debug(f"Reading input registers - Start: {scan_start}, Range: {scan_range}, Slave ID: {self.slave_id}")
                resp = self.client.read_input_registers(scan_start, scan_range, slave=self.slave_id)
            elif function_code == FunctionCodeKey.READ_HOLDING_REGISTERS:
                log.debug(f"Reading holding registers - Start: {scan_start}, Range: {scan_range}, Slave ID: {self.slave_id}")
                resp = self.client.read_holding_registers(scan_start, scan_range, slave=self.slave_id)

            # Not sure why read_input_registers dose not raise an ModbusIOException but rather returns it
            # We solve this by raising the exception manually
            if isinstance(resp, ModbusIOException):
                raise ModbusIOException(f"ModbusIOException occurred while reading registers: {resp.message}")

            return resp.registers

    def write_registers(self, starting_register: int, values: list) -> bool:
        """
        Write a range of holding registers from a start address
        """
        with self._lock:
            try:
                resp = self.client.write_registers(
                    starting_register, values, slave=self.slave_id
                )

                if isinstance(resp, ExceptionResponse):
                    return False

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
        return ModbusTCP(**config)

    def _read_value(self, register: RegisterInterval) -> Optional[float]:
        """Read a value from a register using the device profile's register"""

        try:
            # Create RegisterValue for frequency reading
            reg_value = RegisterValue(
                address=register.start_register,
                size=register.offset,
                function_code=register.function_code,
                data_type=register.data_type,
                scale_factor=register.scale_factor,
                endianness=register.endianness
            )

            # Read and interpret value
            a, b, value = reg_value.read_value(self)
            log.debug("Values read in the format of [raw, raw, value]: %s, %s, %s", a, b, value)

            return value

        except Exception as e:
            log.error(f"Error reading register: {register.start_register}")
            self.disconnect()
            return None

    def _get_frequency_register(self) -> Optional[RegisterInterval]:
        profile: ModbusProfile = ModbusDeviceProfiles().get(name=self.device_type)
        if not profile or not profile.registers:
            return None
        return profile.registers[0]

    def _get_SN_register(self) -> Optional[RegisterInterval]:
        profile: ModbusProfile = ModbusDeviceProfiles().get(name=self.device_type)
        if not profile or not profile.sn:
            return None
        return profile.sn

    def _has_valid_frequency(self) -> bool:
        """Check if the float frequency value is within a reasonable range (48-62 Hz)"""
        frequency = self._read_value(self._get_frequency_register())
        return frequency and 48.0 <= frequency <= 62.0

    def _read_SN(self) -> Optional[str]:
        """Read serial number using the device profile's serial number register"""

        reg: RegisterInterval = self._get_SN_register()

        if not reg:
            return None

        value = self._read_value(reg)

        if not value:
            return None

        if value and isinstance(value, str):
            # Remove null bytes and any non-printable characters
            cleaned_sn = ''.join(char for char in value if char.isprintable())
            cleaned_sn = cleaned_sn.strip()
            value = cleaned_sn

        log.info("SN: %s", value)

        return str(value)
