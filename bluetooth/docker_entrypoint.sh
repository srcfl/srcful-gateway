#!/bin/bash



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
echo 6 > /sys/kernel/debug/bluetooth/hci0/conn_min_interval
echo 400 > /sys/kernel/debug/bluetooth/hci0/conn_max_interval

cat /sys/kernel/debug/bluetooth/hci0/conn_min_interval
cat /sys/kernel/debug/bluetooth/hci0/conn_max_interval

cat /sys/kernel/debug/bluetooth/hci0/supervision_timeout

echo 2000 > /sys/kernel/debug/bluetooth/hci0/supervision_timeout

# these files does not seem to exist neither 0 or 1
#cat /sys/kernel/debug/bluetooth/hci0/conn_min_interval
#cat /sys/kernel/debug/bluetooth/hci0/conn_max_interval
#cat /etc/bluetooth/main.conf

#service dbus start

#bluetoothd -d

#sleep 10

#bluetoothctl <<EOF
#agent off
##power on
#discoverable on
#pairable on
#agent NoInputNoOutput
#default-agent 
#EOF

python ble_agent.py &

# this one runs and then exits an it is likely good to take care of this before the service is up and running.
python ble_flush.py

python ble_service.py -api_url 127.0.0.1
#python nebra/ble_service.py
#python test_server.py

/bin/bash