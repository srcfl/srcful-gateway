import tempfile
import os
import pytest
from server.storage.gateway_storage import DeviceStorage
from unittest.mock import MagicMock
from server.devices.ICom import ICom


@pytest.fixture
def temp_storage():
    """Create a temporary storage instance for testing"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp:
        db_path = tmp.name

    storage = DeviceStorage(db_path)
    yield storage

    # Cleanup
    if os.path.exists(db_path):
        os.unlink(db_path)


@pytest.fixture
def sample_connection():
    """Sample connection data for testing"""
    return {
        "ip": "192.168.1.10",
        "sn": "A2332407312",
        "mac": "20:f8:3b:00:3c:9d",
        "port": 502,
        "slave_id": 1,
        "connection": "TCP",
        "device_type": "sungrow"
    }


@pytest.fixture
def sample_settings():
    """Sample settings data for testing"""
    return {
        "id": 234648,
        "api": {
            "gql_timeout": 5,
            "ws_endpoint": "wss://api.srcful.dev",
            "gql_endpoint": "https://api.srcful.dev"
        },
        "harvest": {
            "endpoints": ["https://mainnet.srcful.dev/gw/data/"]
        }
    }


def test_storage_initialization(temp_storage):
    """Test that storage initializes correctly"""
    assert temp_storage is not None
    assert os.path.exists(temp_storage.db_path)


def test_add_connection_valid(temp_storage, sample_connection):
    """Test adding a valid connection"""
    # Create a mock ICom object
    mock_com = MagicMock(spec=ICom)
    mock_com.get_config.return_value = sample_connection
    mock_com.get_SN.return_value = sample_connection["sn"]

    result = temp_storage.add_connection(mock_com)
    assert result is True

    connections = temp_storage.get_connections()
    assert len(connections) == 1
    assert connections[0]["sn"] == sample_connection["sn"]


def test_add_connection_invalid_not_dict(temp_storage):
    """Test adding invalid connection (not a dict)"""
    result = temp_storage.add_connection("invalid_string")
    assert result is False

    connections = temp_storage.get_connections()
    assert len(connections) == 0


def test_add_connection_invalid_missing_sn(temp_storage):
    """Test adding invalid connection (missing sn)"""
    invalid_connection = {"ip": "192.168.1.10", "port": 502}
    result = temp_storage.add_connection(invalid_connection)
    assert result is False

    connections = temp_storage.get_connections()
    assert len(connections) == 0


def test_add_connection_duplicate_sn(temp_storage, sample_connection):
    """Test adding connection with duplicate SN updates existing connection"""
    # Add first connection
    mock_com = MagicMock(spec=ICom)
    mock_com.get_config.return_value = sample_connection
    mock_com.get_SN.return_value = sample_connection["sn"]

    result1 = temp_storage.add_connection(mock_com)
    assert result1 is True

    # Add duplicate (same SN, different data)
    duplicate = sample_connection.copy()
    duplicate["ip"] = "192.168.1.20"
    mock_com = MagicMock(spec=ICom)
    mock_com.get_config.return_value = duplicate
    mock_com.get_SN.return_value = duplicate["sn"]

    result2 = temp_storage.add_connection(mock_com)
    assert result2 is True  # Should return True and update existing

    connections = temp_storage.get_connections()
    assert len(connections) == 1  # Should still be only 1 connection
    assert connections[0]["ip"] == "192.168.1.20"  # Should be updated IP


def test_get_connections_empty(temp_storage):
    """Test getting connections when none exist"""
    connections = temp_storage.get_connections()
    assert connections == []


def test_get_connections_multiple(temp_storage):
    """Test getting multiple connections"""
    connection1 = {"sn": "123", "ip": "192.168.1.10"}
    connection2 = {"sn": "456", "ip": "192.168.1.20"}

    mock_com1 = MagicMock(spec=ICom)
    mock_com1.get_config.return_value = connection1
    mock_com1.get_SN.return_value = connection1["sn"]
    temp_storage.add_connection(mock_com1)

    mock_com2 = MagicMock(spec=ICom)
    mock_com2.get_config.return_value = connection2
    temp_storage.add_connection(mock_com2)

    connections = temp_storage.get_connections()
    assert len(connections) == 2

    sns = [c["sn"] for c in connections]
    assert "123" in sns
    assert "456" in sns


def test_remove_connection_existing(temp_storage, sample_connection):
    """Test removing an existing connection"""
    # Add connection first
    mock_com = MagicMock(spec=ICom)
    mock_com.get_config.return_value = sample_connection
    mock_com.get_SN.return_value = sample_connection["sn"]
    temp_storage.add_connection(mock_com)
    assert len(temp_storage.get_connections()) == 1

    # Remove it
    result = temp_storage.remove_connection(sample_connection["sn"])
    assert result is True

    connections = temp_storage.get_connections()
    assert len(connections) == 0


def test_remove_connection_nonexistent(temp_storage):
    """Test removing a non-existent connection"""
    result = temp_storage.remove_connection("nonexistent_sn")
    assert result is False  # Should return False when not found

    connections = temp_storage.get_connections()
    assert len(connections) == 0


def test_remove_connection_from_multiple(temp_storage):
    """Test removing one connection from multiple"""
    connection1 = {"connection": "TCP", "sn": "123", "ip": "192.168.1.10"}
    connection2 = {"connection": "TCP", "sn": "456", "ip": "192.168.1.20"}

    mock_com1 = MagicMock(spec=ICom)
    mock_com1.get_config.return_value = connection1
    mock_com1.get_SN.return_value = connection1["sn"]
    temp_storage.add_connection(mock_com1)

    mock_com2 = MagicMock(spec=ICom)
    mock_com2.get_config.return_value = connection2
    mock_com2.get_SN.return_value = connection2["sn"]
    temp_storage.add_connection(mock_com2)

    assert len(temp_storage.get_connections()) == 2

    # Remove one
    result = temp_storage.remove_connection("123")
    assert result is True

    connections = temp_storage.get_connections()
    assert len(connections) == 1
    assert connections[0]["sn"] == "456"


def test_save_settings_valid(temp_storage, sample_settings):
    """Test saving valid settings"""
    result = temp_storage.save_settings(sample_settings)
    assert result is True

    retrieved_settings = temp_storage.get_settings()
    assert retrieved_settings is not None
    assert retrieved_settings["id"] == sample_settings["id"]


def test_save_settings_invalid(temp_storage):
    """Test saving invalid settings (not a dict)"""
    result = temp_storage.save_settings("invalid_string")
    assert result is False

    settings = temp_storage.get_settings()
    assert settings is None


def test_get_settings_empty(temp_storage):
    """Test getting settings when none exist"""
    settings = temp_storage.get_settings()
    assert settings is None


def test_get_settings_after_save(temp_storage, sample_settings):
    """Test getting settings after saving"""
    temp_storage.save_settings(sample_settings)

    retrieved = temp_storage.get_settings()
    assert retrieved == sample_settings


def test_persistence_across_instances():
    """Test that data persists across storage instances"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp:
        db_path = tmp.name

    try:
        # Create first instance and add data
        storage1 = DeviceStorage(db_path)
        connection = {"connection": "TCP", "sn": "persist_test", "ip": "192.168.1.100"}
        mock_com = MagicMock(spec=ICom)
        mock_com.get_config.return_value = connection
        mock_com.get_SN.return_value = connection["sn"]

        storage1.add_connection(mock_com)

        # Create second instance and verify data exists
        storage2 = DeviceStorage(db_path)
        connections = storage2.get_connections()

        assert len(connections) == 1
        assert connections[0]["sn"] == "persist_test"

    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_corrupted_data_handling(temp_storage):
    """Test handling of corrupted data in storage"""
    # Manually insert corrupted data
    import sqlite3

    with sqlite3.connect(temp_storage.db_path) as conn:
        # Insert invalid JSON
        conn.execute("INSERT OR REPLACE INTO storage (key, value) VALUES ('connections', 'invalid_json')")

    # Should return empty list, not crash
    connections = temp_storage.get_connections()
    assert connections == []


