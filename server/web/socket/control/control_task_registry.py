from typing import Any, Dict, List
from server.tasks.control_device_task import ControlDeviceTask


class TaskExecutionRegistry:
    """
    The main purpose of this class is to track the tasks and to be able to flag them for cancellation if needed.
    """

    @property
    def size(self) -> int:
        return len(self._registry)

    def __init__(self):
        # registry of tasks and whether they have been acked or not
        self._registry: List[ControlDeviceTask] = []

    def add_task(self, task: ControlDeviceTask):
        """Registers a task when it's created"""
        self._registry.append(task)

    def get_task(self, message_id: int) -> ControlDeviceTask | None:
        """Retrieves a task by its message ID"""
        return next((t for t in self._registry if t.control_message.id == message_id), None)
