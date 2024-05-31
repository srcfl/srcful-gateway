"""
Example for a BLE 4.0 Server
"""

import time
import sys
import logging
import asyncio
import threading
import json
from uuid import UUID

from typing import Any, Union

import protos.wifi_services_pb2 as wifi_services_pb2
import protos.add_gateway_pb2 as add_gateway_pb2
import protos.wifi_connect_pb2 as wifi_connect_pb2
import protos.diagnostics_pb2 as diagnostics_pb2

from bless import (  # type: ignore
    BlessServer,
    BlessGATTCharacteristic,
    GATTCharacteristicProperties,
    GATTAttributePermissions,
)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(name=__name__)

# NOTE: Some systems require different synchronization methods.
trigger: Union[asyncio.Event, threading.Event]
if sys.platform in ["darwin", "win32"]:
    trigger = threading.Event()
else:
    trigger = asyncio.Event()

helium_service_uuid = "0fda92b2-44a2-4af2-84f5-fa682baa2b8d"

onboarding_key_uuid = 'd083b2bd-be16-4600-b397-61512ca2f5ad'
public_key_uuid = '0a852c59-50d3-4492-bfd3-22fe58a24f01'
wifi_services_uuid = 'd7515033-7e7b-45be-803f-c8737b171a29'
diagnostics_uuid = 'b833d34f-d871-422c-bf9e-8e6ec117d57e'
wifi_mac_uuid = '9c4314f2-8a0c-45fd-a58d-d4a7e64c3a57'
lights_uuid = '180efdef-7579-4b4a-b2df-72733b7fa2fe'
wifi_ssid = '7731de63-bc6a-4100-8ab1-89b2356b038b'
ethernet_online = 'e5866bd6-0288-4476-98ca-ef7da6b4d289'

assert_location = 'd435f5de-01a4-4e7d-84ba-dfd347f60275'
add_gatway = 'df3b16ca-c985-4da2-a6d2-9b9b9abdb858'
wifi_connect = '398168aa-0111-4ec0-b1fa-171671270608'


WIFI_CONNECTING = "connecting"
WIFI_CONNECTED = "connected"
WIFI_ERROR = "error"

SERVER: BlessServer = None

def connect_wifi(characteristic: BlessGATTCharacteristic, value):
    logger.debug(f"Connect wifi")
    wifi_connect_details = wifi_connect_pb2.wifi_connect_v1()
    wifi_connect_details.ParseFromString(bytes(value))

    print(f"wifi connect ssid {wifi_connect_details.service}, password {wifi_connect_details.password}")
    characteristic.value = bytes(WIFI_CONNECTING, "utf-8")
    if SERVER.update_value(helium_service_uuid, wifi_connect):
        logger.debug(f"Char updated, value set to {characteristic.value}")
    else:
        logger.debug(f"Failed to update value")


    time.sleep(5)
    characteristic.value = bytes(WIFI_CONNECTED, "utf-8")
    if SERVER.update_value(helium_service_uuid, wifi_connect):
        logger.debug(f"Char updated, value set to {characteristic.value}")
    else:
        logger.debug(f"Failed to update value")

def add_gateway(characteristic: BlessGATTCharacteristic, value):
    logger.debug(f"Add gateway") 
    add_gw_details = add_gateway_pb2.add_gateway_v1()
    add_gw_details.ParseFromString(bytes(value))

    print(f"add gateway owner {add_gw_details.owner}, fee {add_gw_details.fee} ")
    print(f"amount {add_gw_details.amount}, payer {add_gw_details.payer}")

    # https://docs.helium.com/hotspot-makers/become-a-maker/hotspot-integration-testing/#generate-an-add-hotspot-transaction
    test_response = {
        "address": "11TL62V8NYvSTXmV5CZCjaucskvNR1Fdar1Pg4Hzmzk5tk2JBac",
        "fee": 65000,
        "mode": "full",
        "owner": "14GWyFj9FjLHzoN3aX7Tq7PL6fEg4dfWPY8CrK8b9S5ZrcKDz6S",
        "payer": "138LbePH4r7hWPuTnK6HXVJ8ATM2QU71iVHzLTup1UbnPDvbxmr",
        "staking fee": 4000000,
        "txn": "CrkBCiEBrlImpYLbJ0z0hw5b4g9isRyPrgbXs9X+RrJ4pJJc9MkSIQA7yIy7F+9oPYCTmDz+v782GMJ4AC+jM+VfjvUgAHflWSJGMEQCIGfugfLkXv23vJcfwPYjLlMyzYhKp+Rg8B2YKwnsDHaUAiASkdxUO4fdS33D7vyid8Tulizo9SLEL1lduyvda9YVRCohAa5SJqWC2ydM9IcOW+IPYrEcj64G17PV/kayeKSSXPTJOMCEPUDo+wM="
    }
    
    characteristic.value = bytes(json.dumps(test_response), "utf-8")
    if SERVER.update_value(helium_service_uuid, add_gatway):
        logger.debug(f"Char updated, value set to {characteristic.value}")
    else:
        logger.debug(f"Failed to update value")
    


def read_request(characteristic: BlessGATTCharacteristic, **kwargs) -> bytearray:
    logger.debug(f"Reading {characteristic.value}")
    return characteristic.value


