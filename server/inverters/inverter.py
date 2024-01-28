from .inverter_types import OPERATION, SCAN_RANGE, SCAN_START
import logging
from pymodbus.pdu import ExceptionResponse
from pymodbus import pymodbus_apply_logging_config

from .inverter_types import INVERTERS

pymodbus_apply_logging_config("INFO")

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class Inverter:
    """Base class for all inverters."""

    def __init__(self):
        self._isTerminated = False  # this means the inverter is marked for removal it will not react to any requests
        self.inverterIsOpen = False
        self.registers = INVERTERS[self.get_type()]
        pass

    def terminate(self):
        """Terminates the inverter."""
        self.close()
        self._isTerminated = True

    def is_terminated(self) -> bool:
        return self._isTerminated

    def get_config(self):
        """Returns the inverter's setup as a tuple."""
        raise NotImplementedError("Subclass must implement abstract method")

    def get_config_dict(self):
        """Returns the inverter's setup as a dictionary."""
        raise NotImplementedError("Subclass must implement abstract method")

    def is_open(self) -> bool:
        return self.inverterIsOpen

    def open(self) -> bool:
        """Opens the Modbus connection to the inverter."""
        if not self.is_terminated():
            self.client = self._create_client()
            if self.client.connect():
                self.inverterIsOpen = True
            else:
                self.terminate()
                self.inverterIsOpen = False
            return self.inverterIsOpen
        else:
            return False

    def _create_client(self):
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

        for entry in self.registers:
            operation = entry[OPERATION]
            scan_start = entry[SCAN_START]
            scan_range = entry[SCAN_RANGE]

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
        slave = self.get_address()
        resp = self.client.read_input_registers(scan_start, scan_range, slave=slave)
        log.debug("OK - Reading Input: " + str(scan_start) + "-" + str(scan_range))
        if isinstance(resp, ExceptionResponse):
            raise Exception("readInputRegisters() - ExceptionResponse: " + str(resp))
        return resp.registers

    def read_holding_registers(self, scan_start, scan_range):
        """
        Read a range of holding registers from a start address
        """
        resp = self.client.read_holding_registers(
            scan_start, scan_range, slave=self.get_address()
        )
        log.debug("OK - Reading Holding: " + str(scan_start) + "-" + str(scan_range))
        if isinstance(resp, ExceptionResponse):
            raise Exception("readHoldingRegisters() - ExceptionResponse: " + str(resp))
        return resp.registers

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
