from unittest.mock import MagicMock, patch
import pytest
from requests import HTTPError, Response, Timeout
from server.devices.p1meters.P1Jemac import P1Jemac


@pytest.fixture
def mock_response():
    response = MagicMock(spec=Response)
    response.json.return_value = get_p1_data()
    response.raise_for_status.return_value = None
    return response

@pytest.fixture
def mock_response_404():
    response = MagicMock(spec=Response)
    response.json.return_value = None
    response.raise_for_status.side_effect = HTTPError("404")
    return response

def test_connect_new_device(mock_response):
    """Test connecting to a new device (no serial number specified)"""
    p1_meter = P1Jemac("192.168.0.30", 80)
    
    # Note the corrected patch path
    with patch('server.devices.p1meters.P1Jemac.requests.get', return_value=mock_response) as mock_get:
        assert p1_meter.connect()
        assert p1_meter.meter_serial_number == "/LGF5E360"
        mock_get.assert_called_once_with("http://192.168.0.30:80/telegram.json")

def test_get_harvest_data(mock_response):
    p1_meter = P1Jemac("192.168.0.30", 80)
    with patch('server.devices.p1meters.P1Jemac.requests.get', return_value=mock_response) as mock_get:
        assert p1_meter.connect()
        harvest = p1_meter.read_harvest_data(False)
        assert harvest['serial_number'] == "/LGF5E360"
        assert len(harvest['rows']) == 28

def test_is_open(mock_response):
    p1_meter = P1Jemac("192.168.0.30", 80)
    with patch('server.devices.p1meters.P1Jemac.requests.get', return_value=mock_response) as mock_get:
        assert p1_meter.connect()
        assert p1_meter.is_open()

def test_connect_timeout():
    """Test connecting when request times out"""
    p1_meter = P1Jemac("192.168.0.30", 80)
    
    with patch('server.devices.p1meters.P1Jemac.requests.get', side_effect=Timeout()) as mock_get:
        assert not p1_meter.connect()
        mock_get.assert_called_once_with("http://192.168.0.30:80/telegram.json", timeout=5)

def test_is_open_fail(mock_response_404):
    p1_meter = P1Jemac("192.168.0.30", 80)
    with patch('server.devices.p1meters.P1Jemac.requests.get', return_value=mock_response_404) as mock_get:
        assert not p1_meter.connect()
        assert not p1_meter.is_open()

def test_parse_p1_message():
    p1_data = get_p1_data()
    p1_meter = P1Jemac(p1_data)
    result = p1_meter._parse_p1_message(p1_data)
    assert result['serial_number'] == '/LGF5E360'
    assert len(result['rows']) == 28


def get_p1_data():
    return {
        "id": "D43D39819C59",
        "rssi": -26,
        "fw": "FRTOS-JEMAC-01-2aa77df370-200020",
        "data": [
            "/LGF5E360",
            "0-0:1.0.0(230109214510W)",
            "1-0:1.8.0(00000000.003*kWh)",
            "1-0:2.8.0(00000000.000*kWh)",
            "1-0:3.8.0(00000000.001*kVArh)",
            "1-0:4.8.0(00000000.000*kVArh)",
            "1-0:1.7.0(0000.000*kW)",
            "1-0:2.7.0(0000.000*kW)",
            "1-0:3.7.0(0000.000*kVAr)",
            "1-0:4.7.0(0000.000*kVAr)",
            "1-0:21.7.0(0000.000*kW)",
            "1-0:22.7.0(0000.000*kW)",
            "1-0:41.7.0(0000.000*kW)",
            "1-0:42.7.0(0000.000*kW)",
            "1-0:61.7.0(0000.000*kW)",
            "1-0:62.7.0(0000.000*kW)",
            "1-0:23.7.0(0000.000*kVAr)",
            "1-0:24.7.0(0000.000*kVAr)",
            "1-0:43.7.0(0000.000*kVAr)",
            "1-0:44.7.0(0000.000*kVAr)",
            "1-0:63.7.0(0000.000*kVAr)",
            "1-0:64.7.0(0000.000*kVAr)",
            "1-0:32.7.0(000.0*V)",
            "1-0:52.7.0(000.0*V)",
            "1-0:72.7.0(230.1*V)",
            "1-0:31.7.0(000.0*A)",
            "1-0:51.7.0(000.0*A)",
            "1-0:71.7.0(000.0*A)",
            "!C3BE"
        ]
    }