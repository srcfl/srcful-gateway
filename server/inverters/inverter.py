from .inverter_types import OPERATION, SCAN_RANGE, SCAN_START
import logging
from pymodbus.pdu import ExceptionResponse
from pymodbus import pymodbus_apply_logging_config
from pymodbus.exceptions import ConnectionException, ModbusException, ModbusIOException

# from .inverter_types import INVERTERS

from .supported_inverters import profiles as p


pymodbus_apply_logging_config("INFO")

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class Inverter:
    """Base class for all inverters."""

    def __init__(self):
        self._isTerminated = False  # this means the inverter is marked for removal it will not react to any requests
        # self.registers = INVERTERS[self.get_type()]
        self.registers = p.get_inverter_profile(self.get_type())['registers']
        print(self.registers)
        print(self.registers)
        print(self.registers)
        print(self.registers)

    def terminate(self):
        """Terminates the inverter."""
        self.close()
        self._isTerminated = True

    def is_terminated(self) -> bool:
        return self._isTerminated
    
    def clone(self):
        """Returns a clone of the inverter. This clone will only have the configuration and not the connection."""
        raise NotImplementedError("Subclass must implement abstract method")

    def get_config(self):
        """Returns the inverter's setup as a tuple."""
        raise NotImplementedError("Subclass must implement abstract method")

    def get_config_dict(self):
        """Returns the inverter's setup as a dictionary."""
        raise NotImplementedError("Subclass must implement abstract method")

    def is_open(self) -> bool:
        """
        Returns True if the inverter is open.
        Reason for checking the socket is because that is that ModbusTcpClient and 
        ModbusSerialClient uses different methods to check if the connection is open, 
        but they both have a socket attribute that is None if the connection is closed, 
        so we use that to check if the connection is open. 

        """
        log.debug("is_open() - Checking if inverter is open")
        return bool(self.client.socket)

    def open(self, **kwargs) -> bool:
        """Opens the Modbus connection to the inverter.

        :param kwargs (optional) parameters to be passed to the _create_client method used for creating specific client types (TCP/RTU etc...)
        
        :return True if the connection is open, otherwise False.
        """
        if not self.is_terminated():
            self.client = self._create_client(**kwargs)
            if not self.client.connect():
                log.error("FAILED to open inverter: %s", self.get_type())
            return bool(self.client.socket)
        else:
            return False

    def _create_client(self, **kwargs):
        """Creates the Modbus client."""
        raise NotImplementedError("Subclass must implement abstract method")

    def get_host(self):
        """Returns the inverter's host IP-address"""
        raise NotImplementedError("Subclass must implement abstract method")

    def get_port(self):
        """Returns the inverter's port number"""
        raise NotImplementedError("Subclass must implement abstract method")

    def get_type(self):
        """Returns the inverter's type"""
        raise NotImplementedError("Subclass must implement abstract method")

    def get_address(self):
        """Returns the inverter's address"""
        raise NotImplementedError("Subclass must implement abstract method")

    def close(self):
        self.client.close()

    def read_harvest_data(self):
        if self.is_terminated():
            raise Exception("readHarvestData() - inverter is terminated")

        regs = []
        vals = []
        print(self.registers)
        print(self.registers)
        print(self.registers)
        print(self.registers)
        print(self.registers)
        for entry in self.registers:
            operation = entry['operation']
            scan_start = entry['scanStart']
            scan_range = entry['scanRange']

            r = self.populate_registers(scan_start, scan_range)

            if operation == 0x03:
                v = self.read_holding_registers(scan_start, scan_range)
            elif operation == 0x04:
                v = self.read_input_registers(scan_start, scan_range)
            regs += r
            vals += v

        # Zip the registers and values together convert them into a dictionary
        res = dict(zip(regs, vals))
        if res:
            return res
        else:
            raise Exception("readHarvestData() - res is empty")

    def populate_registers(self, scan_start, scan_range):
        """
        Populate a list of registers from a start address and a range
        """
        return [x for x in range(scan_start, scan_start + scan_range, 1)]

    def read_input_registers(self, scan_start, scan_range):
        """
        Read a range of input registers from a start address
        """
        registers = []
        try:
            resp = self.client.read_input_registers(scan_start, scan_range, slave=self.get_address())
            
            # Not sure why read_input_registers dose not raise an ModbusIOException but rather returns it
            # We solve this by raising the exception manually
            if isinstance(resp, ModbusIOException):
                raise ModbusIOException("Exception occurred while reading input registers")
             
            log.debug("OK - Reading Input: " + str(scan_start) + "-" + str(scan_range))
            registers = resp.registers

        except ModbusException as me:
        
            # Decide whether to break or continue based on the type of ModbusException
            if isinstance(me, ConnectionException):
                log.error("ConnectionException occurred: %s", str(me))

            if isinstance(me, ModbusIOException):
                log.error("ModbusIOException occurred: %s", str(me))
            
        return registers

    def read_holding_registers(self, scan_start, scan_range):
        """
        Read a range of holding registers from a start address
        """
        registers = []
        try:
            resp = self.client.read_holding_registers(scan_start, scan_range, slave=self.get_address())
            
            # Not sure why read_input_registers dose not raise an ModbusIOException but rather returns it
            # We solve this by raising the exception manually
            if isinstance(resp, ModbusIOException):
                raise ModbusIOException("Exception occurred while reading holding registers")

            log.debug("OK - Reading Holding: " + str(scan_start) + "-" + str(scan_range))
            registers = resp.registers

        except ModbusException as me:

            # Decide whether to break or continue based on the type of ModbusException
            if isinstance(me, ConnectionException):
                log.error("ConnectionException occurred: %s", str(me))

            if isinstance(me, ModbusIOException):
                log.error("ModbusIOException occurred: %s", str(me))

        return registers

    def write_registers(self, starting_register, values):
        """
        Write a range of holding registers from a start address
        """
        resp = self.client.write_registers(
            starting_register, values, slave=self.get_address()
        )
        log.debug(
            "OK - Writing Holdings: " + str(starting_register) + "-" + str(values)
        )
        if isinstance(resp, ExceptionResponse):
            raise Exception("writeRegisters() - ExceptionResponse: " + str(resp))
        return resp
