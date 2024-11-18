'''
Interface for a task source
'''

from abc import ABC, abstractmethod

from server.tasks.itask import ITask

class ITaskSource(ABC):
    @abstractmethod
    def add_task(self, task: ITask):
        """
        Add a task to the source
        """
        pass

    @abstractmethod
    def purge_tasks(self) -> list[ITask]:
        """
        Purge all tasks from the source and return them
        """
        pass
