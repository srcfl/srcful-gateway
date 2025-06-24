"""
Global test fixtures for server unit tests.

This module provides shared fixtures that solve the SQLite database issue
when testing components that use BlackBoard.

PROBLEM:
BlackBoard now initializes a DeviceStorage with an SQLite database at 
/data/srcful/gateway.db. In test environments, this path doesn't exist 
or isn't writable, causing sqlite3.OperationalError.

SOLUTION:
These fixtures create temporary SQLite database files for testing and
automatically clean them up afterward. This provides:
- Real database functionality during tests
- Isolated test data (each test gets its own DB)
- Automatic cleanup
- Better test coverage than mocking

USAGE:
Simply use `blackboard` or `bb` as a fixture parameter in your test functions:

    def test_my_function(blackboard):
        # blackboard is a fully functional BlackBoard with temp database
        assert blackboard.settings is not None

MIGRATION:
If you have existing tests with local BlackBoard fixtures, remove them
and use these global fixtures instead. The global fixtures will be
automatically discovered by pytest.
"""

import tempfile
import os
from unittest.mock import Mock, patch
import pytest

from server.app.blackboard import BlackBoard
from server.crypto.crypto_state import CryptoState
from server.storage.gateway_storage import DeviceStorage


@pytest.fixture
def temp_db_path():
    """Create a temporary database file path for testing"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp:
        db_path = tmp.name

    yield db_path

    # Cleanup
    if os.path.exists(db_path):
        os.unlink(db_path)


@pytest.fixture
def blackboard(temp_db_path):
    """Create a BlackBoard instance with temporary database for testing.

    This fixture is available to all unit tests and provides a properly
    initialized BlackBoard with a temporary SQLite database.
    """
    with patch('server.app.blackboard.DeviceStorage') as mock_storage_class:
        mock_storage_class.return_value = DeviceStorage(temp_db_path)
        return BlackBoard(Mock(spec=CryptoState))


@pytest.fixture
def bb(temp_db_path):
    """Alias for blackboard fixture - shorter name for convenience"""
    with patch('server.app.blackboard.DeviceStorage') as mock_storage_class:
        mock_storage_class.return_value = DeviceStorage(temp_db_path)
        return BlackBoard(Mock(spec=CryptoState))
