import sys
import logging
from server.app.backend_settings_saver import BackendSettingsSaver
from server.app.task_scheduler import TaskScheduler
from server.crypto.crypto_state import CryptoState
from server.network.network_utils import NetworkUtils
from server.tasks.checkForWebRequestTask import CheckForWebRequest
from server.tasks.saveStateTask import SaveStatePerpetualTask
import server.web.server
from server.tasks.openDeviceTask import OpenDeviceTask
from server.tasks.scanWiFiTask import ScanWiFiTask
from server.devices.inverters.ModbusTCP import ModbusTCP
from server.tasks.harvestFactory import HarvestFactory
from server.tasks.getSettingsTask import GetSettingsTask
from server.web.socket.settings_subscription import GraphQLSubscriptionClient
from server.web.socket.control.control_subscription import ControlSubscription
from server.app.settings_device_listener import SettingsDeviceListener
from server.app.blackboard import BlackBoard
from server.tasks.discoverHostsTask import DiscoverHostsTask

logger = logging.getLogger(__name__)


# Constants
MAX_WORKERS = 4
CONTROL_SUBSCRIPTION_URL = "ws://192.168.50.112:5000/bms-subscribe"
# CONTROL_SUBSCRIPTION_URL = "wss://devnet.srcful.dev/ems/subscribe"
INITIAL_SETTINGS_DELAY = 500  # milliseconds
SAVE_STATE_DELAY = 10000  # milliseconds (10 seconds)
CHECK_WEB_REQUEST_DELAY = 1000  # milliseconds
SCAN_WIFI_DELAY = 10000  # milliseconds


def main(server_host: tuple[str, int], web_host: tuple[str, int], inverter: ModbusTCP | None = None):

    try:
        crypto_state = CryptoState()
    except Exception as e:
        logger.error(f"Failed to get crypto state: {e}")
        return
    bb = BlackBoard(crypto_state)
    scheduler = TaskScheduler(max_workers=MAX_WORKERS, system_time=bb, task_source=bb)

    HarvestFactory(bb)  # this is what creates the harvest tasks when inverters are added

    logger.info("eGW version: %s", bb.get_version())

    bb.rest_server_port = server_host[1]
    bb.rest_server_ip = server_host[0]
    web_server = server.web.server.Server(web_host, bb)
    logger.info("Server started http://%s:%s", web_host[0], web_host[1])

    props = {
        "version": bb.get_version(),
        **bb.crypto_state().to_dict(bb.chip_death_count)
    }

    NetworkUtils.start_mdns_after_dns_resolution(port=web_host[1], properties=props)

    graphql_client = GraphQLSubscriptionClient(bb, bb.settings.api.ws_endpoint)
    graphql_client.start()

    control_client = ControlSubscription(bb, CONTROL_SUBSCRIPTION_URL)
    control_client.start()

    bb.settings.add_listener(BackendSettingsSaver(bb).on_change)
    bb.settings.devices.add_listener(SettingsDeviceListener(bb).on_change)

    scheduler.add_task(SaveStatePerpetualTask(bb.time_ms() + 1000 * 10, bb))

    # put some initial tasks in the queue
    scheduler.add_task(GetSettingsTask(bb.time_ms() + 500, bb))

    if inverter is not None:
        scheduler.add_task(OpenDeviceTask(bb.time_ms(), bb, inverter))

    scheduler.add_task(CheckForWebRequest(bb.time_ms() + 1000, bb, web_server))
    scheduler.add_task(ScanWiFiTask(bb.time_ms() + 10000, bb))

    scheduler.add_task(DiscoverHostsTask(bb.time_ms() + 1000, bb))

    try:
        scheduler.main_loop()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logger.exception("Unexpected error: %s", sys.exc_info()[0])
        logger.exception("Exception: %s", e)
    finally:
        for i in bb.devices.lst:
            i.disconnect()

        bb.devices.lst.clear()
        web_server.close()
        graphql_client.stop()
        graphql_client.join()

        # Stop mDNS advertisement
        NetworkUtils.stop_mdns_advertisement()

        logger.info("Server stopped.")


# this is for debugging purposes only
if __name__ == "__main__":
    import logging

    logging.basicConfig()

    logging.root.setLevel(logging.INFO)
    args = {
        NetworkUtils.IP_KEY: "192.168.50.11",
        NetworkUtils.MAC_KEY: NetworkUtils.INVALID_MAC,
        ModbusTCP.sn_key(): "2311286262",
        NetworkUtils.PORT_KEY: 502,
        ModbusTCP.slave_id_key(): 1,
        ModbusTCP.device_type_key(): "huawei"
    }
    modbus_tcp = ModbusTCP(**args)
    main(("localhost", 5000), ("localhost", 5000), modbus_tcp)
