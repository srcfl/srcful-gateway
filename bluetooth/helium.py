import logging
import time
from typing import Any
from google.protobuf.json_format import MessageToJson
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
import base58
import ast
import time
import dbus


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(name=__name__)

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
WIFI_SSID_UUID = '7731de63-bc6a-4100-8ab1-89b2356b038b'
ethernet_online = 'e5866bd6-0288-4476-98ca-ef7da6b4d289'

assert_location_uuid = 'd435f5de-01a4-4e7d-84ba-dfd347f60275'
add_gatway_uuid = 'df3b16ca-c985-4da2-a6d2-9b9b9abdb858'
wifi_connect_uuid = '398168aa-0111-4ec0-b1fa-171671270608'

api_endpoint = "http://localhost:80/api"


# response = requests.get("http://localhost:3000/onboading_keys", timeout=10)
# if response.status_code == 200:
#     public_key = response.json()['key'].encode('utf-8')
#     onboarding_key = response.json()['onboarding'].encode('utf-8')
#     name = response.json()['name'].encode('utf-8')

# logger.debug(f"Public key {public_key}")
# logger.debug(f"Onboarding key {onboarding_key}")
# logger.debug(f"Name {name}")

def get_wifi_ssids():
    # request the ssids fro the server
    response = requests.get(f"{api_endpoint}/wifi" , timeout=10)
    if response.status_code == 200:
        return response.json()['ssids']
    else:
        return []
    
def get_connected_wifi_ssid():
    response = requests.get(f"{api_endpoint}/network", timeout=10)
    if response.status_code == 200:
        for connection in response.json()['connections']:
            if "wireless" in connection['connection']['type']:
                return connection['connection']['id']
    else:
        return "n/a"
    
def scan_wifi():
    try:
        requests.get(f"{api_endpoint}/wifi/scan", timeout=10)
    except Exception as e:
        logger.error(f"Error scanning wifi {e}")
        return


def read_request(server: BlessServer, characteristic: BlessGATTCharacteristic, **kwargs) -> bytearray:
    # set the value of the characteristic
    logger.debug(f"################################################")
    logger.debug(f"***** Read request {characteristic.uuid}")
    logger.debug(f"################################################")
    if characteristic.uuid == wifi_services_uuid:
        wifi_ssids = get_wifi_ssids()
        logger.debug(f"Got wifi ssids {wifi_ssids}")

        services = wifi_services_pb2.wifi_services_v1()
        for ssid in wifi_ssids:
            if len(ssid) > 0:
                services.services.append(ssid)

        characteristic.value = bytes(services.SerializeToString())
        server.update_value(service_uuid, wifi_services_uuid)

        # we start a rescan so we can get the latest wifi networks the next time we read
        threading.Thread(target=scan_wifi).start()
    if characteristic.uuid == WIFI_SSID_UUID:
        logger.debug(f"Getting current wifi ssid")
        wifi_ssid = get_connected_wifi_ssid()
        characteristic.value = bytes(wifi_ssid, "utf-8")
        server.update_value(service_uuid, wifi_ssid)


def write_request(server: BlessServer, characteristic: BlessGATTCharacteristic, value: Any, **kwargs) -> bool:
    logger.debug(f"################################################")
    logger.debug(f"***** Write request {characteristic.uuid}, {value.decode('utf-8')}")
    logger.debug(f"################################################")
    if characteristic.uuid == add_gatway_uuid:
        threading.Thread(target=add_gateway, args=(server, characteristic, value,)).start()
        time.sleep(1)
        return True
    elif characteristic.uuid == wifi_connect_uuid:
        threading.Thread(target=connect_wifi, args=(server, characteristic, value,)).start()
        return True

    return False
    

