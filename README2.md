# Srcful Energy Gateway

The Srcful Energy Gateway application is a bundle of services that are deployed as docker containers that are intended to run on a Raspberry Pi.

```
+------------+                       +------------+
|            |                       |            |
|  Srcful    |                       |            |
|  Energy    |<--- modbus tcp/ip --->|  Inverter  |
|  Gateway   |                       |            |
|            |                       |            |
+------------+                       +------------+
```

1. **Select a Lightweight Linux Distro**: Use Raspberry Pi OS (64-bit).

2. **Download and Use Raspberry Pi Imager**:

   - Get it from the official website.
   - Burn Raspberry Pi OS Lite (64-bit) to an SD card.

3. **Image Configuration**: Enable SSH and WiFi using the Raspberry Pi Imager.

4. **Insert SD Card and Power On**: Insert the SD card into the Raspberry Pi and power it on.

5. **Connect to Raspberry Pi**: Use SSH (ssh pi@<RASPBERRY_PI_IP>).

## Setting Up the Raspberry Pi

1. **Configure and Update**:

   - Run `sudo raspi-config` to set locale and timezone.
   - Update with `sudo apt-get update && sudo apt-get upgrade -y`.
   - Restart with `sudo reboot` and log in again using SSH.

2. **Enable i2c and SPI**:
   - Use `sudo raspi-config` to enable `I2C` and `SPI` interfaces.
   - For Rak Hotspot Miner V2, edit `/boot/firmware/config.txt` to add `dtoverlay=spi0-1cs`.
   - Save, exit, and restart with `sudo reboot`, then log in again using SSH.
