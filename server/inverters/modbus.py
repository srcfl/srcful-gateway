import logging
from pymodbus.exceptions import ConnectionException, ModbusException, ModbusIOException
from .supported_inverters.profiles import InverterProfiles, InverterProfile
from .ICom import ICom

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class Modbus(ICom):
    """Base class for all inverters."""

    def __init__(self):
        self._isTerminated = False  # this means the inverter is marked for removal it will not react to any requests
        self.profile: InverterProfile = InverterProfiles().get(self._get_type())
        
    def _get_type(self) -> str:
        """Returns the inverter's type."""
        raise NotImplementedError("Subclass must implement abstract method")

    def _open(self) -> bool:
        """Opens the Modbus connection."""
        raise NotImplementedError("Subclass must implement abstract method")

    def _is_open(self) -> bool:
        """
        Returns True if the inverter is open.
        Reason for checking the socket is because that is that ModbusTcpClient and 
        ModbusSerialClient uses different methods to check if the connection is open, 
        but they both have a socket attribute that is None if the connection is closed, 
        so we use that to check if the connection is open.
        """
        raise NotImplementedError("Subclass must implement abstract method")

    def _close(self) -> None:
        """Closes the Modbus connection."""
        raise NotImplementedError("Subclass must implement abstract method")

    def _terminate(self) -> None:
        """Terminates the inverter."""
        raise NotImplementedError("Subclass must implement abstract method")
    
    def _is_terminated(self) -> bool:
        """Returns True if the inverter is terminated."""
        raise NotImplementedError("Subclass must implement abstract method")

    def _clone(self, host: str):
        """Returns a clone of the inverter. This clone will only have the configuration and not the connection."""
        raise NotImplementedError("Subclass must implement abstract method")

    def _get_config(self) -> tuple:
        """Returns the inverter's setup as a tuple."""
        raise NotImplementedError("Subclass must implement abstract method")

    def _get_config_dict(self) -> dict:
        """Returns the inverter's setup as a dictionary."""
        raise NotImplementedError("Subclass must implement abstract method")

    def _create_client(self, **kwargs) -> None:
        """Creates the Modbus client."""
        raise NotImplementedError("Subclass must implement abstract method")

    def _get_backend_type(self) -> str:
        """Returns the inverter's backend type"""
        raise NotImplementedError("Subclass must implement abstract method")

    def _read_harvest_data(self, force_verbose) -> dict:
        if self._is_terminated():
            raise Exception("readHarvestData() - inverter is terminated")

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

        log.debug("OK - Reading Harvest Data: %s", str(res))

        if res:
            return res
        else:
            raise Exception("readHarvestData() - res is empty")

    def _populate_registers(self, scan_start, scan_range) -> list:
        """
        Populate a list of registers from a start address and a range
        """
        return [x for x in range(scan_start, scan_start + scan_range, 1)]
    
    def _read_registers(self) -> list:
        """Reads a range of registers from a start address."""
        raise NotImplementedError("Subclass must implement abstract method")

    def read_registers(self, operation, scan_start, scan_range) -> list:
        """
        Read a range of input registers from a start address
        """
        resp = []
        
        try:
            resp = self._read_registers(operation, scan_start, scan_range)
            log.debug("OK - Reading: %s - %s", str(scan_start), str(scan_range))

        except ModbusException as me:
            # Decide whether to break or continue based on the type of ModbusException
            if isinstance(me, ConnectionException):
                log.error("ConnectionException occurred: %s", str(me))
                
            if isinstance(me, ModbusIOException):
                log.error("ModbusIOException occurred: %s", str(me))

        return resp

    def write_registers(self) -> bool:
        """Writes a range of registers from a start address."""
        raise NotImplementedError("Subclass must implement abstract method")

    # ICom methods
    
    def connect(self) -> bool:
        return self._open()
    
    def disconnect(self) -> None:
        return self._terminate()
    
    def reconnect(self) -> bool:
        return self._close() and self._open()
    
    def is_open(self) -> bool:
        return self._is_open()
    
    def read_harvest_data(self, force_verbose) -> dict:
        return self._read_harvest_data(force_verbose)
    
    def get_harvest_data_type(self) -> str:
        return self.data_type
    
    def get_config(self) -> dict:
        return self._get_config_dict()
    
    def get_profile(self) -> InverterProfile:
        return self.profile
    
    def clone(self, host: str = None) -> 'ICom':
        return self._clone(host)