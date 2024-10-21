from .ModbusTCP import ModbusTCP
from .ICom import ICom
from pysolarmanv5 import PySolarmanV5
from server.network.network_utils import NetworkUtils
import logging


log = logging.getLogger(__name__)
log.setLevel(logging.INFO)



class ModbusSolarman(ModbusTCP):
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
    def SERIAL(self) -> str:
        return self.serial_key()
    
    @staticmethod
    def serial_key() -> str:
        return "serial"
    
    def VERBOSE(self) -> str:
        return self.verbose_key()
    
    @staticmethod
    def verbose_key() -> str:
        return "verbose"
    
    
    @staticmethod
    def get_config_schema():
        return {
            ModbusTCP.ip_key(): "string, IP address or hostname of the device",
            ModbusSolarman.serial_key(): "int, Serial number of the logger stick",
            ModbusTCP.mac_key(): "string, MAC address of the device",
            ModbusTCP.port_key(): "int, port of the device",
            ModbusTCP.device_type_key(): "string, type of the device",
            ModbusTCP.slave_id_key(): "int, Modbus address of the device",
        }
    

    def __init__(self, 
                 ip: str = None, 
                 mac: str = None, 
                 serial: int = None, 
                 port: int = None, 
                 device_type: str = None, 
                 slave_id: int = None, 
                 verbose: int = None) -> None:
        log.info("Creating with: %s %s %s %s %s %s %s" % (ip, mac, serial, port, device_type, slave_id, verbose))
        super().__init__(ip, mac, port, device_type, slave_id)
        self.serial = serial
        self.verbose = verbose

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
            return bool(self.client and self.client.sock)
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
            self._get_slave_id(), 
            self.verbose
        )


    def _get_serial(self) -> int:
        return self.serial
    
    
    def _get_SN(self) -> str:
        return str(self.serial)

    def _get_config_dict(self) -> dict:
        return {
            ICom.CONNECTION_KEY: "SOLARMAN",
            self.DEVICE_TYPE: self._get_type(),
            self.SERIAL: self._get_serial(),
            self.SLAVE_ID: self._get_slave_id(),
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
                            mb_slave_id=self._get_slave_id(),
                            v5_error_correction=False,
                            verbose=self.verbose,
                            **kwargs)
            self.mac = NetworkUtils.get_mac_from_ip(self._get_host())
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
