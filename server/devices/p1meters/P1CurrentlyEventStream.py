import logging
import json
import requests
import time
from typing import Optional
from dataclasses import dataclass
from server.devices.TCPDevice import TCPDevice
from server.devices.p1meters.common import P1_METER_CLIENT_NAME
from server.devices.p1meters.p1_scanner import scan_for_p1_device
from server.network.network_utils import HostInfo
from ..ICom import HarvestDataType, ICom

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@dataclass
class P1Event:
    id: str
    event: str
    data: str
    retry: Optional[int] = None


class SSEClient:
    def __init__(self, url: str, timeout: int = 30):
        self.url = url
        self.timeout = timeout
        self.session = None
        self.response = None

    def connect(self):
        self.session = requests.Session()
        self.response = self.session.get(
            self.url,
            stream=True,
            timeout=self.timeout,
            headers={'Accept': 'text/event-stream'}
        )
        self.response.raise_for_status()

    def read_event(self) -> Optional[P1Event]:
        if not self.response:
            return None

        event = P1Event(id="", event="", data="")
        for line in self.response.iter_lines():
            if not line:
                if event.event:  # Return event if we have one
                    try:
                        event.data = json.loads(event.data)
                    except json.JSONDecodeError:
                        pass
                    return event
                continue

            line = line.decode('utf-8')
            if ': ' not in line:
                continue

            field, value = line.split(': ', 1)
            if field == 'event':
                event.event = value
            elif field == 'data':
                event.data = value
            elif field == 'id':
                event.id = value
            elif field == 'retry':
                try:
                    event.retry = int(value)
                except ValueError:
                    pass

        return None

    def close(self):
        if self.response:
            self.response.close()
        if self.session:
            self.session.close()
            self.session = None
            self.response = None


class P1CurrentlyEventStream(TCPDevice):
    CONNECTION = "P1CurrentlyEventStream"

    @staticmethod
    def get_supported_devices(verbose: bool = True):
        if verbose:
            return {P1CurrentlyEventStream.CONNECTION: {
                P1CurrentlyEventStream.DEVICE_TYPE: P1CurrentlyEventStream.CONNECTION,
                P1CurrentlyEventStream.MAKER: 'P1 Currently Event Stream',
                P1CurrentlyEventStream.DISPLAY_NAME: 'P1 Currently Event Stream',
                P1CurrentlyEventStream.PROTOCOL: 'http'
            }}
        else:
            return {P1CurrentlyEventStream.CONNECTION: {
                P1CurrentlyEventStream.MAKER: 'P1 Currently Event Stream'
            }}

    @staticmethod
    def get_config_schema():
        return {
            **TCPDevice.get_config_schema(P1CurrentlyEventStream.CONNECTION),
            "meter_serial_number": "optional string, Serial number of the meter",
            "model_name": "optional string, Model name of the meter"
        }

    def __init__(self, ip: str, port: int = 80, meter_serial_number: str = "", model_name: str = "generic_p1_meter"):
        self.ip = ip
        self.port = port
        self.meter_serial_number = meter_serial_number
        self.model_name = model_name
        self.client = None
        self._previous_state = None

    def _connect(self, **kwargs) -> bool:
        try:
            # First get device ID from info endpoint
            info_url = f"http://{self.ip}:{self.port}/api/v1/info"
            response = requests.get(info_url, timeout=5)
            response.raise_for_status()
            info = response.json()
            self.meter_serial_number = info.get("id", "")
            logger.info(f"Got meter ID from info: {self.meter_serial_number}")

            # Then connect to event stream for harvesting
            url = f"http://{self.ip}:{self.port}/events"
            self.client = SSEClient(url)
            self.client.connect()
            logger.info(f"Connected to event stream at {url}")
            return True

        except Exception as e:
            logger.error(f"Failed to connect: {str(e)}")
            return False

    def _disconnect(self) -> None:
        if self.client:
            self.client.close()
            self.client = None

    def _is_open(self) -> bool:
        return self.client is not None

    def _read_harvest_data(self, force_verbose) -> dict:
        if not self.client:
            raise ConnectionError("Not connected")

        event = self.client.read_event()
        if not event:
            raise ConnectionError("Stream closed")

        logger.info(f"Event: {event.event} -> {event.data}")

        if event.event == "state":
            if self._previous_state != event.data:
                self._previous_state = event.data
                return event.data
            return {}

        return {}

    def get_harvest_data_type(self) -> HarvestDataType:
        return HarvestDataType.P1_EVENT_STREAM

    def get_config(self) -> dict:
        return {
            **TCPDevice.get_config(self),
            "meter_serial_number": self.meter_serial_number
        }

    def _get_connection_type(self) -> str:
        return P1CurrentlyEventStream.CONNECTION

    def get_name(self) -> str:
        return "P1CurrentlyEventStream"

    def get_client_name(self) -> str:
        return P1_METER_CLIENT_NAME + "." + "currently.eventstream"

    def clone(self, ip: Optional[str] = None) -> 'ICom':
        if ip is None:
            ip = self.ip
        return P1CurrentlyEventStream(ip, self.port, self.meter_serial_number)

    def find_device(self) -> Optional[ICom]:
        if self.meter_serial_number:
            return scan_for_p1_device(self.meter_serial_number)
        return None

    def _clone_with_host(self, host: HostInfo) -> Optional[ICom]:
        config = self.get_config()
        config[self.IP] = host.ip
        return P1CurrentlyEventStream(**config)

    def get_SN(self) -> str:
        return self.meter_serial_number

    def get_backoff_time_ms(self, harvest_time_ms: int, previous_backoff_time_ms: int) -> int:
        # The event stream sends updates roughly every 5 seconds
        return 5 * 1000
