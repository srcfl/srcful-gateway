import logging
import dbus # Do we really need dbus ? 
import base58
import requests
import constants
import protos.add_gateway_pb2 as add_gateway_pb2


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class HeliumGateway:
    def __init__(self):
        logger.warning("Helium Gateway initialized")
        pass

    def bytes_to_dbus_byte_array(self, str) -> list[dbus.Byte]:
        byte_array = []

        for c in str:
            byte_array.append(dbus.Byte(c))

        return byte_array

    def bytes_to_hex_string(self, byte_data) -> str:
        return ''.join(f'{byte:02x}' for byte in byte_data)

    def create_add_gateway_txn(self, value) -> bytes:
       # https://docs.helium.com/hotspot-makers/become-a-maker/hotspot-integration-testing/#generate-an-add-hotspot-transaction

        logger.debug(f"Add gateway, Value: {value}")

        # Convert bytearray to bytes
        byte_data = bytes(value)

        # Create an instance of the add_gateway_v1 message
        add_gw_details = add_gateway_pb2.add_gateway_v1()

        # Parse the byte array into the message
        add_gw_details.ParseFromString(byte_data)

        owner = base58.b58decode_check(add_gw_details.owner)[1:]
        payer = base58.b58decode_check(add_gw_details.payer)[1:]

        logger.debug(f"Decoded owner {self.bytes_to_hex_string(owner[1:])}")
        logger.debug(f"Decoded payer {self.bytes_to_hex_string(payer[1:])}")

        wallet = base58.b58encode(owner[1:])
        logger.debug(f"Wallet: {wallet}")

        response = requests.post(f"{constants.HELIUM_API_ENDPOINT}/add_gateway", data=value)

        response_json = response.json()

        if response.status_code == 200:
            logger.debug(f"Response {response_json['txn']}")

            txn_bytes = base58.b58decode(response_json['txn'])

            return self.bytes_to_dbus_byte_array(txn_bytes)
        else:
            logger.debug(f"Failed to add gateway {response.text}")
            return None

