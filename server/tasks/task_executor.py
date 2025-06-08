import logging
from typing import Any, List, Optional, Union
from server.tasks.task import Task
from server.tasks.itask import ITask
from server.tasks.task_observer import TaskObserver

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class TaskExecutor:
    """
    Helper class to execute tasks with observer notifications
    """

    @staticmethod
    def execute_task(task: Task, event_time: int) -> Union[List[ITask], ITask, None]:
        """
        Execute a task with observer notifications

        Args:
            task: The task to execute
            event_time: The current event time

        Returns:
            The result of the task execution (None, a single Task, or a list of Tasks)
        """
        observer = TaskObserver.get_instance()

        # Notify observers that task execution has started
        observer.notify_task_started(task)

        try:
            # Execute the task
            result = task.execute(event_time)
            # Notify observers of task success
            observer.notify_task_completed(task, True, result)
            return result
        except Exception as e:
            logger.error(f"Error executing task {task.__class__.__name__}: {e}")
            # Notify observers of task failure
            observer.notify_task_completed(task, False)
            return None
