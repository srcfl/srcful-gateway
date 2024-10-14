from .modbus import Modbus
from .ICom import ICom, HarvestDataType
from pysolarmanv5 import PySolarmanV5
import logging


log = logging.getLogger(__name__)
log.setLevel(logging.INFO)



class ModbusSolarman(Modbus):
    """
    ip: string, IP address of the inverter,
    mac: string, MAC address of the inverter,
    serial: int, Serial number of the logger stick,
    port: int, Port of the inverter,
    type: string, solaredge, huawei or fronius etc...,
    address: int, Modbus address of the inverter
    verbose: int, 0 or 1 for verbose logging
    """

    CONNECTION = "SOLARMAN"
    
    @property
    def IP(self) -> str:
        return "ip"

    @property
    def MAC(self) -> str:
        return "mac"
    
    @property
    def SERIAL(self) -> int:
        return "serial"
    
    @property
    def PORT(self) -> int:
        return "port"
    
    @property
    def DEVICE_TYPE(self) -> str:
        return "device_type"
    
    @property
    def SLAVE_ID(self) -> int:
        return "slave_id"
    
    @property
    def VERBOSE(self) -> int:
        return "verbose"

    @staticmethod
    def list_to_tuple(config: list) -> tuple:
        assert config[ICom.CONNECTION_IX] == ModbusSolarman.CONNECTION, "Invalid connection type"
        ip = config[1]
        mac = config[2]
        serial = int(config[3])
        port = int(config[4])
        device_type = config[5]
        slave_id = int(config[6])
        verbose = False
        return (config[0], ip, mac, serial, port, device_type, slave_id, verbose)
    
    @staticmethod
    def dict_to_tuple(config: dict) -> tuple:
        assert config[ICom.CONNECTION_KEY] == ModbusSolarman.CONNECTION, "Invalid connection type"
        ip = config["host"]
        mac = config["mac"]
        serial = int(config["serial"])
        port = int(config["port"])
        device_type = config["type"]
        slave_id = int(config["address"])
        verbose = False
        return (config[ICom.CONNECTION_KEY], ip, mac, serial, port, device_type, slave_id, verbose)

    def __init__(self, 
                 ip: str = None, 
                 mac: str = None, 
                 serial: int = None, 
                 port: int = None, 
                 device_type: str = None, 
                 slave_id: int = None, 
                 verbose: int = None) -> None:
        log.info("Creating with: %s %s %s %s %s %s %s" % (ip, mac, serial, port, device_type, slave_id, verbose))
        self.ip = ip
        self.mac = mac
        self.serial = serial
        self.port = port
        self.device_type = device_type
        self.slave_id = slave_id
        self.verbose = verbose
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

    def _clone(self, ip: str = None) -> 'ModbusSolarman':
        if ip is None:
            ip = self._get_host()

        return ModbusSolarman(
            ip, 
            self._get_mac(),
            self._get_serial(),
            self._get_port(), 
            self._get_type(), 
            self._get_address(), 
            self.verbose
        )

    def _get_host(self) -> str:
        return self.ip
    
    def _get_mac(self) -> str:
        return self.mac

    def _get_serial(self) -> int:
        return self.serial
    
    def _get_port(self) -> int:
        return self.port

    def _get_type(self) -> str:
        return self.device_type.lower()
    
    def _get_address(self) -> int:
        return self.slave_id

    def _get_config(self) -> tuple[str, str, str, int, int, str, int, int]:
        return (
            ModbusSolarman.CONNECTION,
            self._get_host(),
            self._get_mac(),
            self._get_serial(),
            self._get_port(),
            self._get_type(),
            self._get_address(),
            self.verbose
        )

    def _get_config_dict(self) -> dict:
        return {
            ICom.CONNECTION_KEY: "SOLARMAN",
            self.DEVICE_TYPE: self._get_type(),
            self.SERIAL: self._get_serial(),
            self.SLAVE_ID: self._get_address(),
            self.IP: self._get_host(),
            self.MAC: self._get_mac(),
            self.PORT: self._get_port(),
            self.VERBOSE: self.verbose
        }
    
    def _create_client(self, **kwargs) -> None:
        try:
            self.client = PySolarmanV5(address=self._get_host(),
                            serial=self._get_serial(),
                            port=self._get_port(),
                            mb_slave_id=self._get_address(),
                            v5_error_correction=False,
                            verbose=self.verbose,
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
