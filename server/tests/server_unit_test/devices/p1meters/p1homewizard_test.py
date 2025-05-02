from unittest.mock import MagicMock, patch, PropertyMock
import pytest
from requests import HTTPError, Response, Timeout
from server.devices.p1meters.P1HomeWizard import P1HomeWizard


@pytest.fixture
def mock_response():
    response = MagicMock(spec=Response)
    type(response).text = PropertyMock(return_value=get_p1_data())
    response.raise_for_status.return_value = None
    return response


@pytest.fixture
def mock_response_404():
    response = MagicMock(spec=Response)
    response.text.return_value = None
    response.raise_for_status.side_effect = HTTPError("404")
    return response


def test_connect_new_device(mock_response):
    """Test connecting to a new device (no serial number specified)"""
    p1_meter = P1HomeWizard("192.168.0.30", 80)

    # Note the corrected patch path
    with patch('server.devices.p1meters.P1HomeWizard.requests.get', return_value=mock_response) as mock_get:
        assert p1_meter.connect()
        assert p1_meter.meter_serial_number == "LGF5E360"
        mock_get.assert_called_once_with("http://192.168.0.30:80/api/v1/telegram", timeout=5)


def test_get_harvest_data(mock_response):
    p1_meter = P1HomeWizard("192.168.0.30", 80)
    with patch('server.devices.p1meters.P1HomeWizard.requests.get', return_value=mock_response) as mock_get:
        assert p1_meter.connect()
        harvest = p1_meter.read_harvest_data(False)
        assert harvest['serial_number'] == "LGF5E360"
        assert len(harvest['rows']) == 28


def test_is_open(mock_response):
    p1_meter = P1HomeWizard("192.168.0.30", 80)
    with patch('server.devices.p1meters.P1HomeWizard.requests.get', return_value=mock_response) as mock_get:
        assert p1_meter.connect()
        assert p1_meter.is_open()


def test_connect_timeout():
    """Test connecting when request times out"""
    p1_meter = P1HomeWizard("192.168.0.30", 80)

    with patch('server.devices.p1meters.P1HomeWizard.requests.get', side_effect=Timeout()) as mock_get:
        assert not p1_meter.connect()
        mock_get.assert_called_once_with("http://192.168.0.30:80/api/v1/telegram", timeout=5)


def test_is_open_fail(mock_response_404):
    p1_meter = P1HomeWizard("192.168.0.30", 80)
    with patch('server.devices.p1meters.P1HomeWizard.requests.get', return_value=mock_response_404) as mock_get:
        assert not p1_meter.connect()
        assert not p1_meter.is_open()


def test_parse_p1_message():
    p1_data = get_p1_data()
    p1_meter = P1HomeWizard("192.168.0.30", 80)
    result = p1_meter._parse_p1_message(p1_data)
    assert result['serial_number'] == 'LGF5E360'
    assert len(result['rows']) == 28
    assert result['checksum'] == 'F588'


def test_is_open_disconnected(mock_response):
    p1_meter = P1HomeWizard("192.168.0.30", 80)

    # Note the corrected patch path
    with patch('server.devices.p1meters.P1HomeWizard.requests.get', return_value=mock_response) as mock_get:
        assert p1_meter.connect()
        assert p1_meter.is_open()
        p1_meter.disconnect()
        assert not p1_meter.is_open()


def test_clone(mock_response):
    p1_meter = P1HomeWizard("192.168.0.30", 80)
    with patch('server.devices.p1meters.P1HomeWizard.requests.get', return_value=mock_response) as mock_get:
        assert p1_meter.connect()
        assert p1_meter.is_open()
        p1_meter_clone = p1_meter.clone()
        assert p1_meter_clone.get_SN() == p1_meter.get_SN()
        assert not p1_meter_clone.is_open()


def get_p1_data():
    # This is the telegram from the HomeWizard P1 meter in hex format to avoid encoding issues
    # esp for the checksum that is sensitive to the actual characters
    return bytes.fromhex(
        "2f4c474635453336300d0a0d0a302d303a312e302e302832353031313230393436353057290d0a312d303a312e382e302830303031303037312e3334322a6b5768290d0a312d303a322e382e302830303030303030302e3030302a6b5768290d0a312d303a332e382e302830303030303030342e3933352a6b56417268290d0a312d303a342e382e302830303030313934392e3933312a6b56417268290d0a312d303a312e372e3028303030302e3239302a6b57290d0a312d303a322e372e3028303030302e3030302a6b57290d0a312d303a332e372e3028303030302e3030302a6b564172290d0a312d303a342e372e3028303030302e3135392a6b564172290d0a312d303a32312e372e3028303030302e3035382a6b57290d0a312d303a32322e372e3028303030302e3030302a6b57290d0a312d303a34312e372e3028303030302e3232342a6b57290d0a312d303a34322e372e3028303030302e3030302a6b57290d0a312d303a36312e372e3028303030302e3030362a6b57290d0a312d303a36322e372e3028303030302e3030302a6b57290d0a312d303a32332e372e3028303030302e3030302a6b564172290d0a312d303a32342e372e3028303030302e3033392a6b564172290d0a312d303a34332e372e3028303030302e3030302a6b564172290d0a312d303a34342e372e3028303030302e3130342a6b564172290d0a312d303a36332e372e3028303030302e3030302a6b564172290d0a312d303a36342e372e3028303030302e3031352a6b564172290d0a312d303a33322e372e30283233342e302a56290d0a312d303a35322e372e30283233312e392a56290d0a312d303a37322e372e30283233322e372a56290d0a312d303a33312e372e30283030302e332a41290d0a312d303a35312e372e30283030312e302a41290d0a312d303a37312e372e30283030302e302a41290d0a21463538380d0a"
    ).decode("ascii")
