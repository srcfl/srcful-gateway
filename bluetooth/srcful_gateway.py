# This file include helper functions for the srcful gateway
import constants 
import requests
import time
import logging
import protos.wifi_connect_pb2 as wifi_connect_pb2
import threading
import egwttp
import constants
import time

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class SrcfulGateway:
    def __init__(self) -> None:
        # keep attempting to scan and get wifi info until it succeeds
        while True:
            try:
                self.scan_wifi() # Initial scan upon object creation
                self._fetch_network_info() # Fetch network info
                self._fetch_swarm_id() # Fetch swarm id
                break
            except Exception as e:
                logger.error(f"Error initializing srcful gateway: {e}")
                logger.warning("Retrying in 1 second...")
                time.sleep(1)

    def _fetch_network_info(self) -> None:
        try:
            response = requests.get(f"{constants.SRCFUL_GW_API_ENDPOINT}/api/network/address", timeout=10)
            if response.status_code == 200:
                network_json = response.json()
                # We should probably remove the hardcoded values
                self.eth_mac = network_json['eth0_mac']
                self.wifi_mac = network_json['wlan0_mac']
                
                try:
                    self.eth_ip = network_json['interfaces']['eth0']
                except:
                    self.eth_ip = "n/a"
                    logger.warning("Could not get eth ip")
                try:
                    self.wifi_ip = network_json['interfaces']['wlan0']
                except:
                    self.wifi_ip = "n/a"
                    logger.warning("Could not get wifi ipp")
                    
                logger.warning("Srcful Gateway initialized")
        except Exception as e:
            raise Exception(f"Error getting network info {e}")
        
        logger.info("Network info retrieved")
    
    def get_eth_ip(self) -> str:
        return self.eth_ip

    def get_eth_mac(self) -> str:
        return self.eth_mac

    def get_wifi_ip(self) -> str:
        return self.wifi_ip

    def get_wifi_mac(self) -> str:
        return self.wifi_mac

    def get_swarm_id(self) -> str:
        return self.swarm_id
    
    def _fetch_swarm_id(self) -> None:
        try:
            response = requests.get(f"{constants.SRCFUL_GW_API_ENDPOINT}/api/crypto", timeout=10)
            if response.status_code == 200:
                logger.info("Swarm id retrieved")
                self.swarm_id = response.json()['compactKey']
            else:
                logger.warning("Could not get swarm id")
                self.swarm_id = "n/a"
            
        except Exception as e:
            raise Exception(f"Error getting swarm id {e}")
    
    def scan_wifi(self) -> None:
        try:
            requests.get(f"{constants.SRCFUL_GW_API_ENDPOINT}/api/wifi/scan", timeout=10)
        except Exception as e:
            raise Exception(f"Error scanning wifi {e}")
        
        logger.info("Wifi scanned")
    
    def get_wifi_ssids(self) -> list:
        try:
            response = requests.get(f"{constants.SRCFUL_GW_API_ENDPOINT}/api/wifi" , timeout=10)
            if response.status_code == 200:
                return response.json()['ssids']
            else:
                return []
        except Exception as e:
            raise Exception(f"Error getting wifi ssids {e}")

    def get_connected_wifi_ssid(self) -> str:
        response = requests.get(f"{constants.SRCFUL_GW_API_ENDPOINT}/api/network", timeout=10)
        if response.status_code == 200:
            for connection in response.json()['connections']:
                if "wireless" in connection['connection']['type']:
                    return connection['connection']['id']
        else:
            raise Exception(f"Error getting connected wifi ssid {response.status_code}")

    def get_local_ip(self) -> str:
        return self.wifi_ip
    
    def is_wifi_connected(self, connections, ssid) -> bool:
        for connection in connections:
            if connection['connection']['id'] == ssid:
                return True
        return False
    
    def check_wifi_connection(self, wifi_ssid, update_status_callback, stop_event) -> None:
        while not stop_event.is_set():
            try:
                response = requests.get(f"{constants.SRCFUL_GW_API_ENDPOINT}/api/network", timeout=10)
                connections = response.json()['connections']
                if response.status_code == 200 and self.is_wifi_connected(connections, wifi_ssid):
                    update_status_callback(constants.WIFI_CONNECTED)
                    return
            except requests.RequestException:
                raise Exception(f"Error checking wifi connection {response.status_code}")
            
            time.sleep(3)

    def connect_wifi(self, value, update_status_callback) -> None:
        wifi_connect_details = wifi_connect_pb2.wifi_connect_v1()
        wifi_connect_details.ParseFromString(bytes(value))
        logger.info(f"WiFi connect SSID {wifi_connect_details.service}, PSK {wifi_connect_details.password}")

        post_body = {"ssid": wifi_connect_details.service, "psk": wifi_connect_details.password}

        response = requests.post(f"{constants.SRCFUL_GW_API_ENDPOINT}/api/wifi", json=post_body, timeout=10)

        if response.status_code == 200 and response.json()['status'] == "ok":
            update_status_callback(constants.WIFI_CONNECTING)
        
            stop_event = threading.Event()
            check_thread = threading.Thread(target=self.check_wifi_connection, args=(wifi_connect_details.service, update_status_callback, stop_event))
            check_thread.start()
            
            # Wait for a maximum of 60 seconds
            check_thread.join(timeout=60)
            
            if check_thread.is_alive():
                stop_event.set()
                update_status_callback(constants.WIFI_ERROR)

        else:
            update_status_callback(constants.WIFI_ERROR)
        
    def is_egwttp_request(self, data) -> bool:
        return egwttp.is_request(data)
    
    def parse_egwttp_request(self, data) -> tuple[dict, str]:
        return egwttp.parse_request(data)
    
    def handle_response(self, path: str, method: str, reply: requests.Response, offset: int):
        egwttp_response = egwttp.construct_response(path, method, reply.text, offset)
        logger.debug("Reply: %s", egwttp_response)
        return egwttp_response

    def request_get(self, path: str, offset: int) -> bytes:
        return self.handle_response(path, "GET", requests.get(constants.SRCFUL_GW_API_ENDPOINT + path, timeout=constants.SRCFUL_GW_API_REQUEST_TIMEOUT), offset)

    def request_post(self, path: str, content: str, offset: int) -> bytes:
        return self.handle_response(path, "POST", requests.post(constants.SRCFUL_GW_API_ENDPOINT + path, data=content, timeout=constants.SRCFUL_GW_API_REQUEST_TIMEOUT), offset)