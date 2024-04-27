from server.blackboard import BlackBoard
from unittest.mock import MagicMock
from server.message import Message
import pytest
import time


def test_blackboard():
    bb = BlackBoard()
    assert bb is not None
    assert bb.inverters is not None
    assert bb.inverters.lst is not None

def test_blackboard_get_version():
    bb = BlackBoard()

    # assert that string contains two dots
    assert bb.get_version().count(".") == 2

def test_blackboard_add_inverter():
    listener = MagicMock()
    bb = BlackBoard()
    inverter = MagicMock()
    bb.inverters.add_listener(listener)
    bb.inverters.add(inverter)
    assert inverter in bb.inverters.lst
    assert listener.add_inverter.called


def test_blackboard_remove_inverter():
    listener = MagicMock()
    bb = BlackBoard()
    inverter = MagicMock()
    bb.inverters.add_listener(listener)
    bb.inverters.add(inverter)
    bb.inverters.remove(inverter)
    assert inverter not in bb.inverters.lst
    assert listener.remove - inverter.called


@pytest.fixture
def message_container() -> BlackBoard:
    return BlackBoard()  # Replace with actual constructor if there are parameters

@pytest.fixture
def test_messages():
    return [
        "Test error message",
        "Test warning message",
        "Test info message"
    ]

def test_add_error(message_container, test_messages):
    msg = test_messages[0]
    message_container.add_error(msg)
    assert any(m.message == msg and m.type == Message.Type.Error for m in message_container.messages)

def test_add_warning(message_container, test_messages):
    msg = test_messages[1]
    message_container.add_warning(msg)
    assert any(m.message == msg and m.type == Message.Type.Warning for m in message_container.messages)

def test_add_info(message_container, test_messages):
    msg = test_messages[2]
    message_container.add_info(msg)
    assert any(m.message == msg and m.type == Message.Type.Info for m in message_container.messages)

def test_clear_messages(message_container, test_messages):
    for msg in test_messages:
        message_container.add_error(msg)
    message_container.clear_messages()
    assert len(message_container.messages) == 0

def test_delete_message(message_container, test_messages):
    for msg in test_messages:
        message_container.add_error(msg)

    messages_len_before_deletion = len(message_container.messages)
    id_to_delete = message_container.messages[0].id

    assert message_container.delete_message(id_to_delete)
    assert all(m.id != id_to_delete for m in message_container.messages)
    assert messages_len_before_deletion - 1 == len(message_container.messages)

def test_get_messages(message_container, test_messages):
    for msg in test_messages:
        message_container.add_error(msg)
    messages = message_container.messages
    assert len(messages) == len(test_messages)
    for m in messages:
        assert m.message in test_messages

def test_duplicate_message_updates_timestamp(message_container):
    test_message = "Duplicate message"
    message_container.add_error(test_message)
    initial_timestamp = message_container.messages[0].timestamp

    # sleep for a second to ensure the timestamp is different
    import time
    time.sleep(1)
    message_container.add_error(test_message)
    final_timestamp = message_container.messages[0].timestamp
    assert final_timestamp != initial_timestamp
    assert len(message_container.messages) == 1

def test_message_list_limit(message_container):
    for i in range(15):
        message_container.add_error(f"Overflow message {i}")
    messages = message_container.messages
    assert len(messages) <= 10

def test_time_ms():
    bb = BlackBoard()
    # the time must be an UTC time that corresponds to the current time
    assert bb.time_ms() <= int(time.time() * 1000)

def test_elapsed_time():
    start_time = time.monotonic_ns() // 1_000_000
    bb = BlackBoard()

    time.sleep(0.2)
    end_time = time.monotonic_ns() // 1_000_000

    diff = bb.elapsed_time - (end_time - start_time)  
    
    assert abs(diff) < 10
