from typing import Optional
import requests
from server.devices.ICom import HarvestDataType, ICom
from server.devices.TCPDevice import TCPDevice
from server.devices.p1meters.common import P1_METER_CLIENT_NAME
from server.devices.p1meters.p1_scanner import scan_for_p1_device
import logging
from server.network.network_utils import HostInfo

logger = logging.getLogger(__name__)


class P1HomeWizard(TCPDevice):

    CONNECTION = "P1HomeWizard"

    @staticmethod
    def get_supported_devices(verbose: bool = True):
        logger.info("Getting from P1HomeWizard")
        if verbose:
            return {P1HomeWizard.CONNECTION: {
                TCPDevice.DEVICE_TYPE: P1HomeWizard.CONNECTION,
                TCPDevice.MAKER: 'HomeWizard',
                TCPDevice.DISPLAY_NAME: 'HomeWizard P1 Meter'
            }}
        else:
            return {P1HomeWizard.CONNECTION: {
                TCPDevice.MAKER: 'HomeWizard'
            }}

    @staticmethod
    def get_config_schema():
        return {
            **TCPDevice.get_config_schema(P1HomeWizard.CONNECTION),
            "meter_serial_number": "optional string, Serial number of the meter",
            "model_name": "optional string, Model name of the meter"
        }

    """
    PHomeWizard class
    """
    ip: str
    port: int
    meter_serial_number: str
    model_name: str

    def __init__(self, ip: str, port: int = 80, meter_serial_number: str = "", model_name: str = "homewizard_p1_meter"):
        super().__init__(ip=ip, port=port)
        self.meter_serial_number = meter_serial_number
        self.model_name = model_name
        self.api_url = f"http://{self.ip}:{self.port}/api"
        self.endpoint = "/v1/telegram"
        self._has_connected = False

    def _connect(self, **kwargs) -> bool:
        try:
            harvest = self.read_harvest_data(False)
            if self.meter_serial_number == "":
                self.meter_serial_number = harvest['serial_number']
                self._has_connected = True
            else:
                self._has_connected = self.meter_serial_number == harvest['serial_number']
                if not self._has_connected:
                    logger.error(f"Failed to connect to {self.ip}:{self.port}: Wrong serial number {self.meter_serial_number} vs {harvest['serial_number']}")
            return self._has_connected
        except Exception as e:
            self._has_connected = False
            logger.error(f"Failed to connect to {self.ip}:{self.port}: {str(e)}")
            return self._has_connected

    def _disconnect(self) -> None:
        pass

    def _is_open(self) -> bool:
        return self._has_connected and self._connect()

    def calculate_checksum(self, telegram: str) -> str:
        # CRC16-IBM (also known as CRC16-ANSI) polynomial
        polynomial = 0xA001  # Reversed 0x8005
        crc = 0x0000  # Initial value

        # Process each character from / up to and including !
        start_index = telegram.find('/')
        end_index = telegram.rfind('!') + 1

        for char in telegram[start_index:end_index]:
            crc ^= ord(char)
            for _ in range(8):
                if crc & 0x0001:
                    crc = (crc >> 1) ^ polynomial
                else:
                    crc >>= 1

        # Return the hexadecimal representation (uppercase)
        return f"{crc:04X}"

    def _parse_p1_message(self, message: str) -> dict:

        # print(message.encode('ascii').hex())

        # this is the same as the P1Telnet device
        lines = message.strip().split()
        data = {
            'serial_number': '',
            'rows': [],
            'checksum': ''
        }

        # Extract serial number from the first line remove the leading '/'
        data['serial_number'] = lines[0][1:]

        # Extract checksum from the last line remove the leading '!'
        data['checksum'] = lines[-1][1:]

        # Add all other lines to the rows list
        data['rows'] = [line.strip() for line in lines[1:] if line.strip()]

        # check if the checksum is correct
        if data['checksum'] != self.calculate_checksum(message):
            raise Exception("Checksum is incorrect")

        return data

    def _read_harvest_data(self, force_verbose) -> dict:
        try:
            p1_message = requests.get(f"{self.api_url}{self.endpoint}", timeout=5)
            p1_message.raise_for_status()

            return self._parse_p1_message(p1_message.text)
        except Exception as e:
            logger.error(f"Error reading P1 data: {str(e)}")
            raise

    def get_harvest_data_type(self) -> HarvestDataType:
        # We return data in the same format as the P1Telnet device
        return HarvestDataType.P1_TELNET

    def get_config(self) -> dict:
        return {
            **TCPDevice.get_config(self),
            "meter_serial_number": self.meter_serial_number
        }

    def _get_connection_type(self) -> str:
        return P1HomeWizard.CONNECTION

    def get_name(self) -> str:
        return "P1HomeWizard"

    def get_client_name(self) -> str:
        return P1_METER_CLIENT_NAME + "." + "homewizard"

    def clone(self, ip: Optional[str] = None) -> 'ICom':
        if ip is None:
            ip = self.ip
        return P1HomeWizard(ip, self.port, self.meter_serial_number)

    def find_device(self) -> Optional['ICom']:
        """ If there is an id we try to find a device with that id, using multicast dns for for supported devices"""
        if self.meter_serial_number:
            return scan_for_p1_device(self.meter_serial_number)

        # notthing to connect to
        return None

    def get_SN(self) -> str:
        return self.meter_serial_number

    def get_backoff_time_ms(self, harvest_time_ms: int, previous_backoff_time_ms: int) -> int:
        # p1 meters typically send data every 10 seconds
        return 10 * 1000

    def _clone_with_host(self, host: HostInfo) -> Optional[ICom]:

        config = self.get_config()
        config[self.IP] = host.ip
        return P1HomeWizard(**config)
    
    def get_decoded_data(self, payload: dict | str) -> dict:
        return {}
