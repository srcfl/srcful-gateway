from server.blackboard import BlackBoard
from .itask import ITask


class Task(ITask):
    """Base class for tasks that hold a time and a blackboard object"""

    def __init__(self, event_time: int, bb: BlackBoard):
        self.time = event_time
        self.bb = bb

    def __eq__(self, other):
        if not isinstance(other, Task):
            return self.time == other
        return self.time == other.prio

    def __lt__(self, other):
        if not isinstance(other, Task):
            return self.time < other
        return self.time < other.time

    def get_time(self) -> int:
        return self.time

    def execute(self, event_time):
        """execute the task, return None a single Task or a list of tasks to be added to the scheduler"""
        # throw a not implemented exception
        raise NotImplementedError("Subclass must implement abstract method")
