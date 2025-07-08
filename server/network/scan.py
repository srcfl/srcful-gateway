import logging
import nmcli
from server.network.network_utils import NetworkUtils

logger = logging.getLogger(__name__)

try:
    import dbus
except ImportError:
    logger.info("dbus not found - possibly on non linux platform")
    logger.info("wifi provisioning will not work")

    def get_connection_configs():
        config = {"connection": {"type": "802-11-wireless"}}
        return [config]

    class WifiScanner:
        def __init__(self):
            self.ssids = ["test1", "test2"]

        def scan(self):
            pass

        def get_ssids(self):
            return self.ssids

        def get_connected_ssid(self):
            return "Unknown"

else:

    class WifiScanner:
        def __init__(self):
            # property will not be set until 3 to 5 seconds after the scan is started
            self.ssids = []

        def get_connected_ssid(self):
            return NetworkUtils.get_wifi_ssids()

        def get_ssids(self) -> list[str]:
            return self.ssids

        def scan(self) -> list[str]:
            self.ssids = [ap.ssid for ap in nmcli.device.wifi(rescan=True)]
            return self.ssids
