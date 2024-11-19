import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch

from server.backend.der import DER
from server.backend.connection import Connection
from server.backend.histogram import Histogram, SolarHistogram

@pytest.fixture
def solar_der():
    return DER("SOLAR123", DER.Type.SOLAR)

@pytest.fixture
def resolution():
    return Histogram.Resolution(Histogram.Resolution.Type.MINUTE, 5)

@pytest.fixture
def time_range():
    return (
        datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc),
        datetime(2024, 1, 1, 13, 0, tzinfo=timezone.utc)
    )

@pytest.fixture
def mock_connection():
    connection = Mock(spec=Connection)
    connection.post.return_value = {
        "data": {
            "derData": {
                "solar": {
                    "histogram": [
                        {
                            "ts": "2024-01-01T12:00:00+00:00",
                            "power": 1000.5
                        },
                        {
                            "ts": "2024-01-01T12:05:00+00:00",
                            "power": 1200.75
                        }
                    ]
                }
            }
        }
    }
    return connection

def test_der_initialization():
    der = DER("TEST123", DER.Type.SOLAR)
    assert der.serial == "TEST123"
    assert der.type == DER.Type.SOLAR

def test_construct_query(solar_der, time_range, resolution):
    start_time, end_time = time_range
    query = solar_der._construct_query(start_time, end_time, resolution)
    
    # Verify query structure
    assert 'derData' in query
    assert 'solar(sn:"SOLAR123")' in query
    assert 'start: "2024-01-01T12:00:00+00:00"' in query
    assert 'stop: "2024-01-01T13:00:00+00:00"' in query
    assert 'resolution: "5m"' in query

def test_histogram(solar_der, time_range, resolution, mock_connection):
    start_time, end_time = time_range
    
    # Test
    data = solar_der.histogram(mock_connection, start_time, end_time, resolution)
    
    # Verify connection was called with correct query
    mock_connection.post.assert_called_once()
    query = mock_connection.post.call_args[0][0]
    assert 'solar(sn:"SOLAR123")' in query
    
    # Verify response handling
    assert len(data) == 2
    assert isinstance(data[0], SolarHistogram.Data)
    assert data[0].ts == datetime.fromisoformat("2024-01-01T12:00:00+00:00")
    assert data[0].power == 1000.5

@patch('server.backend.der.datetime')
def test_histogram_from_now(mock_datetime, solar_der, resolution, mock_connection):
    # Setup mock datetime
    fixed_now = datetime(2024, 1, 1, 13, 0, tzinfo=timezone.utc)
    mock_datetime.now.return_value = fixed_now
    
    # Test
    delta = timedelta(hours=1)
    data = solar_der.histogram_from_now(mock_connection, delta, resolution)
    
    # Verify connection was called
    mock_connection.post.assert_called_once()
    query = mock_connection.post.call_args[0][0]
    
    # Verify time calculation in query
    assert 'start: "2024-01-01T12:00:00+00:00"' in query
    assert 'stop: "2024-01-01T13:00:00+00:00"' in query
    
    # Verify response handling
    assert len(data) == 2
    assert isinstance(data[0], SolarHistogram.Data)

def test_histogram_invalid_response(solar_der, time_range, resolution):
    start_time, end_time = time_range
    
    # Setup mock connection with invalid response
    connection = Mock(spec=Connection)
    connection.post.return_value = {"data": {"derData": {"solar": {"histogram": None}}}}
    
    # Test
    with pytest.raises(TypeError):
        solar_der.histogram(connection, start_time, end_time, resolution)

def test_histogram_missing_data(solar_der, time_range, resolution):
    start_time, end_time = time_range
    
    # Setup mock connection with missing data
    connection = Mock(spec=Connection)
    connection.post.return_value = {"data": {"derData": {"solar": {}}}}
    
    # Test
    with pytest.raises(KeyError):
        solar_der.histogram(connection, start_time, end_time, resolution)

def test_histogram_empty_response(solar_der, time_range, resolution):
    start_time, end_time = time_range
    
    # Setup mock connection with empty histogram
    connection = Mock(spec=Connection)
    connection.post.return_value = {
        "data": {
            "derData": {
                "solar": {
                    "histogram": []
                }
            }
        }
    }
    
    # Test
    data = solar_der.histogram(connection, start_time, end_time, resolution)
    assert len(data) == 0