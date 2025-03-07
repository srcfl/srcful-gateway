from typing import Any, Dict, List
from server.tasks.control_device_task import ControlDeviceTask


class TaskExecutionRegistry:
    """
    Tracks the execution status and results of control device tasks
    """

    def __init__(self):
        # registry of tasks and whether they have been acked or not
        self._registry: List[ControlDeviceTask] = []

    def register_task_result(self, task: ControlDeviceTask):
        """Records the execution result of a task"""
        self._registry.append(task)

    def get_task_result(self, message_id: str) -> ControlDeviceTask:
        """Retrieves the execution result for a given task"""
        return next((task for task in self._registry if task.control_message.id == message_id), None)

    def get_all_results(self) -> List[ControlDeviceTask]:
        """Returns all tracked task results"""
        return self._registry
