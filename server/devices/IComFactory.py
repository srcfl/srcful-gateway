from .ModbusRTU import ModbusRTU
from .ModbusTCP import ModbusTCP
from .ModbusSolarman import ModbusSolarman
from .ModbusSunspec import ModbusSunspec
from .P1Telnet import P1Telnet
from .ICom import ICom
import logging

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class IComFactory:


    @staticmethod
    def get_supported_connections():
        return [
            ModbusTCP.CONNECTION,
            ModbusRTU.CONNECTION,
            ModbusSolarman.CONNECTION,
            ModbusSunspec.CONNECTION,
            P1Telnet.CONNECTION,
        ]

    @staticmethod
    def get_connection_configs():
        return {
            cls.CONNECTION: cls.get_config_schema()
            for cls in [ModbusTCP, ModbusRTU, ModbusSolarman, ModbusSunspec, P1Telnet]
        }


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

        connection = config[ICom.CONNECTION_KEY]
        stripped_config = {k: v for k, v in config.items() if k != ICom.CONNECTION_KEY}
        
        log.info("####################################################")
        log.info("Creating ICom object for connection connection: %s", connection)
        log.info("Connection config: %s", stripped_config)
        log.info("####################################################")
        
        match connection:
            case ModbusTCP.CONNECTION:
                return ModbusTCP(**stripped_config)
            case ModbusRTU.CONNECTION:
                return ModbusRTU(**stripped_config)
            case ModbusSolarman.CONNECTION:
                return ModbusSolarman(**stripped_config)
            case ModbusSunspec.CONNECTION:
                return ModbusSunspec(**stripped_config)
            case P1Telnet.CONNECTION:
                return P1Telnet(**stripped_config)
            case _:
                log.error("Unknown connection type: %s", connection)
                return None
            
        