#!/bin/bash

echo 'Starting bluetooth container...'

echo 7 > /sys/kernel/debug/bluetooth/hci0/adv_channel_map
# Send a beacon every 153 x 0.625ms = 95.625ms (244 is 152.5ms)
echo 153 > /sys/kernel/debug/bluetooth/hci0/adv_min_interval
echo 244 > /sys/kernel/debug/bluetooth/hci0/adv_max_interval

# this could set the values for the bluetooth device values from ios documentation
# presumably in in units of 1.25ms  (12 is 15ms) (24 is 30ms)
# according to apple docs the min interval should be in 15ms increments ie 12, 24 etc
echo 6 > /sys/kernel/debug/bluetooth/hci0/conn_min_interval
echo 400 > /sys/kernel/debug/bluetooth/hci0/conn_max_interval

echo 2000 > /sys/kernel/debug/bluetooth/hci0/supervision_timeout


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


python ble_service_twochars.py -api_url 127.0.0.1:${REST_SERVICE_PORT}

/bin/bash