def test_p1_meter_serial_number_support(temp_storage):
    """Test that add_connection and remove_connection work with P1 meters using 'meter_serial_number'"""
    # P1 meter connection with meter_serial_number
    p1_connection = {
        "connection": "P1Telnet",
        "ip": "192.168.1.100",
        "port": 23,
        "meter_serial_number": "LGF5E360"
    }

    # Add P1 connection
    mock_com = MagicMock(spec=ICom)
    mock_com.get_config.return_value = p1_connection
    mock_com.get_SN.return_value = p1_connection["meter_serial_number"]
    result = temp_storage.add_connection(mock_com)
    assert result is True

    # Verify it was added
    connections = temp_storage.get_connections()
    assert len(connections) == 1
    assert connections[0]["meter_serial_number"] == "LGF5E360"

    # Remove by serial number
    result = temp_storage.remove_connection("LGF5E360")
    assert result is True

    # Verify it was removed
    connections = temp_storage.get_connections()
    assert len(connections) == 0


def test_mixed_serial_number_formats(temp_storage):
    """Test that storage can handle both 'sn' and 'meter_serial_number' devices together"""
    # Regular device with 'sn'
    inverter_connection = {"sn": "INV123", "ip": "192.168.1.10", "connection": "TCP"}

    # P1 meter with 'meter_serial_number'
    p1_connection = {
        "connection": "P1Telnet",
        "ip": "192.168.1.100",
        "port": 23,
        "meter_serial_number": "P1_456"
    }

    # Add both
    mock_com1 = MagicMock(spec=ICom)
    mock_com1.get_config.return_value = inverter_connection
    mock_com1.get_SN.return_value = inverter_connection["sn"]
    assert temp_storage.add_connection(mock_com1) is True

    mock_com2 = MagicMock(spec=ICom)
    mock_com2.get_config.return_value = p1_connection
    mock_com2.get_SN.return_value = p1_connection["meter_serial_number"]
    assert temp_storage.add_connection(mock_com2) is True

    # Verify both are there
    connections = temp_storage.get_connections()
    assert len(connections) == 2

    # Remove inverter by sn
    assert temp_storage.remove_connection("INV123") is True
    connections = temp_storage.get_connections()
    assert len(connections) == 1
    assert connections[0]["meter_serial_number"] == "P1_456"

    # Remove P1 meter by meter_serial_number
    assert temp_storage.remove_connection("P1_456") is True
    connections = temp_storage.get_connections()
    assert len(connections) == 0


def test_duplicate_serial_numbers_mixed_formats(temp_storage):
    """Test that duplicate serial numbers are handled correctly across different formats"""
    # First add a regular device
    inverter_connection = {"sn": "SAME123", "ip": "192.168.1.10", "connection": "TCP"}
    mock_com1 = MagicMock(spec=ICom)
    mock_com1.get_config.return_value = inverter_connection
    mock_com1.get_SN.return_value = inverter_connection["sn"]
    assert temp_storage.add_connection(mock_com1) is True

    # Now add a P1 meter with the same serial number
    p1_connection = {
        "connection": "P1Telnet",
        "ip": "192.168.1.100",
        "port": 23,
        "meter_serial_number": "SAME123"
    }
    mock_com2 = MagicMock(spec=ICom)
    mock_com2.get_config.return_value = p1_connection
    mock_com2.get_SN.return_value = p1_connection["meter_serial_number"]
    assert temp_storage.add_connection(mock_com2) is True

    # Should only have one connection (the P1 meter should replace the inverter)
    connections = temp_storage.get_connections()
    assert len(connections) == 1
    assert connections[0]["connection"] == "P1Telnet"
    assert connections[0]["meter_serial_number"] == "SAME123"
