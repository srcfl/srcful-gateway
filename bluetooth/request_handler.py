import logging 
from typing import Any
from bless import (  # type: ignore
    BlessServer,
    BlessGATTCharacteristic
)
import constants 
import protos.wifi_services_pb2 as wifi_services_pb2
from srcful_gateway import SrcfulGateway
from helium_gateway import HeliumGateway


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

srcful_gw = SrcfulGateway()
helium_gw = HeliumGateway()

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
        add_gateway_txn = helium_gw.create_add_gateway_txn(value)

        characteristic.value = add_gateway_txn
        if server.update_value(constants.SERVICEc_UUID, constants.ADD_GATEWAY_UUID):
            logger.debug(f"Char updated, value set to {characteristic.value}")
        else:
            logger.debug(f"Failed to update value")

        return True
    elif characteristic.uuid == constants.WIFI_CONNECT_UUID:

        def update_status_callback(status):
            logger.debug(f"WiFi Status: {status}")
            
            characteristic.value = bytes(status, "utf-8")
            server.update_value(constants.SERVICE_UUID, constants.WIFI_CONNECT_UUID)
        
        srcful_gw.connect_wifi(value, update_status_callback)
        
        return True
    
    return False