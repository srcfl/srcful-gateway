import asyncio
import logging
import json
import base58
import time
from typing import Any

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(name=__name__)


import protos

from bless import (  # type: ignore
    BlessServer,
    BlessGATTCharacteristic,
    GATTCharacteristicProperties,
    GATTAttributePermissions,
)


import protos.wifi_services_pb2 as wifi_services_pb2
import protos.add_gateway_pb2 as add_gateway_pb2
import protos.wifi_connect_pb2 as wifi_connect_pb2
import protos.diagnostics_pb2 as diagnostics_pb2
import threading
import requests

WIFI_CONNECTING = "connecting"
WIFI_CONNECTED = "connected"
WIFI_ERROR = "error"


service_uuid = "0fda92b2-44a2-4af2-84f5-fa682baa2b8d"

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


def get_wifi_ssids():
    # request the ssids fro the server
    response = requests.get("http://localhost:5000/api/wifi" , timeout=10)
    if response.status_code == 200:
        return response.json()['ssids']
    else:
        return []


def read_request(server: BlessServer, characteristic: BlessGATTCharacteristic, **kwargs) -> bytearray:
    # set the value of the characteristic
    if characteristic.uuid == wifi_services_uuid:
        wifi_ssids = get_wifi_ssids()
        logger.debug(f"Got wifi ssids {wifi_ssids}")

        services = wifi_services_pb2.wifi_services_v1()
        for ssid in wifi_ssids:
            services.services.append(ssid)

        characteristic.value = bytes(services.SerializeToString())
        server.update_value(service_uuid, wifi_services_uuid)


def write_request(server: BlessServer, characteristic: BlessGATTCharacteristic, value: Any, **kwargs) -> bool:
    logger.debug(f"Writing!!")
    if characteristic.uuid == add_gatway:
        threading.Thread(target=add_gateway, args=(server, characteristic, value,)).start()
        return True
    elif characteristic.uuid == wifi_connect:
        
        threading.Thread(target=connect_wifi, args=(server, characteristic, value,)).start()
        return True

    return False

async def add_custom_service(server: BlessServer):
    await server.add_new_service(service_uuid)

    char_flags = GATTCharacteristicProperties.read
    permissions = GATTAttributePermissions.readable

    await server.add_new_characteristic(service_uuid, onboarding_key_uuid, char_flags, b'11TqqVzycXK5k49bXbmcUcSne91krq7v3VSQCfDXr', permissions)
    await server.add_new_characteristic(service_uuid, public_key_uuid, char_flags, b'117ei8D1Bk2kYqWNjSFuLgg3BrtTNSTi2tt14LRUFgt', permissions)
    await server.add_new_characteristic(service_uuid, wifi_mac_uuid, char_flags, b'wifi_mac', permissions)
    await server.add_new_characteristic(service_uuid, lights_uuid, char_flags, b'n/a', permissions)
    await server.add_new_characteristic(service_uuid, wifi_ssid, char_flags, b'magic_ssid', permissions)
    await server.add_new_characteristic(service_uuid, ethernet_online, char_flags, b'false', permissions)

    services = wifi_services_pb2.wifi_services_v1()
    services.services.append("nisse")
    services.services.append("kalle")
    services.services.append("pelle")

    await server.add_new_characteristic(service_uuid, wifi_services_uuid, char_flags, bytes(services.SerializeToString()), permissions)

    services = diagnostics_pb2.diagnostics_v1()
    services.diagnostics['test'] = 'testing'
    services.diagnostics['test2'] = 'testing2'
    services.diagnostics['test3'] = 'testing3'

    await server.add_new_characteristic(service_uuid, diagnostics_uuid, char_flags, bytes(services.SerializeToString()), permissions)


    char_flags = GATTCharacteristicProperties.write | GATTCharacteristicProperties.read | GATTCharacteristicProperties.indicate
    permissions = GATTAttributePermissions.writeable | GATTAttributePermissions.readable
    await server.add_new_characteristic(service_uuid, add_gatway, char_flags, b'not supported', permissions)

    await server.add_new_characteristic(service_uuid, wifi_connect, char_flags, b'', permissions)

    logger.debug(f"Helium Service added with uuid {service_uuid}")


async def add_device_info_service(server: BlessServer):
    service_uuid = '0000180a-0000-1000-8000-00805f9b34fb'
    await server.add_new_service(service_uuid)
    
    #await server.setup_task
    #service = DeviceInfoService()
    #await service.init(server)
    #server.services[service._uuid] = service

    char_uuid = "00002A29-0000-1000-8000-00805F9B34FB"
    char_flags = GATTCharacteristicProperties.read
    permissions = GATTAttributePermissions.readable

    #characteristic: BlessGATTCharacteristicBlueZDBus = (
    #        DeviceInfoCharacteristic(char_uuid, "2A29", char_flags, permissions, b'Helium')
    #    )
    #await characteristic.init(service)
    #service.add_characteristic(characteristic)

    #service.add_characteristic(char_uuid, char_flags, b'Helium', permissions)
    await server.add_new_characteristic(service_uuid, char_uuid, char_flags, b'Helium Systems, Inc.', permissions)

    char_uuid = "00002A25-0000-1000-8000-00805F9B34FB"
    await server.add_new_characteristic(service_uuid, char_uuid, char_flags, b'6081F989E7BF', permissions)

    char_uuid = "00002A26-0000-1000-8000-00805F9B34FB"
    await server.add_new_characteristic(service_uuid, char_uuid, char_flags, b'2020.02.18.1', permissions)



def connect_wifi(server: BlessServer, characteristic: BlessGATTCharacteristic, value):
    logger.debug(f"Connect wifi")
    wifi_connect_details = wifi_connect_pb2.wifi_connect_v1()
    wifi_connect_details.ParseFromString(bytes(value))

    print(f"wifi connect ssid {wifi_connect_details.service}, password {wifi_connect_details.password}")
    characteristic.value = bytes(WIFI_CONNECTING, "utf-8")
    if server.update_value(service_uuid, wifi_connect):
        logger.debug(f"Char updated, value set to {characteristic.value}")
    else:
        logger.debug(f"Failed to update value")


    time.sleep(5)
    characteristic.value = bytes(WIFI_CONNECTED, "utf-8")
    if server.update_value(service_uuid, wifi_connect):
        logger.debug(f"Char updated, value set to {characteristic.value}")
    else:
        logger.debug(f"Failed to update value")

def bytes_to_hex_string(byte_data):
    return ''.join(f'{byte:02x}' for byte in byte_data)

def add_gateway(server: BlessServer, characteristic: BlessGATTCharacteristic, value):
    logger.debug(f"Add gateway") 
    add_gw_details = add_gateway_pb2.add_gateway_v1()
    add_gw_details.ParseFromString(bytes(value))

    print(f"add gateway owner {add_gw_details.owner}, fee {add_gw_details.fee} ")
    print(f"amount {add_gw_details.amount}, payer {add_gw_details.payer}")


    owner = base58.b58decode_check(add_gw_details.owner)[1:]
    payer = base58.b58decode_check(add_gw_details.payer)[1:]

    print(f"Decoded owner {bytes_to_hex_string(owner[1:])}")
    print(f"Decoded payer {bytes_to_hex_string(payer[1:])}")

    wallet = base58.b58encode(owner[1:])
    print(f"Wallet: {wallet}")


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
    if server.update_value(service_uuid, add_gatway):
        logger.debug(f"Char updated, value set to {characteristic.value}")
    else:
        logger.debug(f"Failed to update value")