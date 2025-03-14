from server.app.blackboard import BlackBoard
from unittest.mock import MagicMock, Mock
from server.app.message import Message
from server.crypto.crypto_state import CryptoState
import pytest
import time


def test_blackboard():
    bb = BlackBoard(Mock(spec=CryptoState))
    assert bb is not None
    assert bb.devices is not None
    assert bb.devices.lst is not None
    assert bb.settings is not None
    assert len(bb.settings.harvest.endpoints) > 0


def test_blackboard_get_version():
    bb = BlackBoard(Mock(spec=CryptoState))

    # assert that string contains two dots
    assert bb.get_version().count(".") == 2


def test_blackboard_add_device():
    listener = MagicMock()
    bb = BlackBoard(Mock(spec=CryptoState))
    hw = MagicMock()
    bb.devices.add_listener(listener)
    bb.devices.add(hw)
    assert hw in bb.devices.lst
    assert listener.add_device.called


def test_blackboard_remove_device():
    listener = MagicMock()
    bb = BlackBoard(Mock(spec=CryptoState))
    hw = MagicMock()
    bb.devices.add_listener(listener)
    bb.devices.add(hw)
    bb.devices.remove(hw)
    assert hw not in bb.devices.lst
    assert listener.remove - hw.called


@pytest.fixture
def message_container() -> BlackBoard:
    return BlackBoard(Mock(spec=CryptoState))  # Replace with actual constructor if there are parameters


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
    bb = BlackBoard(Mock(spec=CryptoState))
    # the time must be an UTC time that corresponds to the current time
    assert bb.time_ms() <= int(time.time() * 1000)


def test_elapsed_time():
    start_time = time.monotonic_ns() // 1_000_000
    bb = BlackBoard(Mock(spec=CryptoState))

    time.sleep(0.2)
    end_time = time.monotonic_ns() // 1_000_000

    diff = bb.elapsed_time() - (end_time - start_time)

    assert abs(diff) < 10


def test_chip_death_count():
    bb = BlackBoard(Mock(spec=CryptoState))
    assert bb.chip_death_count == 0
    bb.increment_chip_death_count()
    assert bb.chip_death_count == 1
    bb.increment_chip_death_count()
    assert bb.chip_death_count == 2
    bb.reset_chip_death_count()
    assert bb.chip_death_count == 0


def test_add_multiple_devices():
    bb = BlackBoard(Mock(spec=CryptoState))
    hw = MagicMock()
    hw.get_name.return_value = "Test device"
    hw.get_SN.return_value = "1234567890"
    bb.devices.add(hw)
    assert len(bb.devices.lst) == 1
