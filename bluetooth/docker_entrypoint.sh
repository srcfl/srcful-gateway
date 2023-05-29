#!/bin/bash

service dbus start
bluetoothd &


python ble_service.py -api_url 127.0.0.1

/bin/bash