#!/bin/bash

service dbus start
bluetoothd &


python main.py

/bin/bash