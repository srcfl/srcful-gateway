#!/bin/bash


echo 'Starting bluetooth container...'
cat /sys/kernel/debug/bluetooth/hci0/conn_min_interval
cat /sys/kernel/debug/bluetooth/hci0/conn_max_interval

# this could set the values for the bluetooth device values from ios documentation
# Advertise on channels 37, 38 and 39
echo 7 > /sys/kernel/debug/bluetooth/hci0/adv_channel_map
# Send a beacon every 153 x 0.625ms = 95.625ms (244 is 152.5ms)
echo 153 > /sys/kernel/debug/bluetooth/hci0/adv_min_interval
echo 244 > /sys/kernel/debug/bluetooth/hci0/adv_max_interval

# this could set the values for the bluetooth device values from ios documentation
# presumably in in units of 1.25ms  (12 is 15ms) (24 is 30ms)
# according to apple docs the min interval should be in 15ms increments ie 12, 24 etc
#echo 6 > /sys/kernel/debug/bluetooth/hci0/conn_min_interval
#echo 400 > /sys/kernel/debug/bluetooth/hci0/conn_max_interval

cat /sys/kernel/debug/bluetooth/hci0/conn_min_interval
cat /sys/kernel/debug/bluetooth/hci0/conn_max_interval

cat /sys/kernel/debug/bluetooth/hci0/supervision_timeout

# wait for startup of services
#msg="Waiting for services to start..."
#time=0
#echo -n $msg
#while [ "$(pidof start-stop-daemon)" ]; do
#    sleep 1
#    time=$((time + 1))
#    echo -en "\r$msg $time s"
#done
#echo -e "\r$msg done! (in $time s)"

# we simply wait and see if this does the trick...
#echo "Waiting for services to start..."
#sleep 60

# this resets the bluetooth device seems to be needed if the device is restarted by power cycling
hciconfig hci0 down
hciconfig hci0 up

# we need to wait for dbus to be up and running before we can start the bluetooth service
#while true; do
#    dbus-send --session \
#            --print-reply \
#            --dest=org.freedesktop.DBus \
#            /org/freedesktop/DBus \
#            org.freedesktop.DBus.ListNames

#            dbus_wait=$?
#    if [ "$dbus_wait" -eq 0 ]; then
#        break;
#    else
#        sleep 0.1
#    fi
#done

#echo "DBus is now accepting connections"

#echo 2000 > /sys/kernel/debug/bluetooth/hci0/supervision_timeout

# these files does not seem to exist neither 0 or 1
#cat /sys/kernel/debug/bluetooth/hci0/conn_min_interval
#cat /sys/kernel/debug/bluetooth/hci0/conn_max_interval
#cat /etc/bluetooth/main.conf

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



#sleep 60

#bluetoothctl <<EOF
#agent off
##power on
#discoverable on
#pairable on
#agent NoInputNoOutput
#default-agent 
#EOF




python ble_agent.py &

# Disable pairing
#printf "pairable off\nquit" | /usr/bin/bluetoothctl

# this one runs and then exits an it is likely good to take care of this before the service is up and running.
# flushing does not work as expected reconnecting to the pc is flaky at best.
#python ble_flush.py

python ble_service.py -api_url 127.0.0.1
#python nebra/ble_service.py
#python test_server.py

/bin/bash