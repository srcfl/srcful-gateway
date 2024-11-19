import logging
import base58
import requests
import constants
import protos.add_gateway_pb2 as add_gateway_pb2
import json
import time

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class HeliumGateway:
    def __init__(self):
        logger.warning("Initializing Helium Gateway...")
        self.animal_name = ""
        self.payer_name = ""
        self.payer_address = ""
        self.fetch_animal_name()
        
    def fetch_animal_name(self) -> None:
        """
        Fetch the animal name from the gateway-rs API
        """
        try:        
            url = f"{constants.HELIUM_API_ENDPOINT}/name"
            response = requests.get(url)
            logger.debug(f"Response: {response.json()}")
            self.animal_name = response.json()['name']
        except Exception as e:
            logger.error(f"Error fetching animal name: {e}")
            self.animal_name = "Unknown"
    
    def create_add_gateway_txn(self, value) -> bytes:
        """
        Create an add gateway transaction
        https://docs.helium.com/hotspot-makers/become-a-maker/hotspot-integration-testing/#generate-an-add-hotspot-transaction
        """
        logger.debug(f"Add gateway, Value: {value}")

        # Parse and extract gateway details
        add_gw_details = self._parse_gateway_details(value)
        
        # Prepare payload for API request
        payload = self._prepare_payload(add_gw_details)
        
        # Send API request and process response
        return self._send_api_request(payload)

    def _parse_gateway_details(self, value):
        """
        Parse the gateway details from the value
        """
        byte_data = bytes(value)
        add_gw_details = add_gateway_pb2.add_gateway_v1()
        add_gw_details.ParseFromString(byte_data)
        
        logger.debug(f"Add gateway details: {add_gw_details}")
        
        owner = base58.b58decode_check(add_gw_details.owner)[1:]
        owner_encoded = base58.b58encode(owner[1:]).decode('utf-8')
        
        logger.debug(f"Encoded owner: {owner_encoded}")
        logger.debug(f"Fee: {add_gw_details.fee}")
        logger.debug(f"Amount: {add_gw_details.amount}")
        
        return owner_encoded

    def _prepare_payload(self, owner):
        """
        Prepare the payload for the API request
        """
        return {
            "owner": owner,
            "mode": "full",
            "payer": self.payer_address if self.payer_address else owner
        }

    def _send_api_request(self, payload):
        """
        Send the API request
        """
        url = f"{constants.HELIUM_API_ENDPOINT}/add_gateway"
        headers = {'Content-Type': 'application/json'}
        
        json_payload = json.dumps(payload)
        logger.debug(f"Json payload {json_payload}")
        
        response = requests.post(url, json=json_payload, headers=headers)
        response_json = response.json()
        
        logger.debug(f"Response: {response_json}")

        if response.status_code == 200:
            txn = response_json['txn']
            logger.debug("Returning txn %s", txn)
            return txn
        else:
            logger.debug(f"Failed to add gateway {response.text}")
            return None
        
    def fetch_payer(self, gateway_address: str):
        """
        Fetch the payer's address and name for a given gateway address
        """
        try:
            maker_id = self._get_maker_id(gateway_address)
            if not maker_id:
                return

            maker = self._get_maker_info(maker_id)
            if not maker:
                return

            self._set_payer_info(maker)
        except Exception as e:
            self.payer_address = "Unknown"
            self.payer_name = "Unknown"   
            logger.error(f"Error fetching payer: {e}")

    def _get_maker_id(self, gateway_address: str) -> str:
        """Get the maker ID for the given gateway address"""
        hotspot_url = f"{constants.HELIUM_ONBOARDING_ENDPOINT}/api/v2/hotspots/{gateway_address}"
        response = requests.get(hotspot_url)
        
        if response.status_code != 200:
            return None

        hotspot_data = response.json()
        return hotspot_data.get("data", {}).get("makerId")

    def _get_maker_info(self, maker_id: str) -> dict:
        """Get the maker's information based on the maker ID"""
        makers_url = f"{constants.HELIUM_ONBOARDING_ENDPOINT}/api/v2/makers"
        makers_response = requests.get(makers_url)
        
        if makers_response.status_code != 200:
            return None

        makers_data = makers_response.json()
        makers_cache = makers_data.get("data", [])
        return next((m for m in makers_cache if m["id"] == maker_id), None)

    def _set_payer_info(self, maker: dict):
        """Set the payer's name and address from the maker information"""
        payer_name = maker.get("name")
        payer_address = maker.get("solanaAddress")
        
        logger.info(f"Payer name: {payer_name}")
        logger.info(f"Payer address: {payer_address}")
        
        if payer_address:
            self.payer_address = payer_address
            self.payer_name = payer_name