import server.crypto.revive_run as revive_run

from server.blackboard import BlackBoard
from .task import Task


class CryptoReviveTask(Task):
    """Task to revive the crypto chip"""

    def __init__(self, event_time: int, bb: BlackBoard):
        super().__init__(event_time, bb)

    def execute(self, event_time) -> Task | list[Task]:

        revive_run.as_process()
        self.adjust_time(self.bb.time_ms() + 60000 * 45)
        return [self]
