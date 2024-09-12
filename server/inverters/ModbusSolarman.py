from .modbus import Modbus
from .ICom import ICom, HarvestDataType
from pysolarmanv5 import PySolarmanV5
from typing_extensions import TypeAlias
import logging


log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)



class ModbusSolarman(Modbus):
    """
    ip: string, IP address of the inverter,
    serial: int, Serial number of the logger stick,
    port: int, Port of the inverter,
    type: string, solaredge, huawei or fronius etc...,
    address: int, Modbus address of the inverter
    verbose: int, 0 or 1 for verbose logging

    """

    CONNECTION = "SOLARMAN"

    @staticmethod
    def list_to_tuple(config: list) -> tuple:
        assert config[ICom.CONNECTION_IX] == ModbusSolarman.CONNECTION, "Invalid connection type"
        ip = config[1]
        serial = int(config[2])
        port = int(config[3])
        inverter_type = config[4]
        slave_id = int(config[5])
        verbose = False
        return (config[0], ip, serial, port, inverter_type, slave_id, verbose)
    
    @staticmethod
    def dict_to_tuple(config: dict) -> tuple:
        assert config[ICom.CONNECTION_KEY] == ModbusSolarman.CONNECTION, "Invalid connection type"
        ip = config["host"]
        serial = int(config["serial"])
        port = int(config["port"])
        inverter_type = config["type"]
        slave_id = int(config["address"])
        verbose = False
        return (config[ICom.CONNECTION_KEY], ip, serial, port, inverter_type, slave_id, verbose)
    

    # Address, Serial, Port, type, Slave_ID, verbose 
    Setup: TypeAlias = tuple[str | bytes | bytearray, int, int, str, int, int]

    def __init__(self, setup: Setup) -> None:
        log.info("Creating with: %s" % str(setup))
        self.setup = setup
        self.client = None
        self.data_type = HarvestDataType.MODBUS_REGISTERS.value
        super().__init__()

    def _open(self, **kwargs) -> bool:
        if not self._is_terminated():
            try:
                self._create_client(**kwargs)
                if not self.client.sock:
                    log.error("FAILED to open inverter: %s", self._get_type())
                return bool(self.client.sock)
            except Exception as e:
                log.error("Error opening inverter: %s", self._get_type())
                log.error(e)
                return False
        else:
            return False

    def _is_open(self) -> bool:
        try:
            return bool(self.client.sock)
        except Exception as e:
            log.error("Error checking if inverter is open: %s", self._get_type())
            log.error(e)
            return False

    def _close(self) -> None:
        try:
            self.client.disconnect()
            self.client.sock = None
            log.info("Close -> Inverter disconnected successfully: %s", self._get_type())
        except Exception as e:
            log.error("Close -> Error disconnecting inverter: %s", self._get_type())
            log.error(e)

    def _terminate(self) -> None:
        self._close()
        self._isTerminated = True

    def _is_terminated(self) -> bool:
        return self._isTerminated

    def _clone(self, host: str = None) -> 'ModbusSolarman':
        if host is None:
            host = self._get_host()

        return ModbusSolarman(
            (host, 
             self._get_serial(), 
             self._get_port(), 
             self._get_type(), 
             self._get_address(), 
             self.setup[5])
        )

    def _get_host(self) -> str:
        return self.setup[0]

    def _get_serial(self) -> int:
        return self.setup[1]
    
    def _get_port(self) -> int:
        return self.setup[2]

    def _get_type(self) -> str:
        return self.setup[3].lower()
    
    def _get_address(self) -> int:
        return self.setup[4]

    def _get_config(self) -> tuple[str, str, int, str, int]:
        return (
            ModbusSolarman.CONNECTION,
            self._get_host(),
            self._get_serial(),
            self._get_port(),
            self._get_type(),
            self._get_address(),
        )

    def _get_config_dict(self) -> dict:
        return {
            ICom.CONNECTION_KEY: "SOLARMAN",
            "type": self._get_type(),
            "serial": self._get_serial(),
            "address": self._get_address(),
            "host": self._get_host(),
            "port": self._get_port(),
        }
    
    def _create_client(self, **kwargs) -> None:
        try:
            self.client = PySolarmanV5(address=self._get_host(), 
                            serial=self._get_serial(), 
                            port=self._get_port(), 
                            mb_slave_id=self._get_address(), 
                            v5_error_correction=False,
                            verbose=self.setup[5],
                            **kwargs)
        except Exception as e:
            log.error("Error creating client: %s", e)

    def _read_registers(self, operation, scan_start, scan_range) -> list:
        resp = None

        if operation == 0x04:
            resp = self.client.read_input_registers(register_addr=scan_start, quantity=scan_range)
        elif operation == 0x03:
            resp = self.client.read_holding_registers(register_addr=scan_start, quantity=scan_range)

        return resp

    def write_register(self, operation, register, value) -> bool:
        raise NotImplementedError("Not implemented yet")
