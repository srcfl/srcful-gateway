import time
import logging
import queue
from unittest.mock import MagicMock
import pytest

from server.app import app
from server.app import task_scheduler

from server.app.blackboard import BlackBoard
from server.tasks.itask import ITask


@pytest.fixture
def bb():
    return BlackBoard()
@pytest.fixture
def scheduler(bb):
    return task_scheduler.TaskScheduler(max_workers=4, system_time=bb, task_source=bb)

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


def test_main_loop_exiting(scheduler, bb, stop_task, caplog):
    task_scheduler.logger.setLevel(level=logging.INFO)
    
    scheduler.add_task(stop_task)
    scheduler.main_loop()
    assert "StopIteration received" in caplog.text


def test_main_loop_normal_task(scheduler, bb, normal_task, stop_task, caplog):
    task_scheduler.logger.setLevel(level=logging.INFO)
    
    scheduler.add_task(normal_task)
    scheduler.add_task(stop_task)
    scheduler.main_loop()
    assert "StopIteration received" in caplog.text
    assert "is in the past" not in caplog.text
    assert "Failed to execute task:" not in caplog.text


def test_main_loop_future_task(scheduler, bb, normal_task, stop_task, caplog):
    task_scheduler.logger.setLevel(level=logging.INFO)
    
    normal_task.get_time.return_value = bb.time_ms() + 1500
    scheduler.add_task(normal_task)
    scheduler.add_task(stop_task)
    scheduler.main_loop()
    assert "StopIteration received" in caplog.text
    assert "is in the past" not in caplog.text
    assert "Failed to execute task:" not in caplog.text


def test_main_loop_past_task(scheduler, bb, normal_task, stop_task, caplog):
    task_scheduler.logger.setLevel(level=logging.INFO)

    child_task = create_normal_task(bb.time_ms() - 1500)
    normal_task.execute.return_value = child_task

    assert normal_task < stop_task
    assert child_task < stop_task
    assert child_task < normal_task
    
    normal_task.get_time.return_value = bb.time_ms() - 1500
    scheduler.add_task(normal_task)
    scheduler.add_task(stop_task)
    scheduler.main_loop()
    assert "StopIteration received" in caplog.text
    assert "is in the past " in caplog.text
    assert normal_task < child_task
    assert "Failed to execute task" not in caplog.text

def test_main_loop_task_from_list_same_time(scheduler, bb, normal_task, stop_task, caplog):
    task_scheduler.logger.setLevel(level=logging.INFO)

    child_task1 = create_normal_task(normal_task.get_time() + 100)
    child_task2 = create_normal_task(normal_task.get_time() + 100)
    
    stop_task.adjust_time(normal_task.get_time() + 200)
    normal_task.execute.return_value = [child_task1, child_task2]

    scheduler.add_task(normal_task)
    scheduler.add_task(stop_task)
    scheduler.main_loop()
    assert normal_task.execute.called
    assert child_task1.execute.called
    assert child_task2.execute.called

def test_main_loop_task_from_bb(scheduler, bb, normal_task, stop_task, caplog):
    task_scheduler.logger.setLevel(level=logging.INFO)

    child_task = create_normal_task(normal_task.get_time() + 100)
    bb.add_task(child_task)
    stop_task.adjust_time(normal_task.get_time() + 200)
    normal_task.execute.return_value = None

    scheduler.add_task(normal_task)
    scheduler.add_task(stop_task)
    scheduler.main_loop()
    assert child_task.execute.called

def test_main_loop_task_from_bb_2(scheduler, bb, normal_task, stop_task, caplog):
    task_scheduler.logger.setLevel(level=logging.INFO)

    child_task = create_normal_task(normal_task.get_time() + 100)
    bb.add_task(child_task)
    stop_task.adjust_time(normal_task.get_time() + 200)
    normal_task.execute.return_value = []

    scheduler.add_task(normal_task)
    scheduler.add_task(stop_task)
    scheduler.main_loop()
    assert child_task.execute.called


def test_main_loop_task_failure(scheduler, bb, fail_task, stop_task, caplog):
    task_scheduler.logger.setLevel(level=logging.INFO)

    fail_task.name = "fail_task"
    stop_task.name = "stop_task"
    
    fail_task.adjust_time(bb.time_ms() + 100)
    stop_task.adjust_time(bb.time_ms() + 101)

    assert fail_task < stop_task

    scheduler.add_task(fail_task)
    scheduler.add_task(stop_task)
    scheduler.main_loop()
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


def test_main_loop_with_blocking_task(scheduler, bb, short_task, long_task):

    short_task.execute_time = 0
    short_task_time = short_task.get_time()
    scheduler.add_task(long_task)
    scheduler.add_task(short_task)

    # assert that short task ios scheduled after long task but not too long after
    assert short_task_time > long_task.get_time()
    assert short_task_time < long_task.get_time() + 500

    scheduler.main_loop()

    # assert that the short task was executed
    assert short_task.execute_time > 0

    # assert that the short task was executed while the long task was sleeping
    assert short_task.execute_time <= short_task_time + 500  # we alllow for some time of context switching