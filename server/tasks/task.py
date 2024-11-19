from server.app.blackboard import BlackBoard
from .itask import ITask


class Task(ITask):
    """Base class for tasks that hold a time and a blackboard object"""
    bb: BlackBoard
    time: int

    def __init__(self, event_time: int, bb: BlackBoard):
        self.time = event_time
        self.bb = bb

    def get_time(self) -> int:
        return self.time

    def adjust_time(self, new_time: int):
        self.time = new_time
