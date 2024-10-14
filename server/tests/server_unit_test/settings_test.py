import pytest
import json
from server.settings import Settings, ChangeSource
from server.inverters.ModbusTCP import ModbusTCP


@pytest.fixture
def settings():
    return Settings()

@pytest.fixture
def com():
    return ModbusTCP(("192.168.1.1", "00:00:00:00:00:00", 502, "solaredge", 17))

@pytest.fixture
def com2():
    return ModbusTCP(("192.168.1.1", "00:00:00:00:00:00", 502, "solaredge", 17))

def test_constants(settings):
    assert settings.SETTINGS == "settings"
    assert settings.harvest.HARVEST == "harvest"
    assert settings.harvest.ENDPOINTS == "endpoints"

    assert settings.devices.DEVICES == "devices"
    assert settings.devices.CONNECTIONS == "connections"

def test_devices_add_connection(settings, com):

    expected_connection = com.get_config()

    settings.devices.add_connection(com, ChangeSource.LOCAL)
    assert len(settings.devices.connections) == 1
    assert settings.devices.connections[0]["host"] == "192.168.1.1"
    assert settings.devices.to_dict()[settings.devices.CONNECTIONS][0] == expected_connection

def test_add_duplicate_device_but_different_casing(settings, com, com2):
    settings.devices.add_connection(com, ChangeSource.LOCAL)
    settings.devices.add_connection(com2, ChangeSource.LOCAL)
    assert len(settings.devices.connections) == 1
    assert settings.devices.connections[0]["type"] == "solaredge"

def test_devices_listener(settings, com):
    called = False
    def listener(source):
        nonlocal called
        called = True
        assert source == ChangeSource.LOCAL
    
    settings.devices.add_listener(listener)

    settings.devices.add_connection(com, ChangeSource.LOCAL)
    assert called

def test_devices_remove_listener(settings, com):
    called = False
    def listener(source):
        nonlocal called
        called = True
        assert source == ChangeSource.LOCAL
    
    settings.devices.add_connection(com, ChangeSource.LOCAL)
    settings.devices.add_listener(listener)
    settings.devices.remove_connection(com, ChangeSource.LOCAL)
    
    assert called

def test_same_device_twice(settings, com):
    settings.devices.add_connection(com, ChangeSource.LOCAL)
    settings.devices.add_connection(com, ChangeSource.LOCAL)
    assert len(settings.devices.connections) == 1

def test_harvest_add_endpoint(settings):
    settings.harvest.add_endpoint("https://example.com", ChangeSource.LOCAL)
    assert "https://example.com" in settings.harvest.endpoints

def test_harvest_remove_endpoint(settings):
    settings.harvest.add_endpoint("https://example.com", ChangeSource.LOCAL)
    settings.harvest.remove_endpoint("https://example.com", ChangeSource.LOCAL)
    assert "https://example.com" not in settings.harvest.endpoints

def test_harvest_clear_endpoints(settings):
    settings.harvest.add_endpoint("https://example.com", ChangeSource.LOCAL)
    settings.harvest.add_endpoint("https://test.com", ChangeSource.LOCAL)
    settings.harvest.clear_endpoints(ChangeSource.LOCAL)
    assert len(settings.harvest.endpoints) == 0

def test_harvest_endpoints_property(settings):
    settings.harvest.add_endpoint("https://example.com", ChangeSource.LOCAL)
    endpoints = settings.harvest.endpoints
    endpoints.append("https://test.com")
    assert "https://test.com" not in settings.harvest.endpoints

def test_to_json(settings):
    settings.harvest.add_endpoint("https://example.com", ChangeSource.LOCAL)
    settings.harvest.add_endpoint("https://test.com", ChangeSource.LOCAL)
    json_str = settings.to_json()
    expected = {
        settings.SETTINGS: {
            settings.harvest.HARVEST: {
                settings.harvest.ENDPOINTS: [
                    "https://example.com",
                    "https://test.com"
                ]
            },
            settings.devices.DEVICES: {
                settings.devices.CONNECTIONS: []
            }
        }
    }
    assert json.loads(json_str) == expected

def test_from_json(settings):
    json_str = json.dumps({
        settings.SETTINGS: {
            settings.harvest.HARVEST: {
                settings.harvest.ENDPOINTS: [
                    "https://example.com",
                    "https://test.com"
                ]
            }
        }
    })
    settings.from_json(json_str, ChangeSource.BACKEND)
    assert settings.harvest.endpoints == ["https://example.com", "https://test.com"]

def test_from_json_clears_existing_endpoints(settings):
    settings.harvest.add_endpoint("https://old.com", ChangeSource.LOCAL)
    json_str = json.dumps({
        settings.SETTINGS: {
            settings.harvest.HARVEST: {
                settings.harvest.ENDPOINTS: [
                    "https://new.com"
                ]
            }
        }
    })
    settings.from_json(json_str, ChangeSource.BACKEND)
    assert settings.harvest.endpoints == ["https://new.com"]

def test_constants_immutability(settings):
    with pytest.raises(AttributeError):
        settings.SETTINGS = "new_value"