async def add_custom_service(server: BlessServer):  
    await server.add_new_service(service_uuid)

    # tell the server to scan for networks
    threading.Thread(target=scan_wifi).start()

    char_flags = GATTCharacteristicProperties.read
    permissions = GATTAttributePermissions.readable

    await server.add_new_characteristic(service_uuid, onboarding_key_uuid, char_flags, bytes('112qfPXyyXmH7miY5UXa4HFuXwF4PdrfU17kftKpk2a2SpKpxtsh', 'utf-8'), permissions)
    await server.add_new_characteristic(service_uuid, public_key_uuid, char_flags, bytes('112qfPXyyXmH7miY5UXa4HFuXwF4PdrfU17kftKpk2a2SpKpxtsh', 'utf-8'), permissions)
    await server.add_new_characteristic(service_uuid, wifi_mac_uuid, char_flags, b'wifi_mac', permissions)
    await server.add_new_characteristic(service_uuid, lights_uuid, char_flags, b'n/a', permissions)
    await server.add_new_characteristic(service_uuid, WIFI_SSID_UUID, char_flags, b'magic_ssid', permissions)
    await server.add_new_characteristic(service_uuid, ethernet_online, char_flags, b'false', permissions)

    services = wifi_services_pb2.wifi_services_v1()

    await server.add_new_characteristic(service_uuid, wifi_services_uuid, char_flags, bytes(services.SerializeToString()), permissions)

    services = diagnostics_pb2.diagnostics_v1()
    services.diagnostics['Name:\n'] = 'AA'
    services.diagnostics['\nPublic Key:\n'] = 'AA'
    services.diagnostics['\nOnboarding key:\n'] = 'AA'

    await server.add_new_characteristic(service_uuid, diagnostics_uuid, char_flags, bytes(services.SerializeToString()), permissions)


    char_flags = GATTCharacteristicProperties.write | GATTCharacteristicProperties.read | GATTCharacteristicProperties.indicate
    permissions = GATTAttributePermissions.writeable | GATTAttributePermissions.readable
    await server.add_new_characteristic(service_uuid, add_gatway_uuid, char_flags, b'', permissions)

    await server.add_new_characteristic(service_uuid, wifi_connect_uuid, char_flags, b'', permissions)

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



def is_connected(connections, ssid):
    for connection in connections:
        if connection['connection']['id'] == ssid:
            return True
    return False


def connect_wifi(server: BlessServer, characteristic: BlessGATTCharacteristic, value):
    logger.debug(f"Connect wifi")
    wifi_connect_details = wifi_connect_pb2.wifi_connect_v1()
    wifi_connect_details.ParseFromString(bytes(value))

    logger.info(f"wifi connect ssid {wifi_connect_details.service}, password {wifi_connect_details.password}")
    
    response = requests.post(f"{api_endpoint}/wifi", json={"ssid": wifi_connect_details.service, "psk": wifi_connect_details.password}, timeout=10)
    if response.status_code == 200 and response.json()['status'] == "ok":
        characteristic.value = bytes(WIFI_CONNECTING, "utf-8")
        server.update_value(service_uuid, wifi_connect_uuid)

        for _ in range(10):
            time.sleep(5)

            response = requests.get(f"{api_endpoint}/network", json={"ssid": wifi_connect_details.service, "psk": wifi_connect_details.password}, timeout=10)
            if response.status_code == 200 and is_connected(response.json()['connections'], wifi_connect_details.service):
                
                characteristic.value = bytes(WIFI_CONNECTED, "utf-8")
                server.update_value(service_uuid, wifi_connect_uuid)
                return

    # if we get here somethign went wrong
    characteristic.value = bytes(WIFI_ERROR, "utf-8")
    server.update_value(service_uuid, wifi_connect_uuid)


def bytes_to_hex_string(byte_data):
    return ''.join(f'{byte:02x}' for byte in byte_data)


def bytes_to_dbus_byte_array(str):
    byte_array = []

    for c in str:
        byte_array.append(dbus.Byte(c))

    return byte_array

def add_gateway(server: BlessServer, characteristic: BlessGATTCharacteristic, value):
    

    # https://docs.helium.com/hotspot-makers/become-a-maker/hotspot-integration-testing/#generate-an-add-hotspot-transaction

    logger.debug(f"Add gateway") 
    logger.debug(f"Value: {value}")

    # Convert bytearray to bytes
    byte_data = bytes(value)

    # Create an instance of the add_gateway_v1 message
    add_gw_details = add_gateway_pb2.add_gateway_v1()

    # Parse the byte array into the message
    add_gw_details.ParseFromString(byte_data)

    owner = base58.b58decode_check(add_gw_details.owner)[1:]
    payer = base58.b58decode_check(add_gw_details.payer)[1:]

    logger.debug(f"Decoded owner {bytes_to_hex_string(owner[1:])}")
    logger.debug(f"Decoded payer {bytes_to_hex_string(payer[1:])}")

    wallet = base58.b58encode(owner[1:])
    logger.debug(f"Wallet: {wallet}")

    response = requests.post("http://localhost:3000/add_gateway", data=value)
    
    print()
    response_json = response.json()
    


    if response.status_code == 200:
        logger.debug(f"Response {response_json['txn']}")

        txn_bytes = base58.b58decode(response_json['txn'])

        characteristic.value = bytes_to_dbus_byte_array(txn_bytes)

        if server.update_value(service_uuid, add_gatway_uuid):
            logger.debug(f"Char updated, dbus bytes: {bytes_to_dbus_byte_array(txn_bytes)}")
            logger.debug(f"Char updated, value set to {characteristic.value}")
        else:
            logger.debug(f"Failed to update value")

    else:
        logger.debug(f"Failed to add gateway {response.text}")

    

