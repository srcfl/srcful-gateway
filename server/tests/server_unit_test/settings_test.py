import pytest
import json
from server.settings import Settings

@pytest.fixture
def settings():
    return Settings()

def test_constants(settings):
    assert settings.SETTINGS == "settings"
    assert settings.harvest.HARVEST == "harvest"
    assert settings.harvest.ENDPOINTS == "endpoints"

def test_harvest_add_endpoint(settings):
    settings.harvest.add_endpoint("https://example.com")
    assert "https://example.com" in settings.harvest.endpoints

def test_harvest_remove_endpoint(settings):
    settings.harvest.add_endpoint("https://example.com")
    settings.harvest.remove_endpoint("https://example.com")
    assert "https://example.com" not in settings.harvest.endpoints

def test_harvest_clear_endpoints(settings):
    settings.harvest.add_endpoint("https://example.com")
    settings.harvest.add_endpoint("https://test.com")
    settings.harvest.clear_endpoints()
    assert len(settings.harvest.endpoints) == 0

def test_harvest_endpoints_property(settings):
    settings.harvest.add_endpoint("https://example.com")
    endpoints = settings.harvest.endpoints
    endpoints.append("https://test.com")
    assert "https://test.com" not in settings.harvest.endpoints

def test_to_json(settings):
    settings.harvest.add_endpoint("https://example.com")
    settings.harvest.add_endpoint("https://test.com")
    json_str = settings.to_json()
    expected = {
        settings.SETTINGS: {
            settings.harvest.HARVEST: {
                settings.harvest.ENDPOINTS: [
                    "https://example.com",
                    "https://test.com"
                ]
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
    settings.from_json(json_str)
    assert settings.harvest.endpoints == ["https://example.com", "https://test.com"]

def test_from_json_clears_existing_endpoints(settings):
    settings.harvest.add_endpoint("https://old.com")
    json_str = json.dumps({
        settings.SETTINGS: {
            settings.harvest.HARVEST: {
                settings.harvest.ENDPOINTS: [
                    "https://new.com"
                ]
            }
        }
    })
    settings.from_json(json_str)
    assert settings.harvest.endpoints == ["https://new.com"]

def test_constants_immutability(settings):
    with pytest.raises(AttributeError):
        settings.SETTINGS = "new_value"

def test_invalid_json():
    settings = Settings()
    with pytest.raises(json.JSONDecodeError):
        settings.from_json("invalid json")

def test_missing_keys_in_json(settings):
    settings = Settings()
    with pytest.raises(KeyError):
        settings.from_json(json.dumps({settings.SETTINGS: {}}))

def test_add_listener(settings):
    called = False
    def listener():
        nonlocal called
        called = True
    
    settings.add_listener(listener)
    settings.harvest.add_endpoint("https://example.com")
    assert called

def test_remove_listener(settings):
    called = False
    def listener():
        nonlocal called
        called = True
    
    settings.add_listener(listener)
    settings.remove_listener(listener)
    settings.harvest.add_endpoint("https://example.com")
    assert not called

def test_multiple_listeners(settings):
    call_count = 0
    def listener1():
        nonlocal call_count
        call_count += 1
    def listener2():
        nonlocal call_count
        call_count += 1
    
    settings.add_listener(listener1)
    settings.add_listener(listener2)
    settings.harvest.add_endpoint("https://example.com")
    assert call_count == 2

def test_harvest_notifies_settings(settings):
    called = False
    def listener():
        nonlocal called
        called = True
    
    settings.add_listener(listener)
    settings.harvest.add_endpoint("https://example.com")
    assert called

def test_subscribe_all(settings):
    call_count = 0
    def listener():
        nonlocal call_count
        call_count += 1
    
    settings.subscribe_all(listener)
    settings.harvest.add_endpoint("https://example.com")
    assert call_count == 2  # Once for Harvest, once for Settings

def test_from_json_notifies_listeners(settings):
    called = False
    def listener():
        nonlocal called
        called = True
    
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
    settings.from_json(json_str)
    assert called

def test_listener_not_called_on_no_change(settings):
    call_count = 0
    def listener():
        nonlocal call_count
        call_count += 1
    
    settings.subscribe_all(listener)
    settings.harvest.add_endpoint("https://example.com")
    call_count = 0  # Reset count
    settings.harvest.add_endpoint("https://example.com")  # Adding same endpoint
    assert call_count == 0  # Listener should not be called as there's no actual change

def test_listener_called_on_remove(settings):
    called = False
    def listener():
        nonlocal called
        called = True
    
    settings.subscribe_all(listener)
    settings.harvest.add_endpoint("https://example.com")
    called = False  # Reset flag
    settings.harvest.remove_endpoint("https://example.com")
    assert called

def test_listener_called_on_clear(settings):
    called = False
    def listener():
        nonlocal called
        called = True
    
    settings.subscribe_all(listener)
    settings.harvest.add_endpoint("https://example.com")
    called = False  # Reset flag
    settings.harvest.clear_endpoints()
    assert called