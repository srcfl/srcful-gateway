import time
import logging
import queue
from unittest.mock import MagicMock
import pytest

from server import app

from server.app import main_loop
from server.blackboard import BlackBoard
from server.tasks.itask import ITask


@pytest.fixture
def tasks():
    return queue.PriorityQueue()


@pytest.fixture
def bb():
    return BlackBoard()


def create_normal_task(time):

    def adjust_time_side_effect(new_time):
        task.get_time.return_value = new_time

    task = MagicMock(spec=ITask, time=time)
    task.execute.return_value = None
    task.get_time.return_value = task.time
    task.adjust_time.side_effect = adjust_time_side_effect
    task.__lt__.side_effect = lambda x: task.get_time() < x.get_time()
    return task


@pytest.fixture
def stop_task(bb):

    def raise_stop_iteration(x):
        raise StopIteration

    task = create_normal_task(bb.time_ms() + 500)
    task.execute.side_effect = raise_stop_iteration
    task.get_time.return_value = task.time

    return task


@pytest.fixture
def normal_task(bb):
    return create_normal_task(bb.time_ms() + 500)


@pytest.fixture
def fail_task(bb):

    def raise_exception(x):
        raise Exception

    task = create_normal_task(bb.time_ms() + 500)
    task.execute.side_effect = raise_exception
    return task


def test_app():
    assert app is not None


def test_main_loop_exiting(tasks, bb, stop_task, caplog):
    app.logger.setLevel(level=logging.INFO)
    
    tasks.put(stop_task)
    main_loop(tasks, bb)
    assert "StopIteration received" in caplog.text


def test_main_loop_normal_task(tasks, bb, normal_task, stop_task, caplog):
    app.logger.setLevel(level=logging.INFO)
    
    tasks.put(normal_task)
    tasks.put(stop_task)
    main_loop(tasks, bb)
    assert "StopIteration received" in caplog.text
    assert "is in the past" not in caplog.text
    assert "Failed to execute task:" not in caplog.text


def test_main_loop_future_task(tasks, bb, normal_task, stop_task, caplog):
    app.logger.setLevel(level=logging.INFO)
    
    normal_task.get_time.return_value = bb.time_ms() + 1500
    tasks.put(normal_task)
    tasks.put(stop_task)
    main_loop(tasks, bb)
    assert "StopIteration received" in caplog.text
    assert "is in the past" not in caplog.text
    assert "Failed to execute task:" not in caplog.text


def test_main_loop_past_task(tasks, bb, normal_task, stop_task, caplog):
    app.logger.setLevel(level=logging.INFO)

    child_task = create_normal_task(bb.time_ms() + 500)
    child_task.get_time.return_value = bb.time_ms() - 1500
    normal_task.execute.return_value = child_task

    assert child_task < normal_task
    
    normal_task.get_time.return_value = bb.time_ms() - 1500
    tasks.put(normal_task)
    tasks.put(stop_task)
    main_loop(tasks, bb)
    assert "StopIteration received" in caplog.text
    assert normal_task < child_task
    assert "is in the past " in caplog.text
    assert "Failed to execute task" not in caplog.text

def test_main_loop_task_from_list_same_time(tasks, bb, normal_task, stop_task, caplog):
    app.logger.setLevel(level=logging.INFO)

    child_task1 = create_normal_task(normal_task.get_time() + 100)
    child_task2 = create_normal_task(normal_task.get_time() + 100)
    
    stop_task.adjust_time(normal_task.get_time() + 200)
    normal_task.execute.return_value = [child_task1, child_task2]

    tasks.put(normal_task)
    tasks.put(stop_task)
    main_loop(tasks, bb)
    assert normal_task.execute.called
    assert child_task1.execute.called
    assert child_task2.execute.called

def test_main_loop_task_from_bb(tasks, bb, normal_task, stop_task, caplog):
    app.logger.setLevel(level=logging.INFO)

    child_task = create_normal_task(normal_task.get_time() + 100)
    bb.add_task(child_task)
    stop_task.adjust_time(normal_task.get_time() + 200)
    normal_task.execute.return_value = None

    tasks.put(normal_task)
    tasks.put(stop_task)
    main_loop(tasks, bb)
    assert child_task.execute.called

def test_main_loop_task_from_bb_2(tasks, bb, normal_task, stop_task, caplog):
    app.logger.setLevel(level=logging.INFO)

    child_task = create_normal_task(normal_task.get_time() + 100)
    bb.add_task(child_task)
    stop_task.adjust_time(normal_task.get_time() + 200)
    normal_task.execute.return_value = []

    tasks.put(normal_task)
    tasks.put(stop_task)
    main_loop(tasks, bb)
    assert child_task.execute.called


def test_main_loop_task_failure(tasks, bb, fail_task, stop_task, caplog):
    app.logger.setLevel(level=logging.INFO)

    fail_task.name = "fail_task"
    stop_task.name = "stop_task"
    
    fail_task.adjust_time(bb.time_ms() + 100)
    stop_task.adjust_time(bb.time_ms() + 101)

    assert fail_task < stop_task

    tasks.put(fail_task)
    tasks.put(stop_task)
    main_loop(tasks, bb)
    assert "StopIteration received" in caplog.text
    assert "Failed to execute task" in caplog.text


@pytest.fixture
def short_task(bb):

    def execute_side_effect(x):
        task.execute_time = x
        time.sleep(0.1)

    task = create_normal_task(bb.time_ms() + 500)
    task.execute.side_effect = execute_side_effect
    return task

@pytest.fixture
def long_task(bb):

    def sleep_and_raise_stop_iteration(x):
        time.sleep(2)
        raise StopIteration

    task = create_normal_task(bb.time_ms() + 200)
    task.execute.side_effect = sleep_and_raise_stop_iteration
    return task


def test_main_loop_with_blocking_task(tasks, bb, short_task, long_task):

    short_task.execute_time = 0
    short_task_time = short_task.get_time()
    tasks.put(long_task)
    tasks.put(short_task)

    # assert that short task ios scheduled after long task but not too long after
    assert short_task_time > long_task.get_time()
    assert short_task_time < long_task.get_time() + 500

    main_loop(tasks, bb)

    # assert that the short task was executed
    assert short_task.execute_time > 0

    # assert that the short task was executed while the long task was sleeping
    assert short_task.execute_time <= short_task_time + 500  # we alllow for some time of context switching