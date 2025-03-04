from .inverters.ModbusTCP import ModbusTCP
from .inverters.ModbusSolarman import ModbusSolarman
from .inverters.ModbusSunspec import ModbusSunspec
from .inverters.enphase import Enphase
from .p1meters.P1Telnet import P1Telnet
from .p1meters.P1Jemac import P1Jemac
from .p1meters.P1HomeWizard import P1HomeWizard
from .ICom import ICom
import logging

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class IComFactory:

    supported_devices = [ModbusTCP, ModbusSolarman, ModbusSunspec, P1Telnet, Enphase, P1Jemac, P1HomeWizard]

    @staticmethod
    def get_connection_configs():
        return {
            cls.CONNECTION: cls.get_config_schema()
            for cls in IComFactory.supported_devices
        }

    @staticmethod
    def get_supported_devices(verbose: bool = True):
        return [
            cls.get_supported_devices(verbose)
            for cls in IComFactory.supported_devices
        ]

    """
    IComFactory class
    """

    @staticmethod
    def create_com(config: dict) -> ICom:
        """
        Create an ICom object for device communication.

        Args:
            config (tuple): Connection-specific arguments as a tuple:
                ('TCP', host, port, inverter_type, slave_id)
                ('RTU', port, baudrate, bytesize, parity, stopbits, inverter_type, slave_id)
                ('SOLARMAN', host, serial, port, inverter_type, slave_id)
                ('SUNSPEC', host, port, slave_id)

        Returns:
            ICom: Communication object for the specified connection type.

        Raises:
            ValueError: If the connection type (first element of the tuple) is unsupported.
        """

        connection = config[ICom.connection_key()]

        # Strip the connection key and sn from the config
        stripped_config = {k: v for k, v in config.items() if k != ICom.connection_key()}

        log.debug("####################################################")
        log.debug("Creating ICom object for connection connection: %s", connection)
        log.debug("Connection config: %s", stripped_config)
        log.debug("####################################################")

        match connection:
            case ModbusTCP.CONNECTION:
                return ModbusTCP(**stripped_config)
            case ModbusSolarman.CONNECTION:
                return ModbusSolarman(**stripped_config)
            case ModbusSunspec.CONNECTION:
                return ModbusSunspec(**stripped_config)
            case P1Telnet.CONNECTION:
                return P1Telnet(**stripped_config)
            case Enphase.CONNECTION:
                return Enphase(**stripped_config)
            case P1Jemac.CONNECTION:
                return P1Jemac(**stripped_config)
            case P1HomeWizard.CONNECTION:
                return P1HomeWizard(**stripped_config)
            case _:
                log.error("Unknown connection type: %s", connection)
                raise ValueError(f"Unknown connection type: {connection}")
