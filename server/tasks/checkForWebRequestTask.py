from threading import Thread

from server.web.server import Server

from .task import Task


class CheckForWebRequest(Task):
  def __init__(self, eventTime: int, stats: dict, webServer: Server):
    super().__init__(eventTime, stats)
    self.webServer = webServer

  def execute(self, eventTime):
    self.stats['webRequests'] += 1
    if self.webServer.request_queue_size() > 0:
      # launch a new thread to handle the request
      t = Thread(target=self.webServer.handle_request)
      t.start()

    self.time = 1000
    # get all added tasks and put in list
    tasks = [self]
    while not self.webServer.tasks.empty():
      tasks.append(self.webServer.tasks.get())

    # ajust the time for all tasks
    for task in tasks:
      task.time += eventTime

    return tasks
