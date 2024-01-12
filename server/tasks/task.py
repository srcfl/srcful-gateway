from server.blackboard import BlackBoard

class Task:
  '''A task is a unit of work that can be scheduled for execution at a given time.
     Tasks are executed synchronously, so they should not block.
     Blocking operations should be performed in a separate thread. Results should 
     then be collected and processed in the task's execute method.'''

  def __init__(self, eventTime: int, bb: BlackBoard):
    self.time = eventTime
    self.bb = bb

  def __eq__(self, other):
    if not isinstance(other, Task):
      return self.time == other
    return self.time == other.prio

  def __lt__(self, other):
    if not isinstance(other, Task):
      return self.time < other
    return self.time < other.time

  def execute(self):
    '''execute the task, return None a single Task or a list of tasks to be added to the scheduler'''
    # throw a not implemented exception
    raise NotImplementedError("Subclass must implement abstract method")
