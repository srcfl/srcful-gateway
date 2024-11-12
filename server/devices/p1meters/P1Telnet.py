import logging
import select
import socket
import errno
from typing import Callable, List, Optional

from server.devices.Device import Device
from server.devices.TCPDevice import TCPDevice
from server.devices.p1meters.p1_scanner import scan_for_p1_device
from server.network import mdns as mdns
from server.network.network_utils import HostInfo
from ..ICom import HarvestDataType, ICom
import time

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class SimpleTelnet:
    def __init__(self, ip, port, timeout=5):
        self.ip = ip
        self.port = port
        self.timeout = timeout
        self.socket = None
        self.buffer = b""

    def connect(self):
        self.socket = socket.create_connection((self.ip, self.port), self.timeout)
        self.socket.setblocking(False)

    def close(self):
        if self.socket:
            self.socket.close()
            self.socket = None
    
    def clear_buffer(self):
        self.buffer = b""

    def read_until(self, delimiter, timeout=None):
        if timeout is None:
            timeout = self.timeout
        
        start_time = time.time()
        
        while True:
            if time.time() - start_time > timeout:
                raise TimeoutError("Read operation timed out")
            
            if delimiter in self.buffer:
                index = self.buffer.index(delimiter)
                result = self.buffer[:index + len(delimiter)]
                self.buffer = self.buffer[index + len(delimiter):]
                return result
            
            ready = select.select([self.socket], [], [], 1.0)
            if ready[0]:
                try:
                    chunk = self.socket.recv(1024)
                    if not chunk:
                        raise ConnectionError("Connection closed by remote host")
                    self.buffer += chunk
                except socket.error as e:
                    if e.errno == errno.EWOULDBLOCK or e.errno == errno.EAGAIN:
                        # No data available right now, just continue the loop
                        continue
                    else:
                        logger.error(f"Socket error occurred: {str(e)}")
                        raise
                    

    def get_socket(self):
        return self.socket

class P1Telnet(TCPDevice):


    CONNECTION = "P1Telnet"

    
    @staticmethod
    def get_supported_devices():
        return {P1Telnet.CONNECTION: {'device_type': P1Telnet.CONNECTION, 'display_name': 'P1 Telnet', 'protocol': 'telnet'}}
    
    @staticmethod
    def get_config_schema():
        return {
            **TCPDevice.get_config_schema(P1Telnet.CONNECTION),
            "meter_serial_number": "optional string, Serial number of the meter",
            "model_name": "optional string, Model name of the meter"
        }


    """
    P1Telnet class
    """
    client: SimpleTelnet
    ip: str
    port: int
    meter_serial_number: str
    model_name: str

    def __init__(self, ip: str, port: int = 23, meter_serial_number: str = "", model_name: str = "generic_p1_meter"):
        self.ip = ip
        self.port = port
        self.meter_serial_number = meter_serial_number
        self.model_name = model_name

    def _connect(self, **kwargs) -> bool:
        try:
            self.client = SimpleTelnet(self.ip, self.port, 5)
            self.client.connect()
            logger.info(f"Successfully connected to {self.ip}:{self.port}")
            harvest = self.read_harvest_data(False)
            if self.meter_serial_number == "":
                self.meter_serial_number = harvest['serial_number']
                return True
            else:
                return self.meter_serial_number == harvest['serial_number']
        except Exception as e:
            logger.error(f"Failed to connect to {self.ip}:{self.port}: {str(e)}")
            return False
    
    def _disconnect(self) -> None:
        if self.client:
            self.client.close()
       
    def is_open(self) -> bool:
        return self.client is not None and self.client.get_socket() is not None
    
    def _read_harvest_data(self, force_verbose) -> dict:
        try:
            p1_message = self._read_harvest_data_internal(self.client)
            data = self._parse_p1_message(p1_message)
            return data
        except Exception as e:
            logger.error(f"Error reading P1 data: {str(e)}")
            raise
        
    def _read_harvest_data_internal(self, telnet_client: SimpleTelnet) -> str:
        timeout = 20
        
        # we clear the buffer so we don't get old data
        telnet_client.clear_buffer()

        # Read until the start of a P1 message
        telnet_client.read_until(b"/", timeout=timeout)
        
        # Read the entire P1 message including the last crc check
        p1_message = "/" + telnet_client.read_until(b"!", timeout=timeout).decode('ascii') + telnet_client.read_until(b"\r\n", timeout=timeout).decode('ascii')

        if len(p1_message) < 5:
            logger.error(f"P1 message is too short: {p1_message}")
            raise Exception(f"P1 message is too short: {p1_message}")
        
        return p1_message    

    def _parse_p1_message(self, message: str) -> dict:
        lines = message.strip().split()
        data = {
            'serial_number': '',
            'rows': []
        }
        
        # Extract serial number from the first line remove the leading '/'
        data['serial_number'] = lines[0][1:]
        
        # Add all other lines to the rows list
        data['rows'] = [line.strip() for line in lines[1:] if line.strip()]
        
        return data


    def get_harvest_data_type(self) -> HarvestDataType:
        return HarvestDataType.P1_TELNET
    
    def get_config(self) -> dict:
        return {
            **TCPDevice.get_config(self),
            "meter_serial_number": self.meter_serial_number
        }
    
    def _get_connection_type(self) -> str:
        return P1Telnet.CONNECTION
    
    def get_name(self) -> str:
        return "P1Telnet"
    
    def clone(self, ip: Optional[str] = None) -> 'ICom':
        if ip is None:
            ip = self.ip
        return P1Telnet(ip, self.port, self.meter_serial_number)

    
    def find_device(self) -> Optional[ICom]:
        """ If there is an id we try to find a device with that id, using multicast dns for for supported devices"""
        if self.meter_serial_number:
            return scan_for_p1_device(self.meter_serial_number)
                
        # notthing to connect to
        return None

    def _clone_with_host(self, host: HostInfo) -> Optional[ICom]:
        
        config = self.get_config()
        config[self.IP] = host.ip
        return P1Telnet(**config)
    
    def get_SN(self) -> str:
        return self.meter_serial_number

    def get_backoff_time_ms(self, harvest_time_ms: int, previous_backoff_time_ms: int) -> int:
        # p1 meters typically send data every 10 seconds
        return 10 * 1000
