# Sourceful Energy Gateway

The Sourceful Energy Gateway application is a bundle of services that are deployed as docker containers on a Raspberry Pi.

```
+------------+                       +------------+
|            |                       |            |
|  Sourceful |                       |            |
|  Energy    |<--- modbus tcp/ip --->|  Inverter  |
|  Gateway   |                       |            |
|            |                       |            |
+------------+                       +------------+
```

## Setting Up the Raspberry Pi

Raspberry Pi OS Lite (64-bit) is the recommended operating system.

1. **Configure and Update**:

   - Run `sudo raspi-config` to set locale and timezone.
   - Update with `sudo apt-get update && sudo apt-get upgrade -y`.
   - Restart with `sudo reboot` and log in again using SSH.

2. **Enable i2c and SPI**:
   - Use `sudo raspi-config` to enable `I2C` and `SPI` interfaces.
   - For Rak Hotspot Miner V2, edit `/boot/firmware/config.txt` to add `dtoverlay=spi0-1cs`.
   - Save, exit, and restart with `sudo reboot`, then log in again using SSH.

## Building and Running the Project

To build and run this project, simply run the following command:

```shell
docker-compose -f compose-rpi4.yml up
```

Or in detached mode:

```shell
docker-compose -f compose-rpi4.yml up -d
```

## Testing

To run the tests, execute the following command:

For the `server` service:

```shell
pytest server/tests/server_unit_test
pytest server/tests/server_rest_test
```

For the `bluetooth` service:

```shell
pytest bluetooth/tests/ble_unit_test
pytest bluetooth/tests/ble_rest_test
```
