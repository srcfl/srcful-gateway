import queue
import sys
import time
import logging

from server.tasks.checkForWebRequestTask import CheckForWebRequest
import server.web.server
from server.tasks.itask import ITask
from server.tasks.openInverterTask import OpenInverterTask
from server.tasks.scanWiFiTask import ScanWiFiTask
from server.inverters.ModbusTCP import ModbusTCP
from server.tasks.harvestFactory import HarvestFactory
from server.bootstrap import Bootstrap

from server.blackboard import BlackBoard

logger = logging.getLogger(__name__)


def main_loop(tasks: queue.PriorityQueue, bb: BlackBoard):
    # here we could keep track of statistics for different types of tasks
    # and adjust the delay to keep the within a certain range

    def add_task(task: ITask):
        if task.get_time() < bb.time_ms():
            dt = bb.time_ms() - task.get_time()
            s = f"task {type(task)} is in the past {dt} adjusting time"
            logger.info(s)
            task.adjust_time(bb.time_ms() + 100)
        tasks.put(task)

    bb.add_info("eGW started - all is good")

    while True:
        task = tasks.get()
        delay = (task.get_time() - bb.time_ms()) / 1000
        if delay > 0.01:
            time.sleep(delay)

        try:
            new_tasks = task.execute(bb.time_ms())            
        except StopIteration:
            logger.info("StopIteration received, exiting main loop")
            break
        except Exception as e:
            logger.error("Failed to execute task: %s", e)
            new_tasks = None

        # take care of any new tasks
        if new_tasks is None:
            new_tasks = []
        elif not isinstance(new_tasks, list):
            new_tasks = [new_tasks]
        new_tasks = new_tasks + bb.purge_tasks()
        
        for e in new_tasks:
            add_task(e)


def main(server_host: tuple[str, int], web_host: tuple[str, int], inverter: ModbusTCP.Setup | None = None, bootstrap_file: str | None = None):
    bb = BlackBoard()
    harvest_factory = HarvestFactory(bb)  # this is what creates the harvest tasks when inverters are added
    harvest_factory.dummy()

    logger.info("eGW version: %s", bb.get_version())

    bb.rest_server_port = server_host[1]
    bb.rest_server_ip = server_host[0]
    web_server = server.web.server.Server(web_host, bb)
    logger.info("Server started http://%s:%s", web_host[0], web_host[1])

    tasks = queue.PriorityQueue()

    bootstrap = Bootstrap(bootstrap_file)

    bb.inverters.add_listener(bootstrap)

    # put some initial tasks in the queue
    if inverter is not None:
        tasks.put(OpenInverterTask(bb.time_ms(), bb, ModbusTCP(inverter)))

    for task in bootstrap.get_tasks(bb.time_ms() + 500, bb):
        tasks.put(task)

    tasks.put(CheckForWebRequest(bb.time_ms() + 1000, bb, web_server))
    tasks.put(ScanWiFiTask(bb.time_ms() + 45000, bb))

    try:
        main_loop(tasks, bb)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logger.exception("Unexpected error: %s", sys.exc_info()[0])
        logger.exception("Exception: %s", e)
    finally:
        for i in bb.inverters.lst:
            i.close()
        web_server.close()
        logger.info("Server stopped.")


# this is for debugging purposes only
if __name__ == "__main__":
    import logging

    logging.basicConfig()
    # handler = logging.StreamHandler(sys.stdout)
    # logging.root.addHandler(handler)
    logging.root.setLevel(logging.INFO)
    # main(('localhost', 5000), ("localhost", 502, "huawei", 1), 'bootstrap.txt')
    main(("localhost", 5000), ("localhost", 5000), None, "bootstrap.txt")
