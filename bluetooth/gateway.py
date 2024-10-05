import logging 
import asyncio
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
import sys

# Configure the root logger
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    stream=sys.stdout)
logger = logging.getLogger(__name__)


class Gateway:
    def __init__(self, server: BlessServer) -> None:
        self.server = server
        # Move these one level up, e.g. in ble_service and pass as arguments? 
        self.srcful_gw = SrcfulGateway()
        self.helium_gw = HeliumGateway()
        logger.debug("Gatewat Created")
        
    def update_diagnostics(self, characteristic: BlessGATTCharacteristic):        
        services = diagnostics_pb2.diagnostics_v1()
        services.diagnostics['Name:'] = 'AA'
        services.diagnostics['PubKey: '] = self.srcful_gw.get_swarm_id()
        services.diagnostics['Payer: '] = self.helium_gw.payer_name
        services.diagnostics['Payer Addr: '] = self.helium_gw.payer_address
        services.diagnostics['Eth IP: '] = self.srcful_gw.get_eth_ip()
        services.diagnostics['Eth Mac: '] = self.srcful_gw.get_eth_mac()
        services.diagnostics['WiFi SSID: '] = self.srcful_gw.get_connected_wifi_ssid()
        services.diagnostics['WiFi IP: '] = self.srcful_gw.get_wifi_ip()
        services.diagnostics['WiFi Mac: '] = self.srcful_gw.get_wifi_mac()
        
        characteristic.value = bytes(services.SerializeToString())
        self.server.update_value(constants.SERVICE_UUID, constants.DIAGNOSTICS_UUID)
        
    
    async def init_gateway(self):
        char_flags = GATTCharacteristicProperties.read
        permissions = GATTAttributePermissions.readable

        gateway_swarm = self.srcful_gw.get_swarm_id()
        
        logger.debug(f"Gateway Swarm: {gateway_swarm}")
        
        await self.helium_gw.fetch_payer(gateway_swarm)
        
        # To-Do: Read the onboarding and public key from the device and populate the characteristics
        await self.server.add_new_characteristic(constants.SERVICE_UUID, constants.ONBOARDING_KEY_UUID, char_flags, gateway_swarm.encode('utf-8'), permissions)
        await self.server.add_new_characteristic(constants.SERVICE_UUID, constants.PUBLIC_KEY_UUID, char_flags, gateway_swarm.encode('utf-8'), permissions)
        await self.server.add_new_characteristic(constants.SERVICE_UUID, constants.WIFI_MAC_UUID, char_flags, b'n/a', permissions)
        await self.server.add_new_characteristic(constants.SERVICE_UUID, constants.LIGHTS_UUID, char_flags, b'n/a', permissions)
        await self.server.add_new_characteristic(constants.SERVICE_UUID, constants.WIFI_SSID_UUID, char_flags, b'magic_ssid', permissions)
        await self.server.add_new_characteristic(constants.SERVICE_UUID, constants.ETHERNET_ONLINE, char_flags, b'false', permissions)

        wifi_services = wifi_services_pb2.wifi_services_v1()
        await self.server.add_new_characteristic(constants.SERVICE_UUID, constants.WIFI_SERVICES_UUID, char_flags, bytes(wifi_services.SerializeToString()), permissions)

        await self.server.add_new_characteristic(constants.SERVICE_UUID, constants.DIAGNOSTICS_UUID, char_flags, b'n/a', permissions)

        char_flags = GATTCharacteristicProperties.write | GATTCharacteristicProperties.read | GATTCharacteristicProperties.indicate
        permissions = GATTAttributePermissions.writeable | GATTAttributePermissions.readable
        await self.server.add_new_characteristic(constants.SERVICE_UUID, constants.ADD_GATEWAY_UUID, char_flags, b'', permissions)
        await self.server.add_new_characteristic(constants.SERVICE_UUID, constants.WIFI_CONNECT_UUID, char_flags, b'', permissions)

        logger.debug(f"Helium Service added with uuid {constants.SERVICE_UUID}")
        
        # Add srcful specific services
        char_flags = (GATTCharacteristicProperties.write_without_response | GATTCharacteristicProperties.write)
        permissions = GATTAttributePermissions.writeable
        await self.server.add_new_characteristic(constants.SERVICE_UUID, constants.SRCFUL_REQUEST_CHAR, char_flags, b'', permissions)
        
        char_flags = (
        GATTCharacteristicProperties.read | 
        GATTCharacteristicProperties.notify | 
        GATTCharacteristicProperties.indicate
        )
        permissions = GATTAttributePermissions.readable
        await self.server.add_new_characteristic(constants.SERVICE_UUID, constants.SRCFUL_RESPONSE_CHAR, char_flags, b'', permissions)
        
        logger.debug(f"Added srcful characteristics")

    def handle_read_request(self, characteristic: BlessGATTCharacteristic, **kwargs) -> bytearray:
        logger.debug(f"################################################")
        logger.debug(f"***** Read request {characteristic.uuid} {characteristic.value}")
        logger.debug(f"################################################")
        
        if characteristic.uuid == constants.WIFI_SERVICES_UUID:
            wifi_ssids = self.srcful_gw.get_wifi_ssids()
            logger.debug(f"Got wifi ssids {wifi_ssids}")

            services = wifi_services_pb2.wifi_services_v1()
            for ssid in wifi_ssids:
                if len(ssid) > 0:
                    services.services.append(ssid)

            characteristic.value = bytes(services.SerializeToString())
            self.server.update_value(constants.SERVICE_UUID, constants.WIFI_CONNECT_UUID)
        
        elif characteristic.uuid == constants.WIFI_SSID_UUID:
            # This characteristic is not being read by the app for some reason
            wifi_ssid = self.srcful_gw.get_connected_wifi_ssid()
            characteristic.value = bytes(wifi_ssid, "utf-8")
            self.server.update_value(constants.SERVICE_UUID, wifi_ssid)
            
        elif characteristic.uuid == constants.DIAGNOSTICS_UUID:
            self.update_diagnostics(characteristic)
            
        return characteristic.value 
    
            
    def handle_write_request(self, characteristic: BlessGATTCharacteristic, value: Any, **kwargs) -> bool:
        logger.debug(f"################################################")
        logger.debug(f"***** Write request {characteristic.uuid}, {value.decode('utf-8')}")
        logger.debug(f"################################################")
        if characteristic.uuid == constants.ADD_GATEWAY_UUID:
            
            # Seems like the timing of return here is critical. 
            # If the return is too early, the value is not updated
            add_gateway_txn = self.helium_gw.create_add_gateway_txn(value)

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
            
            self.srcful_gw.connect_wifi(value, update_status_callback)
            
            return True
        
        elif characteristic.uuid == constants.SRCFUL_REQUEST_CHAR:
            value = value.decode("utf-8")
            if self.srcful_gw.is_egwttp_request(value):
                logger.debug("Request received...")
                header, content = self.srcful_gw.parse_egwttp_request(value)
                logger.debug("Header: %s", header)
                logger.debug("Content: %s", content)
                if header["method"] == "GET" or header["method"] == "POST":
                    response = (
                        self.srcful_gw.request_get(header["path"], header["Offset"])
                        if header["method"] == "GET"
                        else self.srcful_gw.request_post(header["path"], content, header["Offset"])
                    )
                    response_char = self.server.get_characteristic(constants.SRCFUL_RESPONSE_CHAR)
                    response_char.value = response
                    logger.debug("Char value set to %s", response_char.value)
                    if self.server.update_value(constants.SERVICE_UUID, constants.SRCFUL_RESPONSE_CHAR):
                        logger.debug(
                            "Value updated sent notifications to %s",
                            str(len(self.server.app.subscribed_characteristics)),
                        )
                else:
                    logger.debug("Value not updated")
            else:
                logger.debug("Not an EGWTP request")
            
            return True
                        
        return False
    
    
    async def start_advertising(self):
        logging.info("Starting advertising")
        # we depend on that we are now on a bluez backend
        await self.app.start_advertising(self.server.adapter)
        # we don't create a new task as the button loop should be blocked until we have stoped advertising
        await self.stop_advertising()
        
    async def stop_advertising(self):
        logging.info("Stopping advertising in 3 minutes")
        await asyncio.sleep(60 * 3)
        logging.info("Stopping advertising...")

        # we depend on that we are now on a bluez backend
        adv = self.server.app.advertisements[0]
        await self.server.app.stop_advertising(self.server.adapter)

        # we also need to remove the exported advertisement endpoint
        # this is a hack to get bless start advertising to work
        self.server.app.bus.unexport(adv.path, adv)
        logging.info("Stopped advertising")