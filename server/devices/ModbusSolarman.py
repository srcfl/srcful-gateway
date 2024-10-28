from .ModbusTCP import ModbusTCP
from .ICom import ICom
from pysolarmanv5 import PySolarmanV5
from server.network.network_utils import NetworkUtils
import logging


log = logging.getLogger(__name__)
log.setLevel(logging.INFO)



class ModbusSolarman(ModbusTCP):
    """
    ModbusSolarman device class
    
    Attributes:
        ip (str): The IP address or hostname of the device.
        mac (str, optional): The MAC address of the device. Defaults to "00:00:00:00:00:00" if not provided.
        serial (int): The serial number of the logger stick.
        port (int): The port number used for the Modbus connection.
        device_type (str): The type of the device (solaredge, huawei or fronius etc...).
        slave_id (int): The Modbus address of the device, typically used to identify the device on the network.
        verbose (int, optional): The verbosity level of the device. Defaults to 0.
    """
    
    CONNECTION = "SOLARMAN"
    
    @property
    def VERBOSE(self) -> str:
        return self.verbose_key()
    
    @staticmethod
    def verbose_key() -> str:
        return "verbose"
    
    
    @staticmethod
    def get_config_schema():
        schema = ModbusTCP.get_config_schema()
        return {
            **schema,
            ModbusTCP.sn_key(): "int - Serial number of the logger stick",
        }
    
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        
        self.verbose = kwargs.get(self.verbose_key(), 0)

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
        
    def _is_valid(self) -> bool:
        return self.get_SN() is not None

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
            
        args = {
            self.IP: ip,
            self.MAC: self._get_mac(),
            self.SN: self._get_SN(),
            self.PORT: self._get_port(),
            self.DEVICE_TYPE: self._get_type(),
            self.SLAVE_ID: self._get_slave_id(),
            self.VERBOSE: self.verbose
        }
        
        return ModbusSolarman(**args)
    
    def _get_SN(self) -> str:
        return str(self.sn)

    def _get_config_dict(self) -> dict:
        return {
            ICom.CONNECTION_KEY: ModbusSolarman.CONNECTION,
            self.DEVICE_TYPE: self._get_type(),
            self.SN: self._get_SN(),
            self.SLAVE_ID: self._get_slave_id(),
            self.IP: self._get_host(),
            self.MAC: self._get_mac(),
            self.PORT: self._get_port(),
            self.VERBOSE: self.verbose
        }
    
    def _create_client(self, **kwargs) -> None:
        try:
            self.client = PySolarmanV5(address=self._get_host(),
                            serial=self._get_SN(),
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
