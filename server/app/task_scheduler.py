import logging
import threading
import queue
from concurrent.futures import ThreadPoolExecutor

from server.app.isystem_time import ISystemTime
from server.tasks.itask import ITask

logger = logging.getLogger(__name__)


class TaskScheduler:

    def __init__(self, max_workers: int, system_time: ISystemTime):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.tasks: queue.PriorityQueue = queue.PriorityQueue()
        self.active_threads = 0
        self.new_tasks_condition = threading.Condition()
        self.stop_event = threading.Event()
        self.system_time = system_time

    
    def add_task(self, task: ITask):
        with self.new_tasks_condition:

            if task.get_time() <= self.system_time.time_ms():
                logger.warning("Task (%s) is in the past by %d ms, adjusting time to now", task, self.system_time.time_ms() - task.get_time())
                task.adjust_time(self.system_time.time_ms() + 100)

            self.tasks.put(task)
            self.new_tasks_condition.notify()

    def stop(self):
        self.stop_event.set()

    def worker(self, task: ITask):
        try:
            new_tasks = task.execute(self.system_time.time_ms())
            if new_tasks is None:
                new_tasks = []
        except StopIteration:
            logger.info("StopIteration received, stopping TaskScheduler")
            self.stop()
            new_tasks = None
        except Exception as e:
            logging.error(f"Failed to execute task {task}: {e}")
            new_tasks = None
            
        if new_tasks is not None:
            if not isinstance(new_tasks, list):
                new_tasks_list = [new_tasks]
            else:
                new_tasks_list = new_tasks
            new_tasks_list = new_tasks_list
            for new_task in new_tasks_list:
                self.add_task(new_task)
        
        with self.new_tasks_condition:
            self.active_threads -= 1
            self.new_tasks_condition.notify()

    def main_loop(self):
        while not self.stop_event.is_set():
            with self.new_tasks_condition:
                while (self.active_threads >= self.executor._max_workers) or self.tasks.empty() or self.tasks.queue[0].get_time() > self.bb.time_ms():
                    if self.stop_event.is_set():
                        break

                    if not self.tasks.empty():
                        # wake the loop up gain when the next task is due (note that it may wake up before that if a new task is added)
                        delay = max(0, (self.tasks.queue[0].get_time() - self.bb.time_ms()) / 1000)
                        self.new_tasks_condition.wait(delay)
                    else:
                        self.new_tasks_condition.wait()

                if self.stop_event.is_set():
                    break
                
                if not self.tasks.empty() and self.tasks.queue[0].get_time() <= self.bb.time_ms():
                    task = self.tasks.get()
                    self.executor.submit(self.worker, task)
                    self.active_threads += 1