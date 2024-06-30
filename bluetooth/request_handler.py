import logging 
import constants 
from bless import (  # type: ignore
    BlessServer,
    BlessGATTCharacteristic
)
import protos.wifi_services_pb2 as wifi_services_pb2
import threading
import srcful_gw
import helium_gw
import time
from typing import Any

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def read_request(server: BlessServer, characteristic: BlessGATTCharacteristic, **kwargs) -> bytearray:
    logger.debug(f"################################################")
    logger.debug(f"***** Read request {characteristic.uuid} {characteristic.value}")
    logger.debug(f"################################################")
    
    if characteristic.uuid == constants.WIFI_SERVICES_UUID:
        wifi_ssids = srcful_gw.get_wifi_ssids()
        logger.debug(f"Got wifi ssids {wifi_ssids}")

        services = wifi_services_pb2.wifi_services_v1()
        for ssid in wifi_ssids:
            if len(ssid) > 0:
                services.services.append(ssid)

        characteristic.value = bytes(services.SerializeToString())
        server.update_value(constants.SERVICE_UUID, constants.WIFI_CONNECT_UUID)
    
    elif characteristic.uuid == constants.WIFI_MAC_UUID:
        logger.debug(f"Getting current wifi ssid")
        wifi_ssid = srcful_gw.get_connected_wifi_ssid()
        characteristic.value = bytes(wifi_ssid, "utf-8")
        server.update_value(constants.SERVICE_UUID, wifi_ssid)


def write_request(server: BlessServer, characteristic: BlessGATTCharacteristic, value: Any, **kwargs) -> bool:
    logger.debug(f"################################################")
    logger.debug(f"***** Write request {characteristic.uuid}, {value.decode('utf-8')}")
    logger.debug(f"################################################")
    if characteristic.uuid == constants.ADD_GATEWAY_UUID:
        
        # Seems like the timing of return here is critical. 
        # If the return is too early, the value is not updated
        helium_gw.add_gateway(server, characteristic, value)

        # threading.Thread(target=helium_gw.add_gateway, args=(server, characteristic, value,)).start()
        # time.sleep(1) # Look into this... This was needed in order for the value to be updated before it was read
        return True
    elif characteristic.uuid == constants.WIFI_CONNECT_UUID:
        threading.Thread(target=srcful_gw.connect_wifi, args=(server, characteristic, value,)).start()
        return True
    return False