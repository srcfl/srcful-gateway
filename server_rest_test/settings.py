#api_url = "http://localhost:5000/api/"
api_url = "http://192.168.0.215/api/"

inverter_host = "20.218.129.227"
inverter_port = 502
inverter_type = "solaredge"
inverter_connection = "TCP"
inverter_address = 1

# default inverter simulator settings
# inverter_port = 502
# inverter_type = "solaredge"
# inverter_connection = "TCP"
# inverter_address = 1

# wifi settings
# testing wifi can be potentially messy
# if you try to connect to a non existent network the old network is lost
# ethernet is recommended as backup or the gateway could lose internet
wifi_do_test = True 
wifi_real_settings = False  # check if we have a valid ssid and psk that should connect to a network
wifi_ssid = "test"          # do not check in real settings
wifi_psk = "test"           # do not check in real settings
