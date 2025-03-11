from typing import Any, Dict, List
from server.tasks.control_device_task import ControlDeviceTask


class TaskExecutionRegistry:
    """
    Tracks the execution status and results of control device tasks
    """

    def __init__(self):
        # registry of tasks and whether they have been acked or not
        self._registry: List[ControlDeviceTask] = []

    def add_task(self, task: ControlDeviceTask):
        """Registers a task when it's created"""
        self._registry.append(task)

    def update_task(self, task: ControlDeviceTask) -> bool:
        """Updates a task when it's updated"""
        for t in self._registry:
            if t.control_message.id == task.control_message.id:
                t = task
                return True
        return False

    def register_task_result(self, task: ControlDeviceTask):
        """Records the execution result of a task"""
        self._registry.append(task)

    def get_task(self, message_id: str) -> ControlDeviceTask | None:
        """Retrieves a task by its message ID"""
        return next((t for t in self._registry if t.control_message.id == message_id), None)

    def get_tasks(self) -> List[ControlDeviceTask]:
        """Returns a copy of the tracked tasks"""
        return self._registry.copy()
