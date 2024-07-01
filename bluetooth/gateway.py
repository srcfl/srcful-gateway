import logging 
from typing import Any
from bless import (  # type: ignore
    BlessServer,
    BlessGATTCharacteristic,
    GATTAttributePermissions,
    GATTCharacteristicProperties,
)
import constants 
import protos.wifi_services_pb2 as wifi_services_pb2
import protos.diagnostics_pb2 as diagnostics_pb2
from srcful_gateway import SrcfulGateway
from helium_gateway import HeliumGateway


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Move these one level up, e.g. in ble_service and pass as arguments? 
srcful_gw = SrcfulGateway()
helium_gw = HeliumGateway()



class Gateway:
    def __init__(self, server: BlessServer) -> None:
        self.server = server
    
    async def init_gateway(self):
        await self.server.add_new_service(constants.SERVICE_UUID)

        char_flags = GATTCharacteristicProperties.read
        permissions = GATTAttributePermissions.readable

        gateway_swarm = srcful_gw.get_swarm_id()
        gateway_eth_ip = srcful_gw.get_eth_ip()
        gateway_eth_mac = srcful_gw.get_eth_mac()
        gateway_wifi_ip = srcful_gw.get_wifi_ip()
        gateway_wifi_mac = srcful_gw.get_wifi_mac()
        
        # To-Do: Read the onboarding and public key from the device and populate the characteristics
        await self.server.add_new_characteristic(constants.SERVICE_UUID, constants.ONBOARDING_KEY_UUID, char_flags, bytes(gateway_swarm, 'utf-8'), permissions)
        await self.server.add_new_characteristic(constants.SERVICE_UUID, constants.PUBLIC_KEY_UUID, char_flags, bytes(gateway_swarm, 'utf-8'), permissions)
        await self.server.add_new_characteristic(constants.SERVICE_UUID, constants.WIFI_MAC_UUID, char_flags, bytes(gateway_wifi_mac, 'utf-8'), permissions)
        await self.server.add_new_characteristic(constants.SERVICE_UUID, constants.LIGHTS_UUID, char_flags, b'n/a', permissions)
        await self.server.add_new_characteristic(constants.SERVICE_UUID, constants.WIFI_SSID_UUID, char_flags, b'magic_ssid', permissions)
        await self.server.add_new_characteristic(constants.SERVICE_UUID, constants.ETHERNET_ONLINE, char_flags, b'false', permissions)

        services = wifi_services_pb2.wifi_services_v1()
        await self.server.add_new_characteristic(constants.SERVICE_UUID, constants.WIFI_SERVICES_UUID, char_flags, bytes(services.SerializeToString()), permissions)


        services = diagnostics_pb2.diagnostics_v1()
        services.diagnostics['Name:\n'] = 'AA'
        services.diagnostics['\nPublic Key:\n'] = gateway_swarm
        services.diagnostics['\nEthernet IP:\n'] = gateway_eth_ip
        services.diagnostics['\nEtherner Mac:\n'] = gateway_eth_mac
        services.diagnostics['\nWiFi IP:\n'] = gateway_wifi_ip
        services.diagnostics['\nWiFi Mac:\n'] = gateway_wifi_mac

        await self.server.add_new_characteristic(constants.SERVICE_UUID, constants.DIAGNOSTICS_UUID, char_flags, bytes(services.SerializeToString()), permissions)


        char_flags = GATTCharacteristicProperties.write | GATTCharacteristicProperties.read | GATTCharacteristicProperties.indicate
        permissions = GATTAttributePermissions.writeable | GATTAttributePermissions.readable
        await self.server.add_new_characteristic(constants.SERVICE_UUID, constants.ADD_GATEWAY_UUID, char_flags, b'', permissions)

        await self.server.add_new_characteristic(constants.SERVICE_UUID, constants.WIFI_CONNECT_UUID, char_flags, b'', permissions)

        logger.debug(f"Helium Service added with uuid {constants.SERVICE_UUID}")


    def handle_read_request(self, characteristic: BlessGATTCharacteristic, **kwargs) -> bytearray:
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
            self.server.update_value(constants.SERVICE_UUID, constants.WIFI_CONNECT_UUID)
        
        elif characteristic.uuid == constants.WIFI_MAC_UUID:
            logger.debug(f"Getting current wifi ssid")
            wifi_ssid = srcful_gw.get_connected_wifi_ssid()
            characteristic.value = bytes(wifi_ssid, "utf-8")
            self.server.update_value(constants.SERVICE_UUID, wifi_ssid)

    def handle_write_request(self, characteristic: BlessGATTCharacteristic, value: Any, **kwargs) -> bool:
        logger.debug(f"################################################")
        logger.debug(f"***** Write request {characteristic.uuid}, {value.decode('utf-8')}")
        logger.debug(f"################################################")
        if characteristic.uuid == constants.ADD_GATEWAY_UUID:
            
            # Seems like the timing of return here is critical. 
            # If the return is too early, the value is not updated
            add_gateway_txn = helium_gw.create_add_gateway_txn(value)

            characteristic.value = add_gateway_txn
            if self.server.update_value(constants.SERVICE_UUID, constants.ADD_GATEWAY_UUID):
                logger.debug(f"Char updated, value set to {characteristic.value}")
            else:
                logger.debug(f"Failed to update value")

            return True
        elif characteristic.uuid == constants.WIFI_CONNECT_UUID:

            def update_status_callback(status):
                logger.debug(f"WiFi Status: {status}")
                
                characteristic.value = bytes(status, "utf-8")
                self.server.update_value(constants.SERVICE_UUID, constants.WIFI_CONNECT_UUID)
            
            srcful_gw.connect_wifi(value, update_status_callback)
            
            return True
        
        return False