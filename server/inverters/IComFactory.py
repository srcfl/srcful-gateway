from .ModbusRTU import ModbusRTU
from .ModbusTCP import ModbusTCP
from .ModbusSolarman import ModbusSolarman
from .ModbusSunspec import ModbusSunspec
from .ICom import ICom
import logging

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class IComFactory:
    """
    IComFactory class
    """
    
    @staticmethod
    def parse_connection_config_from_list(config: list) -> tuple:
        
        logging.debug("Parsing connection config from list: %s", config)
        
        match config[0]:
            case ModbusTCP.CONNECTION:
                return ModbusTCP.list_to_tuple(config)
            case ModbusRTU.CONNECTION:
                return ModbusRTU.list_to_tuple(config)
            case ModbusSolarman.CONNECTION:
                return ModbusSolarman.list_to_tuple(config)
            case ModbusSunspec.CONNECTION:
                return ModbusSunspec.list_to_tuple(config)
            case _:
                log.error("Unknown connection type: %s", config[0])
                return None
        
    @staticmethod
    def parse_connection_config_from_dict(config: dict) -> tuple:
        
        match config[ICom.CONNECTION_KEY]:
            case ModbusTCP.CONNECTION:
                return ModbusTCP.dict_to_tuple(config)
            case ModbusRTU.CONNECTION:
                return ModbusRTU.dict_to_tuple(config)
            case ModbusSolarman.CONNECTION:
                return ModbusSolarman.dict_to_tuple(config)
            case ModbusSunspec.CONNECTION:
                return ModbusSunspec.dict_to_tuple(config)
            case _:
                log.error("Unknown connection type: %s", config[ICom.CONNECTION_KEY])
                raise ValueError("Unknown connection type")

    
    @staticmethod
    def create_com(config: tuple) -> ICom:
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
                    
        connection = config[ICom.CONNECTION_IX]
        connection_config = [c for c in config if c != connection]
        # connection_config = IComFactory.parse_connection_config_from_list(config)
        log.info("####################################################")
        log.info("Creating ICom object for connection connection: %s", connection)
        log.info("Connection config: %s", connection_config)
        log.info("####################################################")
        
        match connection:
            case ModbusTCP.CONNECTION:
                return ModbusTCP(connection_config)
            case ModbusRTU.CONNECTION:
                return ModbusRTU(connection_config)
            case ModbusSolarman.CONNECTION:
                return ModbusSolarman(connection_config)
            case ModbusSunspec.CONNECTION:
                return ModbusSunspec(connection_config)
            case _:
                log.error("Unknown connection type: %s", connection)
                return None
            
        