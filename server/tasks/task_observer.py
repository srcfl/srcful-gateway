import logging
from typing import List, Optional, Any
import threading
from server.tasks.task import Task

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class TaskObserver:
    """
    Observer for Task that notifies listeners when any task is executed.
    This class follows the observer pattern to decouple task execution from notification.
    """

    _instance = None
    _lock = threading.Lock()

    @classmethod
    def get_instance(cls):
        """
        Singleton pattern to ensure only one observer exists
        """
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
            return cls._instance

    def __init__(self):
        self.listeners = []

    def register_listener(self, listener):
        """
        Register a listener to receive notifications
        """
        if listener not in self.listeners:
            self.listeners.append(listener)
            logger.info(f"Registered listener: {listener}")

    def unregister_listener(self, listener):
        """
        Unregister a listener
        """
        if listener in self.listeners:
            self.listeners.remove(listener)
            logger.info(f"Unregistered listener: {listener}")

    def notify_task_started(self, task: Task):
        """
        Notify all listeners that a task has started execution
        """
        # logger.info(f"Notifying {len(self.listeners)} listeners that task {task.__class__.__name__} started")

        for listener in self.listeners:
            try:
                listener.on_task_started(task)
            except Exception as e:
                logger.error(f"Error notifying listener about task start: {e}")

    def notify_task_completed(self, task: Task, success: bool, result: Any = None):
        """
        Notify all listeners that a task has completed execution

        Args:
            task: The completed task
            success: Whether the task completed successfully
            result: Optional result from task execution
        """
        # logger.info(f"Notifying {len(self.listeners)} listeners that task {task.__class__.__name__} completed with status: {success}")

        for listener in self.listeners:
            try:
                listener.on_task_completed(task, success, result)
            except Exception as e:
                logger.error(f"Error notifying listener about task completion: {e}")


class TaskListener:
    """
    Interface for listeners that want to be notified of task events
    Implement this interface to receive notifications
    """

    def on_task_started(self, task: Task):
        """
        Called when a task starts execution

        Args:
            task: The task that started executing
        """
        pass

    def on_task_completed(self, task: Task, success: bool, result: Any = None):
        """
        Called when a task completes execution

        Args:
            task: The completed task
            success: Whether the task completed successfully
            result: Optional result from task execution
        """
        pass
