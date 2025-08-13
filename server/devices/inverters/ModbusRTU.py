from typing import Optional
from server.devices.profile_keys import FunctionCodeKey
from .modbus import Modbus
from ..ICom import ICom, HarvestDataType
from pymodbus.client import ModbusSerialClient as ModbusClient
from pymodbus.pdu import ExceptionResponse
from pymodbus.exceptions import ModbusIOException
from server.devices.supported_devices.profile import RegisterInterval
from server.devices.registerValue import RegisterValue
from pymodbus import pymodbus_apply_logging_config
import logging

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

pymodbus_apply_logging_config("INFO")


class ModbusRTU(Modbus):
    """
    ModbusRTU device class

    Attributes:
        port (str): The serial port used for communication.
        baudrate (int): The bits per second.
        bytesize (int): The number of bits per byte (7-8).
        parity (str): The parity ('E'ven, 'O'dd or 'N'one).
        stopbits (float): The number of stop bits (1, 1.5, 2).
        device_type (str): The type of the device (solaredge, huawei or fronius etc...).
        slave_id (int): The Modbus address of the device.
    """

    CONNECTION = "RTU"

    @property
    def PORT(self) -> str:
        return "port"

    @staticmethod
    def port_key() -> str:
        return "port"

    @property
    def BAUD_RATE(self) -> str:
        return self.baud_rate_key()

    @staticmethod
    def baud_rate_key() -> str:
        return "baudrate"

    @property
    def BYTESIZE(self) -> str:
        return self.bytesize_key()

    @staticmethod
    def bytesize_key() -> str:
        return "bytesize"

    @property
    def PARITY(self) -> str:
        return self.parity_key()

    @staticmethod
    def parity_key() -> str:
        return "parity"

    @property
    def STOPBITS(self) -> str:
        return self.stopbits_key()

    @staticmethod
    def stopbits_key() -> str:
        return "stopbits"

    @property
    def DEVICE_TYPE(self) -> str:
        return self.device_type_key()

    @staticmethod
    def device_type_key() -> str:
        return "device_type"

    @property
    def SLAVE_ID(self) -> str:
        return self.slave_id_key()

    @staticmethod
    def slave_id_key() -> str:
        return "slave_id"

    @staticmethod
    def get_supported_devices():
        return []

    @staticmethod
    def get_config_schema():
        return {
            ModbusRTU.baud_rate_key(): "string - baudrate of the device",
            ModbusRTU.bytesize_key(): "string - bytesize of the device",
            ModbusRTU.port_key(): "int - port of the device",
            ModbusRTU.parity_key(): "string - parity of the device",
            ModbusRTU.stopbits_key(): "float - stopbits of the device",
            ModbusRTU.device_type_key(): "string - type of the device",
            ModbusRTU.slave_id_key(): "int - Modbus address of the device",
        }

    def __init__(self, **kwargs) -> None:
        Modbus.__init__(self, **kwargs)

        self.port = kwargs.get(self.port_key(), None)
        self.baudrate = kwargs.get(self.baud_rate_key(), None)
        self.bytesize = kwargs.get(self.bytesize_key(), None)
        self.parity = kwargs.get(self.parity_key(), None)
        self.stopbits = kwargs.get(self.stopbits_key(), None)
        self.slave_id = kwargs.get(self.slave_id_key(), None)
        self.client = None
        self.data_type = HarvestDataType.MODBUS_REGISTERS

    def _connect(self, **kwargs) -> bool:
        self._create_client(**kwargs)

        if not self.client.connect():
            log.error("FAILED to open inverter: %s", self.device_type)
            return False

        if self.sn is None:
            log.info("Reading SN from device")
            # if self.profile.name == "sdm630":
            #     self.sn = "SDM630"
            # else:
            self.sn = self._read_SN()

            if self.sn is None:
                log.error("Failed to read SN from device")
                return False

        self._validate_and_select_profile()

        return self.sn is not None and self.profile.profile_is_valid(self)

    def _get_type(self) -> str:
        return self.device_type

    def _is_open(self) -> bool:
        return bool(self.client) and bool(self.client.socket)

    def _close(self) -> None:
        self.client.close()

    def _disconnect(self) -> None:
        self._close()

    def clone(self, port: str = None) -> 'ModbusRTU':
        config = self.get_config()
        if port:
            config[self.PORT] = port

        return ModbusRTU(**config)

    def get_config(self) -> dict:
        super_config = super().get_config()

        my_config = {
            ICom.CONNECTION_KEY: ModbusRTU.CONNECTION,
            self.PORT: self.port,
            self.BAUD_RATE: self.baudrate,
            self.BYTESIZE: self.bytesize,
            self.PARITY: self.parity,
            self.STOPBITS: self.stopbits,
        }
        return {**super_config, **my_config}

    def _get_connection_type(self) -> str:
        return ModbusRTU.CONNECTION

    def find_device(self) -> 'ICom':
        return self

    def _create_client(self, **kwargs) -> None:
        self.client = ModbusClient(
            method="rtu",
            port=self.port,
            baudrate=self.baudrate,
            bytesize=self.bytesize,
            parity=self.parity,
            stopbits=self.stopbits,
            **kwargs
        )

    def _read_registers(self, function_code: FunctionCodeKey, scan_start, scan_range) -> list:
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
                raise ModbusIOException("Exception occurred while reading registers")

            return resp.registers

    def write_registers(self, starting_register, values) -> bool:
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
            log.debug("Values read from %s %s in the format of [raw, raw, value]: %s, %s, %s", self.device_type, self.sn, a, b, value)

            return value

        except Exception as e:
            log.error(f"Error reading register: {register.start_register}")
            self.disconnect()
            return None

    def compare_host(self, other: ICom) -> bool:
        if isinstance(other, ModbusRTU):
            return self.sn == other.sn
        return False
