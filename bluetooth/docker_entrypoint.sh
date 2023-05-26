#!/bin/bash

service dbus start
bluetoothd &


python ble_service.py

/bin/bash