from ModbusRTU import ModbusRTU
from ModbusTCP import ModbusTCP
from ModbusSolarman import ModbusSolarman
from ModbusSunspec import ModbusSunspec
from ICom import ICom
import logging

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

class IComFactory:
    """
    IComFactory class
    """
    
    @staticmethod
    def parse_connection_args(args: list) -> tuple:
        
        match args[0]:
            case "TCP":
                ip = args[1]
                port = int(args[2])
                inverter_type = args[3]
                slave_id = int(args[4])
                return (ip, port, inverter_type, slave_id)
            case "RTU":
                port = args[1]
                baudrate = int(args[2])
                bytesize = int(args[3])
                parity = args[4]
                stopbits = float(args[5])
                inverter_type = args[6]
                slave_id = int(args[7])
                return (port, baudrate, bytesize, parity, stopbits, inverter_type, slave_id)
            case "SOLARMAN":
                ip = args[1]
                serial = int(args[2])
                port = int(args[3])
                inverter_type = args[4]
                slave_id = int(args[5])
                verbose = False
                return (ip, serial, port, inverter_type, slave_id, verbose)
            case "SUNSPEC":
                ip = args[1]
                port = int(args[2])
                slave_id = int(args[3])
                return (ip, port, slave_id)
            case _:
                log.error("Unknown connection type: %s", args[0])
                return None
        
        
    @staticmethod
    def create_com(args: tuple) -> ICom:
        """
        Create a new ICom object
        """
        
        connection_type = args[0]
        connection_args = IComFactory.parse_connection_args(args)
        
        factories = {
            "TCP": ModbusTCP(connection_args),
            "RTU": ModbusRTU(connection_args),
            "SOLARMAN": ModbusSolarman(connection_args),
            "SUNSPEC": ModbusSunspec(connection_args)
        }
        
        try:
            return factories[connection_type]
        except:
            log.error("Unknown connection type: %s", connection_type)
            return None
            
        