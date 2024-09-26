from datetime import datetime, timezone
import requests
from .ICom import ICom, HarvestDataType, DER_TYPE
from .supported_inverters.profiles import InverterProfile
import logging

logger = logging.getLogger(__name__)

class HomeWizardP1(ICom):
    CONNECTION = "HOMEWIZARD_P1"
    data_type = HarvestDataType.HOMEWIZARD_P1

    @staticmethod
    def list_to_tuple(config: list) -> tuple:
        return (HomeWizardP1.CONNECTION, config[1], config[2] if len(config) > 2 else None)

    @staticmethod
    def dict_to_tuple(config: dict) -> tuple:
        return (HomeWizardP1.CONNECTION, config["host"], config.get("serial"))

    @staticmethod
    def get_config_schema():
        return {
            "host": "string, IP address or hostname of the device",
            "serial": "string, serial number of the device (optional)",
        }

    def get_min_backoff_time(self) -> int:
        return 1000 * 10 # 10 seconds

    def __init__(self, config):
        self.host = config[0]
        if len(config) == 2:
            self.serial = config[1]
        else:
            self.serial = None
        self.api_url = f"http://{self.host}/api"
        self.connected = False

    def connect(self) -> bool:
        ''' Get the serial number from the data and either set it or check that it is correct   '''
        try:
            response = requests.get(f"{self.api_url}")
            if response.status_code == 200:
                serial = response.json().get("serial")
                if self.serial is None:
                    self.serial = serial
                elif self.serial != serial:
                    logger.error(f"Serial number does not match: {self.serial} != {serial}")
                    return False
                
                self.connected = True
                return True
            else:
                logger.error(f"Failed to connect to HomeWizard P1 meter: {response.status_code}")
                return False
        except requests.RequestException as e:
            logger.error(f"Error connecting to HomeWizard P1 meter: {e}")
            return False

    def disconnect(self) -> None:
        self.connected = False

    def reconnect(self) -> bool:
        self.disconnect()
        return self.connect()

    def is_open(self) -> bool:
        return self.connected

    def read_harvest_data(self, der_type=DER_TYPE.UTILITY_METER, force_verbose=False) -> dict:
        if not self.is_open():
            raise ConnectionError("Not connected to HomeWizard P1 meter")

        try:
            response = requests.get(f"{self.api_url}/v1/data")
            if response.status_code == 200:
                data = response.json()
                if force_verbose:
                    return data
                else:

                    return {
                        "active_power_w": data.get("active_power_w"),
                    }
            else:
                raise requests.RequestException(f"Failed to read data: {response.status_code}")
        except requests.RequestException as e:
            logger.error(f"Error reading data from HomeWizard P1 meter: {e}")
            raise

    def get_harvest_data_type(self) -> str:
        return self.data_type.value

    def get_config(self) -> dict:
        return {
            ICom.CONNECTION_KEY: self.CONNECTION,
            "host": self.host,
            "serial": self.serial
        }
    
    def get_model_name(self) -> str:
        return "home_wizard_P1"

    def clone(self, host: str) -> 'HomeWizardP1':
        return HomeWizardP1([host, self.serial])