# This file include helper functions for the srcful gateway
import constants 
import requests
import time
import logging
from bless import (  # type: ignore
    BlessServer,
    BlessGATTCharacteristic
)
import protos.wifi_connect_pb2 as wifi_connect_pb2
import threading

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(name=__name__)


def scan_wifi():
    try:
        requests.get(f"{constants.API_ENDPOINT}/wifi/scan", timeout=10)
    except Exception as e:
        logger.error(f"Error scanning wifi {e}")
        return
    
def get_wifi_ssids():
    try:
        response = requests.get(f"{constants.API_ENDPOINT}/wifi" , timeout=10)
        if response.status_code == 200:
          return response.json()['ssids']
        else:
            return []
    except Exception as e:
        logger.error(f"Error getting wifi ssids {e}")
        return []

def get_connected_wifi_ssid():
    response = requests.get(f"{constants.API_ENDPOINT}/network", timeout=10)
    if response.status_code == 200:
        for connection in response.json()['connections']:
            if "wireless" in connection['connection']['type']:
                return connection['connection']['id']
    else:
        return "n/a"

def get_ip():
    try:
        response = requests.get(f"{constants.API_ENDPOINT}/network/address", timeout=10)
        if response.status_code == 200:
            logger.debug(f"Got ip {response.json()['address']}")
            return response.json()['address']
        else:
            return "n/a"
        
    except Exception as e:
        logger.error(f"Error getting ip {e}")
        return "n/a"
    
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
    
    response = requests.post(f"{constants.API_ENDPOINT}/wifi", json={"ssid": wifi_connect_details.service, "psk": wifi_connect_details.password}, timeout=10)
    if response.status_code == 200 and response.json()['status'] == "ok":
        characteristic.value = bytes(constants.WIFI_CONNECTING, "utf-8")
        server.update_value(constants.SERVICE_UUID, constants.WIFI_CONNECT_UUID)

        for _ in range(10):
            time.sleep(5)

            response = requests.get(f"{constants.API_ENDPOINT}/network", json={"ssid": wifi_connect_details.service, "psk": wifi_connect_details.password}, timeout=10)
            if response.status_code == 200 and is_connected(response.json()['connections'], wifi_connect_details.service):
                
                characteristic.value = bytes(constants.WIFI_CONNECTED, "utf-8")
                server.update_value(constants.SERVICE_UUID, constants.WIFI_CONNECT_UUID)
                return

    # if we get here somethign went wrong
    characteristic.value = bytes(constants.WIFI_ERROR, "utf-8")
    server.update_value(constants.SERVICE_UUID, constants.WIFI_CONNECT_UUID)


# Initial scan
threading.Thread(target=scan_wifi).start()