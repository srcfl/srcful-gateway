from .inverters.modbus import Modbus
from .inverters.ModbusTCP import ModbusTCP
from .inverters.ModbusRTU import ModbusRTU
from .inverters.ModbusSolarman import ModbusSolarman
from .tasks.openInverterPerpetualTask import OpenInverterPerpetualTask
import os
import logging
from .inverters.IComFactory import IComFactory

logger = logging.getLogger(__name__)


class BootstrapSaver:
    """Abstract class for saving bootstrap tasks to a file"""

    def append_inverter(self, setup):
        """Appends an inverter to the bootstrap file"""
        raise NotImplementedError("Subclass must implement abstract method")


class Bootstrap(BootstrapSaver):
    """A bootstrap is a list of tasks that are executed on startup."""

    def __init__(self, filename: str):
        self.filename = filename
        self.tasks = []
        self._create_file_if_not_exists()
        self._icom_factory = IComFactory()

    # implementation of blackboard inverter observer
    def add_inverter(self, inverter: Modbus):
        self.append_inverter(inverter._get_config())

    def remove_inverter(self, inverter: Modbus):
        logger.info(
            "Removing inverter from bootstrap: {} not yet supported".format(
                inverter._get_config()
            )
        )

    def _create_file_if_not_exists(self):
        # create the directories and the file if it does not exist
        # log any errors
        if not os.path.exists(self.filename):
            try:
                os.makedirs(os.path.dirname(self.filename), exist_ok=True)
                with open(self.filename) as f:
                    f.write(
                        "# This file contains the tasks that are executed on startup\n"
                    )
                    f.write("# Each line contains a task name and its arguments\n")

            except Exception as e:
                logger.error("Failed to create file: {}".format(self.filename))
                logger.error(e)

    def append_inverter(self, inverter_args):
        self._create_file_if_not_exists()

        # check if the setup already exists
        for task in self.get_tasks(0, None):
            if (
                isinstance(task, OpenInverterPerpetualTask)
                and task.inverter._get_config() == inverter_args
            ):
                return

        # append the setup to the file
        with open(self.filename, "w") as f:
            logger.info("Writing (w) inverter to bootstrap file: %s", inverter_args)
            inverter_str = " ".join(str(i) for i in inverter_args)
            f.write(f"OpenInverter {inverter_str}\n")

    def get_tasks(self, event_time, stats):
        self.tasks = []
        # read the file handle errors
        try:
            with open(self.filename, "r") as f:
                logger.info("Reading bootstrap file: %s", self.filename)
                lines = f.readlines()
        except Exception as e:
            logger.error("Failed to read file: {}".format(self.filename))
            return self.tasks

        return self._process_lines(lines, event_time, stats)

    def _process_lines(self, lines: list, event_time, stats):
        # for each line, create a task and execute it
        for line in lines:
            line = line.strip()
            line = line.replace("\n", "")
            tokens = line.split(" ")

            # ignore empty lines, comments and lines without tokens
            if len(line) == 0 or line[0] == "#" or len(tokens) == 0:
                continue

            # get the task name
            task_name = tokens[0]

            # get the task arguments
            task_args = tokens[1:]

            # create the task
            task = self._create_task(task_name, task_args, event_time, stats)
            if task is None:
                continue
            self.tasks.append(task)

        return self.tasks

    def _create_task(self, task_name: str, task_args: list, event_time, bb):
        # currently we only support OpenInverter
        if task_name == "OpenInverter":
            return self._create_open_inverter_task(task_args, event_time, bb)
        else:
            logger.error("Unknown task: {} in file {}".format(task_name, self.filename))
            return None

    def _create_open_inverter_task(self, task_args: list, event_time, bb):
        
        obj = self._icom_factory.create_com(task_args)
        
        try:
            return OpenInverterPerpetualTask(
                event_time + 1000,
                bb,
                obj,
            )
        except Exception as e:
            logger.error("Failed to create OpenInverter task: {}".format(task_args))
            logger.error(e)
            return None