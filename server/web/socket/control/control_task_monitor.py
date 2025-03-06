import logging
from typing import Any
from server.tasks.task import Task
from server.tasks.control_device_task import ControlDeviceTask
from server.tasks.task_observer import TaskListener, TaskObserver

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class ControlTaskMonitor(TaskListener):
    """
    Simple task listener that monitors execution of control-related tasks
    and logs their execution to the console.
    """

    def __init__(self):
        """
        Initialize the control task monitor and register with the global task observer
        """
        # Register with the observer
        TaskObserver.get_instance().register_listener(self)
        logger.info("Control task monitor registered")

    def on_task_started(self, task: Task):
        """
        Called when any task starts execution.
        Filters for ControlDeviceTask instances.
        """
        if not isinstance(task, ControlDeviceTask):
            return

        # Get task details
        task_id = task.control_message.id
        sn = task.control_message.sn
        command_count = len(task.control_message.commands)

        # Simply log the event
        logger.info("*" * 100)
        logger.info(f"Control task started: ID={task_id}, Device={sn}, Commands={command_count}")
        logger.info("*" * 100)

    def on_task_completed(self, task: Task, success: bool, result: Any = None):
        """
        Called when any task completes execution.
        Filters for ControlDeviceTask instances.
        """
        if not isinstance(task, ControlDeviceTask):
            return

        # Get task details
        task_id = task.control_message.id
        sn = task.control_message.sn
        status = "SUCCESS" if success else "FAILED"

        # Result information
        result_info = ""
        if result and isinstance(result, list):
            result_info = f", Results={[bool(r) for r in result]}"
        else:
            result_info = f", Result={result}"

        # Simply log the event
        logger.info("*" * 100)
        log_fn = logger.info if success else logger.error
        log_fn(f"Control task completed: ID={task_id}, Device={sn}, Status={status}{result_info}")
        logger.info("*" * 100)

    def unregister(self):
        """
        Unregister from the observer when no longer needed
        """
        TaskObserver.get_instance().unregister_listener(self)
        logger.info("Control task monitor unregistered")
