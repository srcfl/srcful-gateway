from abc import ABC, abstractmethod
import logging
from pymodbus.exceptions import ConnectionException, ModbusException, ModbusIOException

from server.devices.Device import Device
from .supported_inverters.profiles import InverterProfiles, InverterProfile
from .ICom import ICom
from server.network.network_utils import NetworkUtils

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


    def __init__(self, device_type: str):
        super().__init__()
        self.device_type = device_type
        self.profile: InverterProfile = InverterProfiles().get(self.device_type)
    
    def _read_harvest_data(self, force_verbose) -> dict:
        regs = []
        vals = []

        registers = []

        if force_verbose or self.profile.verbose_always:
            registers = self.profile.get_registers_verbose()
        else:
            registers = self.profile.get_registers()
        
        for entry in registers:
            operation = entry.operation
            scan_start = entry.start_register
            scan_range = entry.offset

            r = self._populate_registers(scan_start, scan_range)
            # log.debug("OK - Populating Registers: %s", str(r))
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

    def _populate_registers(self, scan_start, scan_range) -> list:
        """
        Populate a list of registers from a start address and a range
        """
        return [x for x in range(scan_start, scan_start + scan_range, 1)]
    
    @abstractmethod
    def _read_registers(self, operation, scan_start, scan_range) -> list:
        """Reads a range of registers from a start address."""
        pass

    def read_registers(self, operation, scan_start, scan_range) -> list:
        """
        Read a range of input registers from a start address
        """
        resp = []
        
        try:
            resp = self._read_registers(operation, scan_start, scan_range)
            logger.debug("OK - Reading: %s - %s", str(scan_start), str(scan_range))

        except ModbusException as me:
            # Decide whether to break or continue based on the type of ModbusException
            if isinstance(me, ConnectionException):
                logger.error("ConnectionException occurred: %s", str(me))
                
            if isinstance(me, ModbusIOException):
                logger.error("ModbusIOException occurred: %s", str(me))

        return resp

    # ICom methods
    def is_valid(self) -> bool:
        """
        Check if the device is valid by checking if the MAC address is not 00:00:00:00:00:00,
        this is a simple check to make sure the device is on the local network. 
        More sophisticated checks may be added later.
        """
        # Ensure that the device is on the local network
        # There can be other checks to make sure the device is valid, but this is a good start.
        if self.get_config()[NetworkUtils.MAC_KEY] == "00:00:00:00:00:00":
            return False
        return True
    
    def get_harvest_data_type(self) -> str:
        return self.data_type
    
    def get_name(self) -> str:
        return self.profile.name
    
    def find_device(self) -> 'ICom':
        
        port = self.get_config()[NetworkUtils.PORT_KEY] # get the port from the previous inverter config
        hosts = NetworkUtils.get_hosts([int(port)], 0.01)
        
        if len(hosts) > 0:
            for host in hosts:
                if host[NetworkUtils.MAC_KEY] == self.get_config()[NetworkUtils.MAC_KEY]:
                    return self.clone(host[NetworkUtils.IP_KEY])
        return None
    
    def get_config(self) -> dict:
        return {self.DEVICE_TYPE: self.device_type}

