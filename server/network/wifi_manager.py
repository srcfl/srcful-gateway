import nmcli
import subprocess
import socket
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class WiFiManager:
    @staticmethod
    def scan_networks() -> list[str]:
        try:
            nmcli.disable_use_sudo()
            aps = nmcli.device.wifi(rescan=True)
            return [ap.ssid for ap in aps]
        except Exception as e:
            print(f"Error scanning WiFi networks: {e}")
            return []

    @staticmethod
    def connect(ssid: str, psk: str, timeout: int) -> bool:
        try:
            nmcli.device.wifi_connect(ssid=ssid, password=psk, wait=timeout)
            print(f"Successfully connected to {ssid}")
            return True
        except Exception as e:
            print(f"Error connecting to {ssid}: {e}")
            return False

    @staticmethod
    def disconnect():
        try:
            # Find active WiFi device to disconnect
            devices = nmcli.device()
            wifi_device = None
            for device in devices:
                if device.device_type == 'wifi' and device.state == 'connected':
                    wifi_device = device.device
                    break

            if wifi_device:
                nmcli.device.disconnect(wifi_device)
                print(f"Successfully disconnected from WiFi")
                return True
            else:
                print("No active WiFi connection found")
                return False
        except Exception as e:
            print(f"Error disconnecting from WiFi: {e}")
            return False

    @staticmethod
    def get_ip():
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                return s.getsockname()[0]
        except:
            return "no network"

    @staticmethod
    def get_mac_address(iface):
        try:
            with open(f"/sys/class/net/{iface}/address") as f:
                return f.read().strip().upper()
        except:
            return None

    @staticmethod
    def get_network_interfaces():
        try:
            result = subprocess.run(
                ['ip', '-4', 'addr', 'show'], capture_output=True, text=True)
            interfaces = {}
            for line in result.stdout.split('\n'):
                if ': ' in line and not line.startswith(' '):
                    iface = line.split(':')[1].strip()
                elif 'inet ' in line and not '127.' in line:
                    ip = line.split('inet ')[1].split('/')[0].strip()
                    interfaces[iface] = ip

            # Filter to only return eth0 and wlan0 interfaces
            filtered_interfaces = {}
            for iface in ['eth0', 'wlan0']:
                if iface in interfaces:
                    filtered_interfaces[iface] = interfaces[iface]

            return filtered_interfaces
        except:
            return {}

    @staticmethod
    def has_internet_access():
        try:
            # Test internet connectivity by connecting to Google DNS
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(3)
                s.connect(("8.8.8.8", 53))
                return True
        except:
            return False

    @staticmethod
    def get_network_devices():
        try:
            devices = nmcli.device()
            connected = {
                'wifi': next((d for d in devices if d.device_type == 'wifi' and d.state == 'connected'), None),
                'ethernet': next((d for d in devices if d.device_type == 'ethernet' and d.state == 'connected'), None)
            }
            return connected
        except:
            return {'wifi': None, 'ethernet': None}

    @staticmethod
    def is_wifi_connected():
        try:
            devices = nmcli.device()
            for device in devices:
                if device.device_type == 'wifi' and device.state == 'connected':
                    return True
            return False
        except Exception as e:
            return False

    @staticmethod
    def get_wifi_ssid():
        try:
            devices = nmcli.device()
            logger.info(f"Devices: {devices}")

            for device in devices:
                logger.info(f"Device: {device}")
                if device.device_type == 'wifi' and device.state == 'connected':
                    return device.connection
            return None
        except Exception as e:
            return None
