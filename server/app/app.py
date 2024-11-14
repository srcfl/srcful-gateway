import queue
import sys
import logging
from server.app.backend_settings_saver import BackendSettingsSaver
from server.app.task_scheduler import TaskScheduler
from server.network.network_utils import NetworkUtils
from server.tasks.checkForWebRequestTask import CheckForWebRequest
from server.tasks.saveStateTask import SaveStatePerpetualTask
import server.web.server
from server.tasks.openDeviceTask import OpenDeviceTask
from server.tasks.scanWiFiTask import ScanWiFiTask
from server.devices.inverters.ModbusTCP import ModbusTCP
from server.tasks.harvestFactory import HarvestFactory
from server.tasks.getSettingsTask import GetSettingsTask
from server.tasks.discoverModbusDevicesTask import DiscoverModbusDevicesTask
from server.web.socket.settings_subscription import GraphQLSubscriptionClient
from server.app.settings_device_listener import SettingsDeviceListener

from server.app.blackboard import BlackBoard

logger = logging.getLogger(__name__)


def main_loop(tasks: queue.PriorityQueue, bb: BlackBoard):
    scheduler = TaskScheduler(4, tasks, bb)
    scheduler.main_loop()


def main(server_host: tuple[str, int], web_host: tuple[str, int], inverter: ModbusTCP | None = None): 

    from server.web.handler.get.crypto import Handler as CryptoHandler
    try:
        crypto_state = CryptoHandler().get_crypto_state(0)
    except Exception as e:
        logger.error(f"Failed to get crypto state: {e}")
        crypto_state = {'error': 'no crypto key or chip'}
    bb = BlackBoard(crypto_state)

    HarvestFactory(bb)  # this is what creates the harvest tasks when inverters are added

    logger.info("eGW version: %s", bb.get_version())

    bb.rest_server_port = server_host[1]
    bb.rest_server_ip = server_host[0]
    web_server = server.web.server.Server(web_host, bb)
    logger.info("Server started http://%s:%s", web_host[0], web_host[1])

    graphql_client = GraphQLSubscriptionClient(bb, "wss://api.srcful.dev/")
    graphql_client.start()

    tasks: queue.PriorityQueue = queue.PriorityQueue()

    bb.settings.add_listener(BackendSettingsSaver(bb).on_change)
    bb.settings.devices.add_listener(SettingsDeviceListener(bb).on_change)

    tasks.put(SaveStatePerpetualTask(bb.time_ms() + 1000 * 10, bb))

    # put some initial tasks in the queue
    tasks.put(GetSettingsTask(bb.time_ms() + 500, bb))

    if inverter is not None:
        tasks.put(OpenDeviceTask(bb.time_ms(), bb, inverter))

    tasks.put(CheckForWebRequest(bb.time_ms() + 1000, bb, web_server))
    tasks.put(ScanWiFiTask(bb.time_ms() + 45000, bb))
    tasks.put(DiscoverModbusDevicesTask(bb.time_ms() + 5000, bb))
    # tasks.put(CryptoReviveTask(bb.time_ms() + 7000, bb))

    try:
        main_loop(tasks, bb)
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
        logger.info("Server stopped.")


# this is for debugging purposes only
if __name__ == "__main__":
    import logging

    logging.basicConfig()
    # handler = logging.StreamHandler(sys.stdout)
    # logging.root.addHandler(handler)
    logging.root.setLevel(logging.INFO)
    args = {
        NetworkUtils.IP_KEY: "192.168.1.100",
        NetworkUtils.MAC_KEY: NetworkUtils.INVALID_MAC,
        NetworkUtils.PORT_KEY: 502,
        ModbusTCP.slave_id_key(): 1,  
        ModbusTCP.device_type_key(): "huawei"
    }
    modbus_tcp = ModbusTCP(**args)
    main(("localhost", 5000), ("localhost", 5000), modbus_tcp)
