#!/bin/bash

service dbus start
bluetoothd &


python ble_test.py

/bin/bash