def test_invalid_json():
    settings = Settings()
    with pytest.raises(json.JSONDecodeError):
        settings.from_json("invalid json", ChangeSource.BACKEND)

def test_add_listener(settings:Settings):
    called = False
    def listener(source):
        nonlocal called
        called = True
        assert source == ChangeSource.LOCAL
    
    settings.harvest.add_listener(listener)
    settings.harvest.add_endpoint("https://example.com", ChangeSource.LOCAL)
    assert called

def test_remove_listener(settings:Settings):
    called = False
    def listener(source):
        nonlocal called
        called = True
    
    settings.harvest.add_listener(listener)
    settings.harvest.remove_listener(listener)
    settings.harvest.add_endpoint("https://example.com", ChangeSource.LOCAL)
    assert not called

def test_multiple_listeners(settings:Settings):
    call_count = 0
    def listener1(source):
        nonlocal call_count
        call_count += 1
        assert source == ChangeSource.LOCAL
    def listener2(source):
        nonlocal call_count
        call_count += 1
        assert source == ChangeSource.LOCAL
    
    settings.harvest.add_listener(listener1)
    settings.harvest.add_listener(listener2)
    settings.harvest.add_endpoint("https://example.com", ChangeSource.LOCAL)
    assert call_count == 2

def test_sub_listener_notified(settings:Settings):
    called = False
    def listener(source):
        nonlocal called
        called = True
        assert source == ChangeSource.LOCAL
    
    settings.devices.add_listener(listener)
    settings.update_from_dict({
        settings.SETTINGS: {
            settings.devices.DEVICES: {
                settings.devices.CONNECTIONS: [
                    ("TCP", "192.168.1.1", 502, "solaredge", 17)
                ]
            }
        }
    }, ChangeSource.LOCAL)  

    assert called
    

def test_harvest_notifies_settings(settings:Settings):
    called = False
    def listener(source):
        nonlocal called
        called = True
        assert source == ChangeSource.LOCAL
    
    settings.harvest.add_listener(listener)
    settings.harvest.add_endpoint("https://example.com", ChangeSource.LOCAL)
    assert called

def test_subscribe_all(settings:Settings):
    call_count = 0
    def listener(source):
        nonlocal call_count
        call_count += 1
        assert source == ChangeSource.LOCAL
    
    settings.subscribe_all(listener)
    settings.harvest.add_endpoint("https://example.com", ChangeSource.LOCAL)
    assert call_count == 2  # Once for Harvest, once for Settings

def test_from_json_notifies_listeners(settings:Settings):
    called = False
    def listener(source):
        nonlocal called
        called = True
        assert source == ChangeSource.BACKEND
    
    settings.add_listener(listener)
    json_str = json.dumps({
        settings.SETTINGS: {
            settings.harvest.HARVEST: {
                settings.harvest.ENDPOINTS: [
                    "https://example.com"
                ]
            }
        }
    })
    settings.from_json(json_str, ChangeSource.BACKEND)
    assert called

def test_listener_not_called_on_no_change(settings:Settings):
    call_count = 0
    def listener(source):
        nonlocal call_count
        call_count += 1
    
    settings.subscribe_all(listener)
    settings.harvest.add_endpoint("https://example.com", ChangeSource.LOCAL)
    call_count = 0  # Reset count
    settings.harvest.add_endpoint("https://example.com", ChangeSource.LOCAL)  # Adding same endpoint
    assert call_count == 0  # Listener should not be called as there's no actual change

def test_listener_called_on_remove(settings:Settings):
    called = False
    def listener(source):
        nonlocal called
        called = True
        assert source == ChangeSource.LOCAL
    
    settings.subscribe_all(listener)
    settings.harvest.add_endpoint("https://example.com", ChangeSource.LOCAL)
    called = False  # Reset flag
    settings.harvest.remove_endpoint("https://example.com", ChangeSource.LOCAL)
    assert called

def test_listener_called_on_clear(settings:Settings):
    called = False
    def listener(source):
        nonlocal called
        called = True
        assert source == ChangeSource.LOCAL
    
    settings.subscribe_all(listener)
    settings.harvest.add_endpoint("https://example.com", ChangeSource.LOCAL)
    called = False  # Reset flag
    settings.harvest.clear_endpoints(ChangeSource.LOCAL)
    assert called

def test_update_from_backend(settings:Settings, com):
    called = False
    def listener(source):
        nonlocal called
        called = True
        assert source == ChangeSource.BACKEND
    
    settings.add_listener(listener)
    settings.update_from_dict({
        settings.SETTINGS: {
            settings.harvest.HARVEST: {
                settings.harvest.ENDPOINTS: [
                    "https://backend.com"
                ]
            },
            settings.devices.DEVICES: {
                settings.devices.CONNECTIONS: [
                    com.get_config()
                ]
            }
        }
    }, ChangeSource.BACKEND)
    assert called
    assert settings.harvest.endpoints == ["https://backend.com"]
    assert settings.devices.connections == [com.get_config()]