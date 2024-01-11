#!/bin/bash

echo 'Starting bluetooth container...'


# we disable bluetooth in the host os and restart in local container.
# this is to avoid adding the default bluez plugin services
# these services cause e.g. windows to connect in a paring mode which is more troublesome

DBUS_SYSTEM_BUS_ADDRESS=unix:path=/host/run/dbus/system_bus_socket \
  dbus-send \
  --system \
  --print-reply \
  --dest=org.freedesktop.systemd1 \
  /org/freedesktop/systemd1 \
  org.freedesktop.systemd1.Manager.StopUnit \
  string:bluetooth.service string:replace

service dbus start
bluetoothd --experimental --noplugin=* &

hciconfig hci0 up


python ble_agent.py &

# Disable pairing
#printf "pairable off\nquit" | /usr/bin/bluetoothctl


python ble_service_twochars.py -api_url 127.0.0.1

/bin/bash