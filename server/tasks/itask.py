class ITask:
    """Interface for a task. A task is a unit of work that can be scheduled for execution at a given time.
    Tasks are executed synchronously, so they should not block.
    Blocking operations should be performed in a separate thread. Results should
    then be collected and processed in the task's execute method."""

    def __init__(self):
        pass

    def __eq__(self, other):
        """Override the default Equals behavior. Should return True if the time of the task is equal to the other task or time"""
        raise NotImplementedError("Subclass must implement abstract method")

    def __lt__(self, other):
        """Override the default Less than behavior. Should return True if the time of the task is less than the other task or time"""
        raise NotImplementedError("Subclass must implement abstract method")
    
    def get_time(self) -> int:
        """Return the time of the task in milliseconds"""
        raise NotImplementedError("Subclass must implement abstract method")

    def execute(self, event_time):
        """execute the task, return None a single Task or a list of tasks to be added to the scheduler"""
        # throw a not implemented exception
        raise NotImplementedError("Subclass must implement abstract method")