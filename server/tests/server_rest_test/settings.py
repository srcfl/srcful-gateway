API_URL = "http://localhost:8080/api/"
#API_URL = "http://192.168.0.215/api/"

IP_DO_TEST_AGAINST_API_URL = False  # checks if the ip adress is part of the API_URL
DO_TEST_CRYPTO = True  # if set to False all crypto dependent tests should return a 500


INVERTER_HOST = "35.198.102.58"
INVERTER_PORT = 502
INVERTER_TYPE = "SOLAREDGE"
INVERTER_CONNECTION = "TCP"
INVERTER_ADDRESS = 1

REQUEST_TIMEOUT = 10

# default inverter simulator settings
# inverter_port = 502
# inverter_type = "solaredge"
# inverter_connection = "TCP"
# inverter_address = 1

# wifi settings
# testing wifi can be potentially messy
# if you try to connect to a non existent network the old network is lost
# ethernet is recommended as backup or the gateway could lose internet
WIFI_DO_TEST = False
WIFI_REAL_SETTINGS = False  # check if we have a valid ssid and psk that should connect to a network

WIFI_SSID = "test"  # do not check in real settings
WIFI_PSK = "test"  # do not check in real settings
