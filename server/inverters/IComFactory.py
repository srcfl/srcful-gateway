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
            case "TCP":
                ip = config[1]
                port = int(config[2])
                inverter_type = config[3]
                slave_id = int(config[4])
                return (config[0], ip, port, inverter_type, slave_id)
            case "RTU":
                port = config[1]
                baudrate = int(config[2])
                bytesize = int(config[3])
                parity = config[4]
                stopbits = float(config[5])
                inverter_type = config[6]
                slave_id = int(config[7])
                return (config[0], port, baudrate, bytesize, parity, stopbits, inverter_type, slave_id)
            case "SOLARMAN":
                ip = config[1]
                serial = int(config[2])
                port = int(config[3])
                inverter_type = config[4]
                slave_id = int(config[5])
                verbose = False
                return (config[0], ip, serial, port, inverter_type, slave_id, verbose)
            case "SUNSPEC":
                ip = config[1]
                port = int(config[2])
                slave_id = int(config[3])
                return (config[0], ip, port, slave_id)
            case _:
                log.error("Unknown connection type: %s", config[0])
                return None
        
    @staticmethod
    def parse_connection_config_from_dict(config: dict) -> tuple:
        
        match config["mode"]:
            case "TCP":
                ip = config["ip"]
                port = int(config["port"])
                inverter_type = config["type"]
                slave_id = int(config["address"])
                return (config["mode"], ip, port, inverter_type, slave_id)
            case "RTU":
                serial_port = config["serial_port"]
                baudrate = int(config["baudrate"])
                bytesize = int(config["bytesize"])
                parity = config["parity"]
                stopbits = float(config["stopbits"])
                inverter_type = config["type"]
                slave_id = int(config["address"])
                return (config["mode"], serial_port, baudrate, bytesize, parity, stopbits, inverter_type, slave_id)
            case "SOLARMAN":
                ip = config["ip"]
                serial = int(config["serial"])
                port = int(config["port"])
                inverter_type = config["type"]
                slave_id = int(config["address"])
                verbose = False
                return (config["mode"], ip, serial, port, inverter_type, slave_id, verbose)
            case "SUNSPEC":
                ip = config["host"]
                port = int(config["port"])
                slave_id = int(config["address"])
                return (config["mode"], ip, port, slave_id)
            case _:
                log.error("Unknown connection type: %s", config["mode"])
                raise ValueError("Unknown connection type")

    
    @staticmethod
    def create_com(config: tuple) -> ICom:
        """
        Create an ICom object for device communication.

        Args:
            config (tuple): Connection-specific arguments as a tuple:
                ('TCP', ip, port, inverter_type, slave_id)
                ('RTU', port, baudrate, bytesize, parity, stopbits, inverter_type, slave_id)
                ('SOLARMAN', ip, serial, port, inverter_type, slave_id)
                ('SUNSPEC', ip, port, slave_id)

        Returns:
            ICom: Communication object for the specified connection type.

        Raises:
            ValueError: If the connection type (first element of the tuple) is unsupported.
        """
                    
        mode = config[0]
        connection_config = config[1:]
        # connection_config = IComFactory.parse_connection_config_from_list(config)
        log.info("####################################################")
        log.info("Creating ICom object for connection mode: %s", mode)
        log.info("Connection config: %s", connection_config)
        log.info("####################################################")
        
        match mode:
            case "TCP":
                return ModbusTCP(connection_config)
            case "RTU":
                return ModbusRTU(connection_config)
            case "SOLARMAN":
                return ModbusSolarman(connection_config)
            case "SUNSPEC":
                return ModbusSunspec(connection_config)
            case _:
                log.error("Unknown connection mode: %s", mode)
                return None
            
        