def write_request(characteristic: BlessGATTCharacteristic, value: Any, **kwargs):
    logger.debug(f"Writing!!")
    if characteristic.uuid == add_gatway:
        threading.Thread(target=add_gateway, args=(characteristic, value,)).start()
    elif characteristic.uuid == wifi_connect:
        
        threading.Thread(target=connect_wifi, args=(characteristic, value,)).start()

    else:
        characteristic.value = value
        logger.debug(f"Char value set to {characteristic.value}")
        if characteristic.value == b"\x0f":
            logger.debug("NICE")
            trigger.set()


async def add_helium_device_info_service(server: BlessServer):
    service_uuid = '0000180a-0000-1000-8000-00805f9b34fb'
    await server.add_new_service(service_uuid)

    char_uuid = "00002A29-0000-1000-8000-00805F9B34FB"
    char_flags = GATTCharacteristicProperties.read
    permissions = GATTAttributePermissions.readable
    await server.add_new_characteristic(service_uuid, char_uuid, char_flags, b'Helium', permissions)

    char_uuid = "00002A25-0000-1000-8000-00805F9B34FB"
    await server.add_new_characteristic(service_uuid, char_uuid, char_flags, b'6081F989E7BF', permissions)

    char_uuid = "00002A26-0000-1000-8000-00805F9B34FB"
    await server.add_new_characteristic(service_uuid, char_uuid, char_flags, b'2020.02.18.1', permissions)


async def add_helium_custom_service(server: BlessServer):
    await server.add_new_service(helium_service_uuid)

    char_flags = GATTCharacteristicProperties.read
    permissions = GATTAttributePermissions.readable
    

    await server.add_new_characteristic(helium_service_uuid, onboarding_key_uuid, char_flags, b'11TqqVzycXK5k49bXbmcUcSne91krq7v3VSQCfDXr', permissions)
    await server.add_new_characteristic(helium_service_uuid, public_key_uuid, char_flags, b'117ei8D1Bk2kYqWNjSFuLgg3BrtTNSTi2tt14LRUFgt', permissions)
    await server.add_new_characteristic(helium_service_uuid, wifi_mac_uuid, char_flags, b'wifi_mac', permissions)
    await server.add_new_characteristic(helium_service_uuid, lights_uuid, char_flags, b'n/a', permissions)
    await server.add_new_characteristic(helium_service_uuid, wifi_ssid, char_flags, b'magic_ssid', permissions)
    await server.add_new_characteristic(helium_service_uuid, ethernet_online, char_flags, b'false', permissions)

    services = wifi_services_pb2.wifi_services_v1()
    services.services.append("nisse")
    services.services.append("kalle")
    services.services.append("pelle")

    await server.add_new_characteristic(helium_service_uuid, wifi_services_uuid, char_flags, bytes(services.SerializeToString()), permissions)

    services = diagnostics_pb2.diagnostics_v1()
    services.diagnostics['test'] = 'testing'
    services.diagnostics['test2'] = 'testing2'
    services.diagnostics['test3'] = 'testing3'

    await server.add_new_characteristic(helium_service_uuid, diagnostics_uuid, char_flags, bytes(services.SerializeToString()), permissions)


    char_flags = GATTCharacteristicProperties.write | GATTCharacteristicProperties.read | GATTCharacteristicProperties.indicate
    permissions = GATTAttributePermissions.writeable | GATTAttributePermissions.readable
    await server.add_new_characteristic(helium_service_uuid, add_gatway, char_flags, b'not supported', permissions)

    await server.add_new_characteristic(helium_service_uuid, wifi_connect, char_flags, b'', permissions)


async def run(loop):
    trigger.clear()
    # Instantiate the server
    my_service_name = "Srcful Hotspot"
    global SERVER
    SERVER = BlessServer(name=my_service_name, loop=loop, name_overwrite=True)
    SERVER.read_request_func = read_request
    SERVER.write_request_func = write_request


    # device info service does not work on windows
    # await add_helium_device_info_service(SERVER)
    await add_helium_custom_service(SERVER)

    # Add Service
    my_service_uuid = "A07498CA-AD5B-474E-940D-16F1FBE7E8CD"
    await SERVER.add_new_service(my_service_uuid)

    # Add a Characteristic to the service
    my_char_uuid = "51FF12BB-3ED8-46E5-B4F9-D64E2FEC021B"
    char_flags = (
        GATTCharacteristicProperties.read
        | GATTCharacteristicProperties.write
        | GATTCharacteristicProperties.indicate
    )
    permissions = GATTAttributePermissions.readable | GATTAttributePermissions.writeable
    await SERVER.add_new_characteristic(
        my_service_uuid, my_char_uuid, char_flags, None, permissions
    )

    logger.debug(SERVER.get_characteristic(my_char_uuid))
    await SERVER.start()
    logger.debug("Advertising")
    logger.info(f"Write '0xF' to the advertised characteristic: {my_char_uuid}")
    try:
        if trigger.__module__ == "threading":
            trigger.wait()
        else:
            await trigger.wait()
    except KeyboardInterrupt:
        print("Server stopped by user")
        await SERVER.stop()
        trigger.set()

    if not trigger.is_set():
        await asyncio.sleep(2)
        logger.debug("Updating")
        SERVER.get_characteristic(my_char_uuid)
        SERVER.update_value(my_service_uuid, "51FF12BB-3ED8-46E5-B4F9-D64E2FEC021B")
        await asyncio.sleep(5)
        await SERVER.stop()


try:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(loop))
except KeyboardInterrupt:
    SERVER.stop()
    print("Server stopped by user")