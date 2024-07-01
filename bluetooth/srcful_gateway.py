# This file include helper functions for the srcful gateway
import constants 
import requests
import time
import logging
import protos.wifi_connect_pb2 as wifi_connect_pb2
import threading
from typing import Any


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class SrcfulGateway:

    def __init__(self) -> None:
        self.scan_wifi() # Initial scan upon object creation
        network_json = self.get_network_info()

        # We should probably remove the hardcoded values
        self.eth_ip = network_json['interfaces']['eth0']
        self.eth_mac = network_json['eth0_mac']
        self.wifi_ip = network_json['interfaces']['wlan0']
        self.wifi_mac = network_json['wlan0_mac']

    def get_network_info(self) -> None:
        try:
            response = requests.get(f"{constants.SRCFUL_GW_API_ENDPOINT}/network/address", timeout=10)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.error(f"Error getting mac {e}")
    
    def get_eth_ip(self) -> str:
        return self.eth_ip

    def get_eth_mac(self) -> str:
        return self.eth_mac

    def get_wifi_ip(self) -> str:
        return self.wifi_ip

    def get_wifi_mac(self) -> str:
        return self.wifi_mac

    def get_swarm_id(self) -> str:
        try:
            response = requests.get(f"{constants.SRCFUL_GW_API_ENDPOINT}/crypto", timeout=10)
            if response.status_code == 200:
                return response.json()['compactKey']
            else:
                return "n/a"
        except Exception as e:
            logger.error(f"Error getting swarm id {e}")
            return "n/a"

    def scan_wifi(self) -> None:
        try:
            requests.get(f"{constants.SRCFUL_GW_API_ENDPOINT}/wifi/scan", timeout=10)
        except Exception as e:
            logger.error(f"Error scanning wifi {e}")
            return "n/a"
    
    def get_wifi_ssids(self) -> list:
        try:
            response = requests.get(f"{constants.SRCFUL_GW_API_ENDPOINT}/wifi" , timeout=10)
            if response.status_code == 200:
                return response.json()['ssids']
            else:
                return []
        except Exception as e:
            logger.error(f"Error getting wifi ssids {e}")
            return []

    def get_connected_wifi_ssid(self) -> str:
        response = requests.get(f"{constants.SRCFUL_GW_API_ENDPOINT}/network", timeout=10)
        if response.status_code == 200:
            for connection in response.json()['connections']:
                if "wireless" in connection['connection']['type']:
                    return connection['connection']['id']
        else:
            return "n/a"

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
                response = requests.get(f"{constants.SRCFUL_GW_API_ENDPOINT}/network", timeout=10)
                connections = response.json()['connections']
                if response.status_code == 200 and self.is_wifi_connected(connections, wifi_ssid):
                    update_status_callback(constants.WIFI_CONNECTED)
                    return
            except requests.RequestException:
                pass
            
            time.sleep(3)

    def connect_wifi(self, value, update_status_callback) -> None:
        wifi_connect_details = wifi_connect_pb2.wifi_connect_v1()
        wifi_connect_details.ParseFromString(bytes(value))
        logger.info(f"WiFi connect SSID {wifi_connect_details.service}, PSK {wifi_connect_details.password}")

        post_body = {"ssid": wifi_connect_details.service, "psk": wifi_connect_details.password}

        response = requests.post(f"{constants.SRCFUL_GW_API_ENDPOINT}/wifi", json=post_body, timeout=10)

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
        
