from .modbus import Modbus
from .ICom import ICom, HarvestDataType
from pymodbus.client import ModbusTcpClient as ModbusClient
from pymodbus.exceptions import ModbusIOException
from pymodbus.pdu import ExceptionResponse
from pymodbus import pymodbus_apply_logging_config
from server.network.network_utils import NetworkUtils
import logging


log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

pymodbus_apply_logging_config("INFO")

class ModbusTCP(Modbus):

    """
    ip: string, IP address of the Modbus TCP device,
    mac: string, MAC address of the Modbus TCP device,
    port: int, Port of the Modbus TCP device,
    device_type: string, solaredge, huawei or fronius etc...,
    address: int, Modbus address of the Modbus TCP device
    """

    CONNECTION = "TCP"
    
    @property
    def IP(self) -> str:
        return "ip"

    @property
    def MAC(self) -> str:
        return "mac"
    
    @property
    def PORT(self) -> int:
        return "port"
    
    @property
    def DEVICE_TYPE(self) -> str:
        return "device_type"
    
    @property
    def SLAVE_ID(self) -> int:
        return "slave_id"

    @staticmethod
    def list_to_tuple(config: list) -> tuple:
        assert config[ICom.CONNECTION_IX] == ModbusTCP.CONNECTION, "Invalid connection type"
        ip = config[1]
        mac = config[2]
        port = int(config[3])
        device_type = config[4]
        slave_id = int(config[5])
        return (config[ICom.CONNECTION_IX], ip, mac, port, device_type, slave_id)
    
    @staticmethod
    def dict_to_tuple(config: dict) -> tuple:
        assert config[ICom.CONNECTION_KEY] == ModbusTCP.CONNECTION, "Invalid connection type"
        ip = config["ip"]
        mac = config["mac"]
        port = int(config["port"])
        device_type = config["device_type"]
        slave_id = int(config["slave_id"])
        return (config[ICom.CONNECTION_KEY], ip, mac, port, device_type, slave_id)

    def __init__(self, 
                 ip: str = None, 
                 mac: str = "00:00:00:00:00:00", 
                 port: int = None, 
                 device_type: str = None, 
                 slave_id: int = None) -> None:
        log.info("Creating with: %s %s %s %s %s" % (ip, mac, port, device_type, slave_id))
        self.ip = ip
        self.mac = mac
        self.port = port
        self.device_type = device_type
        self.slave_id = slave_id
        self.client = None
        self.data_type = HarvestDataType.MODBUS_REGISTERS.value
        super().__init__()

    def _open(self, **kwargs) -> bool:
        if not self._is_terminated():
            self._create_client(**kwargs)
            if not self.client.connect():
                log.error("FAILED to open Modbus TCP device: %s", self._get_type())
            return bool(self.client.socket)
        else:
            return False

    def _is_open(self) -> bool:
        return bool(self.client) and bool(self.client.socket)

    def _close(self) -> None:
        log.info("Closing client ModbusTCP")
        self.client.close()

    def _terminate(self) -> None:
        self._close()
        self._isTerminated = True

    def _is_terminated(self) -> bool:
        return self._isTerminated

    def _clone(self, ip: str = None) -> 'ModbusTCP':
        if ip is None:
            ip = self._get_host()

        return ModbusTCP(ip, self._get_mac(), self._get_port(),
                            self._get_type(), self._get_slave_id())

    def _get_host(self) -> str:
        return self.ip
    
    def _get_mac(self) -> str:
        return self.mac

    def _get_port(self) -> int:
        return self.port

    def _get_type(self) -> str:
        return self.device_type

    def _get_slave_id(self) -> int:
        return self.slave_id

    def _get_config(self) -> tuple[str, str, int, str, int]:
        return (
            ModbusTCP.CONNECTION,
            self._get_host(),
            self._get_mac(),
            self._get_port(),
            self._get_type(),
            self._get_slave_id(),
        )

    def _get_config_dict(self) -> dict:
        return {
            ICom.CONNECTION_KEY: ModbusTCP.CONNECTION,
            self.DEVICE_TYPE: self._get_type(),
            self.MAC: self._get_mac(),
            self.SLAVE_ID: self._get_slave_id(),
            self.IP: self._get_host(),
            self.PORT: self._get_port(),
        }

    def _create_client(self, **kwargs) -> None:
        self.client =  ModbusClient(host=self._get_host(),
                                    port=self._get_port(), 
                                    unit_id=self._get_slave_id(),
                                    **kwargs
        )
        self.mac = NetworkUtils.get_mac_from_ip(self._get_host())
    def _read_registers(self, operation, scan_start, scan_range) -> list:
        resp = None
        
        if operation == 0x04:
            resp = self.client.read_input_registers(scan_start, scan_range, slave=self._get_slave_id())
        elif operation == 0x03:
            resp = self.client.read_holding_registers(scan_start, scan_range, slave=self._get_slave_id())

        # Not sure why read_input_registers dose not raise an ModbusIOException but rather returns it
        # We solve this by raising the exception manually
        if isinstance(resp, ModbusIOException):
            raise ModbusIOException("Exception occurred while reading registers")
        
        return resp.registers
    
    def write_registers(self, starting_register, values) -> None:
        """
        Write a range of holding registers from a start address
        """
        resp = self.client.write_registers(
            starting_register, values, slave=self._get_slave_id()
        )
        log.debug("OK - Writing Holdings: %s - %s", str(starting_register),  str(values))
        
        if isinstance(resp, ExceptionResponse):
            raise Exception("writeRegisters() - ExceptionResponse: " + str(resp))
        return resp
    