import pytest
from datetime import datetime, timezone
from server.backend.histogram import Histogram, SolarHistogram

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
def sample_histogram_data():
    return [
        {
            "ts": "2024-01-01T12:00:00+00:00",
            "power": 1000.5
        },
        {
            "ts": "2024-01-01T12:05:00+00:00",
            "power": 1200.75
        }
    ]

def test_resolution_type_values():
    assert Histogram.Resolution.Type.SECOND.value == "s"
    assert Histogram.Resolution.Type.MINUTE.value == "m"
    assert Histogram.Resolution.Type.HOUR.value == "h"
    assert Histogram.Resolution.Type.DAY.value == "d"

def test_resolution_value_format(resolution):
    assert resolution.value == "5m"

def test_resolution_default_count():
    res = Histogram.Resolution(Histogram.Resolution.Type.HOUR)
    assert res.count == 1
    assert res.value == "1h"

def test_solar_histogram_construct_query(resolution, time_range):
    start_time, end_time = time_range
    query = SolarHistogram.construct_query("TEST123", start_time, end_time, resolution)
    
    # Verify query structure
    assert 'start: "2024-01-01T12:00:00+00:00"' in query
    assert 'stop: "2024-01-01T13:00:00+00:00"' in query
    assert 'resolution: "5m"' in query
    assert "ts" in query
    assert "power" in query

def test_solar_histogram_from_dict(sample_histogram_data):
    data_points = SolarHistogram.from_dict(sample_histogram_data)
    
    assert len(data_points) == 2
    
    # Check first data point
    assert isinstance(data_points[0], SolarHistogram.Data)
    assert data_points[0].ts == datetime.fromisoformat("2024-01-01T12:00:00+00:00")
    assert data_points[0].power == 1000.5
    
    # Check second data point
    assert isinstance(data_points[1], SolarHistogram.Data)
    assert data_points[1].ts == datetime.fromisoformat("2024-01-01T12:05:00+00:00")
    assert data_points[1].power == 1200.75

def test_solar_histogram_data_properties():
    test_time = datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc)
    test_power = 1000.5
    
    data_point = SolarHistogram.Data(test_time, test_power)
    
    assert data_point.ts == test_time
    assert data_point.power == test_power

@pytest.mark.parametrize("res_type,count,expected", [
    (Histogram.Resolution.Type.SECOND, 30, "30s"),
    (Histogram.Resolution.Type.MINUTE, 15, "15m"),
    (Histogram.Resolution.Type.HOUR, 2, "2h"),
    (Histogram.Resolution.Type.DAY, 1, "1d"),
])
def test_resolution_variations(res_type, count, expected):
    resolution = Histogram.Resolution(res_type, count)
    assert resolution.value == expected

def test_solar_histogram_from_dict_empty():
    data_points = SolarHistogram.from_dict([])
    assert len(data_points) == 0

def test_solar_histogram_data_immutability():
    test_time = datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc)
    data_point = SolarHistogram.Data(test_time, 1000.5)
    
    # Verify properties are read-only
    with pytest.raises(AttributeError):
        data_point.ts = datetime.now()
    with pytest.raises(AttributeError):
        data_point.power = 2000.0