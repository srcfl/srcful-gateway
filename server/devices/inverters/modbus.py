from abc import ABC, abstractmethod
import logging
from pymodbus.exceptions import ConnectionException, ModbusException, ModbusIOException
from server.devices.Device import Device
from server.devices.inverters.common import INVERTER_CLIENT_NAME
from ..ICom import HarvestDataType
from ..supported_devices.profiles import ModbusDeviceProfiles, ModbusProfile
from server.devices.profile_keys import FunctionCodeKey

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Modbus(Device, ABC):
    """Base class for all inverters."""

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
    
    @property
    def SN(self) -> str:
        return "sn"
    
    @staticmethod
    def sn_key() -> str:
        return "sn"


    def __init__(self, **kwargs) -> None:
        if "address" in kwargs:
            kwargs[self.SLAVE_ID] = kwargs.pop("address")
        if "type" in kwargs:
            kwargs[self.DEVICE_TYPE] = kwargs.pop("type")
        
        self.sn = kwargs.get(self.SN, None)
        self.slave_id = kwargs.get(self.SLAVE_ID, None)
        self.device_type = kwargs.get(self.DEVICE_TYPE, None)
        
        logger.debug("Device Type: %s", str(self.device_type))

        if self.device_type:
            self.device_type = self.device_type.lower()
            self.profile: ModbusProfile = ModbusDeviceProfiles().get(self.device_type)
    
    def _read_harvest_data(self, force_verbose: bool) -> dict:
        regs = []
        vals = []

        registers = []
    
        if force_verbose or self.profile.verbose_always:
            registers = self.profile.get_registers_verbose()
        else:
            registers = self.profile.get_registers()
            
        for entry in registers:
            operation = entry.function_code
            scan_start = entry.start_register
            scan_range = entry.offset

            r = self._populate_registers(scan_start, scan_range)
            v = self.read_registers(operation, scan_start, scan_range)
                        
            regs += r
            vals += v

        # Zip the registers and values together convert them into a dictionary
        res = dict(zip(regs, vals))

        logger.debug("OK - Reading Harvest Data: %s", str(res))

        if res:
            return res
        else:
            raise Exception("readHarvestData() - res is empty")

    def _populate_registers(self, scan_start: int, scan_range: int) -> list:
        """
        Populate a list of registers from a start address and a range
        """
        return [x for x in range(scan_start, scan_start + scan_range, 1)]
    
    @abstractmethod
    def _read_registers(self, function_code: FunctionCodeKey, scan_start: int, scan_range: int) -> list:
        """Reads a range of registers from a start address."""
        pass

    def read_registers(self, function_code:FunctionCodeKey, scan_start: int, scan_range: int) -> list:
        """
        Read a range of input registers from a start address
        """
        resp = []
        
        try:
            resp = self._read_registers(function_code, scan_start, scan_range)
            logger.debug("OK - Reading %s: %s - %s", self.device_type, str(scan_start), str(scan_range))

        except ModbusException as me:
            # Decide whether to break or continue based on the type of ModbusException
            if isinstance(me, ConnectionException):
                logger.error(str(me))
                
            if isinstance(me, ModbusIOException):
                logger.error(str(me))

        return resp
    
    def get_harvest_data_type(self) -> HarvestDataType:
        return self.data_type
    
    def get_name(self) -> str:
        return self.profile.name
    
    def get_client_name(self) -> str:
        return INVERTER_CLIENT_NAME + "." + self.get_name().lower()
    
    def get_config(self) -> dict:
        return {
            self.DEVICE_TYPE: self.device_type,
            self.SLAVE_ID: self.slave_id,
            self.SN: self.get_SN()
        }

