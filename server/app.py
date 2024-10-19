import queue
import sys
import logging
import threading
from concurrent.futures import ThreadPoolExecutor
from server.devices.IComFactory import IComFactory
from server.tasks.checkForWebRequestTask import CheckForWebRequest
from server.tasks.saveStateTask import SaveStatePerpetualTask
import server.web.server
from server.tasks.itask import ITask
from server.tasks.openDevicePerpetualTask import DevicePerpetualTask
from server.tasks.openDeviceTask import OpenDeviceTask
from server.tasks.scanWiFiTask import ScanWiFiTask
from server.devices.ModbusTCP import ModbusTCP
from server.tasks.harvestFactory import HarvestFactory
from server.settings import DebouncedMonitorBase, ChangeSource
from server.tasks.getSettingsTask import GetSettingsTask
from server.tasks.saveSettingsTask import SaveSettingsTask
from server.tasks.discoverModbusDevicesTask import DiscoverModbusDevicesTask
from server.web.socket.settings_subscription import GraphQLSubscriptionClient
from server.network.network_utils import NetworkUtils


from server.blackboard import BlackBoard

logger = logging.getLogger(__name__)


class TaskScheduler:

    def __init__(self, max_workers, initial_tasks, bb):
        self.bb = bb
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.tasks = queue.PriorityQueue()
        self.active_threads = 0
        self.new_tasks_condition = threading.Condition()
        self.stop_event = threading.Event()

        while initial_tasks.qsize() > 0:
            self.tasks.put(initial_tasks.get())

    
    def add_task(self, task: ITask):
        with self.new_tasks_condition:

            if task.get_time() <= self.bb.time_ms():
                logger.warning("Task (%s) is in the past by %d ms, adjusting time to now", task, self.bb.time_ms() - task.get_time())
                task.adjust_time(self.bb.time_ms() + 100)

            self.tasks.put(task)
            self.new_tasks_condition.notify()

    def stop(self):
        self.stop_event.set()

    def worker(self, task: ITask):
        try:
            new_tasks = task.execute(self.bb.time_ms())
            if new_tasks is None:
                new_tasks = []
        except StopIteration:
            logger.info("StopIteration received, stopping TaskScheduler")
            self.stop()
            new_tasks = None
        except Exception as e:
            logging.error(f"Failed to execute task {task}: {e}")
            new_tasks = None
            
        if new_tasks is not None:
            if not isinstance(new_tasks, list):
                new_tasks = [new_tasks]
            new_tasks = new_tasks + self.bb.purge_tasks()
            for new_task in new_tasks:
                self.add_task(new_task)
        
        with self.new_tasks_condition:
            self.active_threads -= 1
            self.new_tasks_condition.notify()

    def main_loop(self):
        while not self.stop_event.is_set():
            with self.new_tasks_condition:
                while (self.active_threads >= self.executor._max_workers) or self.tasks.empty() or self.tasks.queue[0].get_time() > self.bb.time_ms():
                    if self.stop_event.is_set():
                        break

                    if not self.tasks.empty():
                        # wake the loop up gain when the next task is due (note that it may wake up before that if a new task is added)
                        delay = max(0, (self.tasks.queue[0].get_time() - self.bb.time_ms()) / 1000)
                        self.new_tasks_condition.wait(delay)
                    else:
                        self.new_tasks_condition.wait()

                if self.stop_event.is_set():
                    break
                
                if not self.tasks.empty() and self.tasks.queue[0].get_time() <= self.bb.time_ms():
                    task = self.tasks.get()
                    self.executor.submit(self.worker, task)
                    self.active_threads += 1


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

    tasks = queue.PriorityQueue()

    class BackendSettingsSaver(DebouncedMonitorBase):
            """ Monitors settings changes and schedules a save to the backend, ignores changes from the backend """
            def __init__(self, blackboard: BlackBoard, debounce_delay: float = 0.5):
                super().__init__(debounce_delay)
                self.blackboard = blackboard

            def _perform_action(self, source: ChangeSource):
                if source != ChangeSource.BACKEND:
                    logger.info("Settings change detected, scheduling a save to backend")
                    self.blackboard.add_task(SaveSettingsTask(self.blackboard.time_ms() + 500, self.blackboard))
                else:
                    logger.info("No need to save settings to backend as the source is the backend")

    class SettingsDeviceListener(DebouncedMonitorBase):
        def __init__(self, blackboard: BlackBoard, debounce_delay: float = 0.5):
            super().__init__(debounce_delay)
            self.blackboard = blackboard

        def _perform_action(self, source: ChangeSource):
    
            for connection in self.blackboard.settings.devices.connections:
                
                # Backward compatibility stuff 
                # TODO: Remove this once released
                
                if NetworkUtils.IP_KEY not in connection or NetworkUtils.MAC_KEY not in connection or "sn" not in connection:
                    
                    old_ip_key = "host"
                    old_slave_id_key = "address"
                    
                    new_config_format = connection
                    
                    new_config_format[NetworkUtils.IP_KEY] = new_config_format.pop(old_ip_key)
                    new_config_format['slave_id'] = new_config_format.pop(old_slave_id_key)
                
                if NetworkUtils.MAC_KEY not in connection or "sn" not in connection:
                    logger.info("Device with settings %s was not found in the blackboard, opening a perpetual task to connect it", new_config_format)
                    self.blackboard.add_task(DevicePerpetualTask(self.blackboard.time_ms(), self.blackboard, IComFactory.create_com(new_config_format)))
                    self.blackboard.settings.devices.remove_connection_by_config(connection, ChangeSource.LOCAL)

                    continue
                
                sn = connection["sn"]
                
                for device in self.blackboard.devices.lst:
                    # Check if the device already exists in the blackboard
                    # Then check if the device is open, if not, then start a perpetual task to open it
                    # TODO: This might start another DevicePerpetualTask in addition to one that might
                    # already be running from the blackboard. Consider reworking this logic
                    if device.get_SN() == sn:
                        if not device.is_open():
                            logger.info("Device %s from settings was found in the blackboard, but not open", sn)
                            logger.info("Removing %s from the blackboard and opening a perpetual task to connect it", sn)
                            self.blackboard.devices.remove(device)
                            self.blackboard.add_task(DevicePerpetualTask(self.blackboard.time_ms(), self.blackboard, IComFactory.create_com(connection)))
                        break
                else:
                    # Device not found in the blackboard, but apperantly exists in the settings,
                    # which means it was previously connected So we try to open it again
                    logger.info("Device %s from settings was not found in the blackboard, opening a perpetual task to connect it", sn)
                    self.blackboard.add_task(DevicePerpetualTask(self.blackboard.time_ms(), self.blackboard, IComFactory.create_com(connection)))


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
    modbus_tcp = ModbusTCP("192.168.1.100", "00:00:00:00:00:00", 502, "huawei", 1)
    main(("localhost", 5000), ("localhost", 5000), modbus_tcp)
