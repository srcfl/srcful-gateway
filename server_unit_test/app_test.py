from server import app
import queue
from unittest.mock import MagicMock
import pytest
from server.app import main_loop
from server.blackboard import BlackBoard
from server.tasks.itask import ITask
import logging


@pytest.fixture
def tasks():
    return queue.PriorityQueue()

@pytest.fixture
def bb():
    return BlackBoard()

def create_normal_task(bb):

    def adjust_time_side_effect(new_time):
        task.get_time.return_value = new_time

    task = MagicMock(spec=ITask, time=bb.time_ms() + 500)
    task.execute.return_value = None
    task.get_time.return_value = task.time
    task.adjust_time.side_effect = adjust_time_side_effect
    task.__lt__.side_effect = lambda x: task.get_time() < x.get_time()
    return task

@pytest.fixture
def stop_task(bb):
    task = MagicMock(spec=ITask, time=bb.time_ms() + 500)
    task.execute.side_effect = StopIteration
    task.get_time.return_value = task.time
    task.adjust_time.side_effect = lambda x: setattr(task, "time", x)
    task.__lt__.side_effect = lambda x: task.get_time() < x.get_time()
    return task


@pytest.fixture
def normal_task(bb):
    return create_normal_task(bb)

@pytest.fixture
def fail_task(bb):
    task = MagicMock(spec=ITask, time=bb.time_ms() + 500)
    task.execute.side_effect = Exception
    task.get_time.return_value = task.time
    task.adjust_time.side_effect = lambda x: setattr(task, "time", x)
    task.__lt__.side_effect = lambda x: task.get_time() < x.get_time()
    return task

def test_app():
    assert app is not None

def test_main_loop_exiting(tasks, bb, stop_task, caplog):
    app.logger.setLevel(level=logging.INFO)
    
    tasks.put(stop_task)
    main_loop(tasks, bb)
    assert "StopIteration received, exiting main loop" in caplog.text

def test_main_loop_normal_task(tasks, bb, normal_task, stop_task, caplog):
    app.logger.setLevel(level=logging.INFO)
    
    tasks.put(normal_task)
    tasks.put(stop_task)
    main_loop(tasks, bb)
    assert "StopIteration received, exiting main loop" in caplog.text
    assert "task <class 'unittest.mock.MagicMock'> is in the past 0 adjusting time" not in caplog.text
    assert "Failed to execute task:" not in caplog.text

def test_main_loop_future_task(tasks, bb, normal_task, stop_task, caplog):
    app.logger.setLevel(level=logging.INFO)
    
    normal_task.get_time.return_value = bb.time_ms() + 1500
    tasks.put(normal_task)
    tasks.put(stop_task)
    main_loop(tasks, bb)
    assert "StopIteration received, exiting main loop" in caplog.text
    assert "task <class 'unittest.mock.MagicMock'> is in the past 0 adjusting time" not in caplog.text
    assert "Failed to execute task:" not in caplog.text

def test_main_loop_past_task(tasks, bb, normal_task, stop_task, caplog):
    app.logger.setLevel(level=logging.INFO)

    child_task = create_normal_task(bb)
    child_task.get_time.return_value = bb.time_ms() - 1500
    normal_task.execute.return_value = child_task

    assert child_task < normal_task
    
    normal_task.get_time.return_value = bb.time_ms() - 1500
    tasks.put(normal_task)
    tasks.put(stop_task)
    main_loop(tasks, bb)
    assert "StopIteration received, exiting main loop" in caplog.text
    assert normal_task < child_task
    assert "task <class 'unittest.mock.MagicMock'> is in the past " in caplog.text
    assert "Failed to execute task:" not in caplog.text

def test_main_loop_task_failure(tasks, bb, fail_task, stop_task, caplog):
    app.logger.setLevel(level=logging.INFO)
    
    tasks.put(fail_task)
    tasks.put(stop_task)
    main_loop(tasks, bb)
    assert "StopIteration received, exiting main loop" in caplog.text
    assert "Failed to execute task:" in caplog.text