# This file includes helper functions for the Helium gateway-rs 
import dbus # Do we really need dbus ? 
import base58
import logging
import requests
import constants 
import protos.add_gateway_pb2 as add_gateway_pb2
from bless import (  # type: ignore
    BlessServer,
    BlessGATTCharacteristic
)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(name=__name__)


def bytes_to_dbus_byte_array(str):
    byte_array = []

    for c in str:
        byte_array.append(dbus.Byte(c))

    return byte_array

def bytes_to_hex_string(byte_data):
    return ''.join(f'{byte:02x}' for byte in byte_data)

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

        if server.update_value(constants.SERVICE_UUID, constants.ADD_GATEWAY_UUID):
            logger.debug(f"Char updated, dbus bytes: {bytes_to_dbus_byte_array(txn_bytes)}")
            logger.debug(f"Char updated, value set to {characteristic.value}")
        else:
            logger.debug(f"Failed to update value")

    else:
        logger.debug(f"Failed to add gateway {response.text}")

    