import logging
import dbus # Do we really need dbus ? 
import base58
import requests
import constants
import protos.add_gateway_pb2 as add_gateway_pb2
import json

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class HeliumGateway:
    def __init__(self):
        logger.warning("Helium Gateway initialized")
        self.payer_name = ""
        self.payer_address = "" # This is the payer's solana address
        pass

    def bytes_to_dbus_byte_array(self, str) -> list[dbus.Byte]:
        byte_array = []

        for c in str:
            byte_array.append(dbus.Byte(c))

        return byte_array

    def bytes_to_hex_string(self, byte_data) -> str:
        return ''.join(f'{byte:02x}' for byte in byte_data)

    async def create_add_gateway_txn(self, value) -> bytes:
       # https://docs.helium.com/hotspot-makers/become-a-maker/hotspot-integration-testing/#generate-an-add-hotspot-transaction

        logger.debug(f"Add gateway, Value: {value}")

        # Convert bytearray to bytes
        byte_data = bytes(value)

        # Create an instance of the add_gateway_v1 message
        add_gw_details = add_gateway_pb2.add_gateway_v1()

        # Parse the byte array into the message
        add_gw_details.ParseFromString(byte_data)
        
        logger.debug(f"Add gateway details: {add_gw_details}")
    
        owner = base58.b58decode_check(add_gw_details.owner)[1:]
        payer = base58.b58decode_check(add_gw_details.payer)[1:]
        fee = add_gw_details.fee
        amount = add_gw_details.amount
        
        # Encode the owner and payer
        owner_encoded = base58.b58encode(owner[1:])
        payer_encoded = base58.b58encode(payer[1:])

        logger.debug(f"Encoded owner {owner_encoded}")
        logger.debug(f"Encoded payer {payer_encoded}")
        
        owner = owner_encoded.decode('utf-8')
        payer = await self.fetch_payer(owner)
        
        payload = {
            "owner": owner,
            "mode": "full",
            "payer": payer
        }
        
        url = f"{constants.HELIUM_API_ENDPOINT}/add_gateway"
        headers = {'Content-Type': 'application/json'}
        
        json_payload = json.dumps(payload)
        logger.debug(f"Json payload {json_payload}")
        
        response = requests.post(url, json=json_payload, headers=headers)
        
        response_json = response.json()
        
        logger.debug(f"Response: {response_json}")

        if response.status_code == 200:
            
            txn = response_json['txn'] # This is the base64 encoded txn returned by gateway-rs
            
            logger.debug("Returning txn %s", txn)
            return txn
        else:
            logger.debug(f"Failed to add gateway {response.text}")
            return None
        
        
    async def fetch_payer(self, gateway_address: str) -> str:
        try:
            # Step 1: Get the maker ID for the gateway
            hotspot_url = f"{constants.HELIUM_ONBOARDING_ENDPOINT}/api/v2/hotspots/{gateway_address}"
            
            response = requests.get(hotspot_url)
            
            if response.status_code != 200:
                return None

            hotspot_data = response.json()
            maker_id = hotspot_data.get("data", {}).get("makerId")

            if not maker_id:
                return None

            # Step 2: Get the maker's SOL wallet address
            makers_url = f"{constants.HELIUM_ONBOARDING_ENDPOINT}/api/v2/makers"
            makers_response = requests.get(makers_url)
            
            if makers_response.status_code != 200:
                return None

            makers_data = makers_response.json()
            makers_cache = makers_data.get("data", [])

            maker = next((m for m in makers_cache if m["id"] == maker_id), None)
            
            if not maker:
                return None

            payer_name = maker.get("name")
            payer_address = maker.get("solanaAddress")
            
            logger.debug(f"Payer name: {payer_name}")
            logger.debug(f"Payer address: {payer_address}")
            
            if not payer_address:
                return None

            self.payer_name = payer_name
            self.payer_address = payer_address

            return payer_address
        except Exception as e:
            logger.error(f"Error fetching payer {e}")
            self.payer_name = ""
            self.payer_address = ""
            return None
