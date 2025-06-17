import tempfile
import os
import pytest
from server.storage.gateway_storage import GatewayStorage


@pytest.fixture
def temp_storage():
    """Create a temporary storage instance for testing"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp:
        db_path = tmp.name

    storage = GatewayStorage(db_path)
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
    result = temp_storage.add_connection(sample_connection)
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
    result1 = temp_storage.add_connection(sample_connection)
    assert result1 is True

    # Add duplicate (same SN, different data)
    duplicate = sample_connection.copy()
    duplicate["ip"] = "192.168.1.20"
    result2 = temp_storage.add_connection(duplicate)
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

    temp_storage.add_connection(connection1)
    temp_storage.add_connection(connection2)

    connections = temp_storage.get_connections()
    assert len(connections) == 2

    sns = [c["sn"] for c in connections]
    assert "123" in sns
    assert "456" in sns


def test_remove_connection_existing(temp_storage, sample_connection):
    """Test removing an existing connection"""
    # Add connection first
    temp_storage.add_connection(sample_connection)
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
    connection1 = {"sn": "123", "ip": "192.168.1.10"}
    connection2 = {"sn": "456", "ip": "192.168.1.20"}

    temp_storage.add_connection(connection1)
    temp_storage.add_connection(connection2)
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
        storage1 = GatewayStorage(db_path)
        connection = {"sn": "persist_test", "ip": "192.168.1.100"}
        storage1.add_connection(connection)

        # Create second instance and verify data exists
        storage2 = GatewayStorage(db_path)
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


def test_mixed_data_types_in_connections(temp_storage):
    """Test that add_connection properly rejects invalid data types"""
    # Try to add various invalid data types - all should be rejected
    invalid_data = [
        "invalid_string",
        123,  # Invalid number
        {"invalid": "no_sn"},  # Invalid dict without sn
        {"sn": ""},  # Empty sn
        {"sn": None},  # None sn
    ]

    for invalid in invalid_data:
        result = temp_storage.add_connection(invalid)
        assert result is False

    # Add valid connections
    valid_connections = [
        {"sn": "valid1", "ip": "192.168.1.10"},
        {"sn": "valid2", "ip": "192.168.1.20"}
    ]

    for valid in valid_connections:
        result = temp_storage.add_connection(valid)
        assert result is True

    # Should only have the 2 valid connections
    connections = temp_storage.get_connections()
    assert len(connections) == 2

    sns = [c["sn"] for c in connections]
    assert "valid1" in sns
    assert "valid2" in sns
