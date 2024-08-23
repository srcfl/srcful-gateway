import pytest
import json
import time
from server.settings import Settings, DebouncedMonitorBase
from unittest.mock import Mock, patch


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

class TestMonitor(DebouncedMonitorBase):
    def __init__(self, debounce_delay: float = 0.1):
        super().__init__(debounce_delay)
        self.action_performed = False

    def _perform_action(self):
        self.action_performed = True

@pytest.fixture
def test_monitor():
    return TestMonitor()

def test_debounce_action_called(test_monitor):
    test_monitor.on_change()
    time.sleep(0.2)  # Wait for debounce timer to expire
    assert test_monitor.action_performed

def test_debounce_action_not_called_immediately(test_monitor):
    test_monitor.on_change()
    assert not test_monitor.action_performed

def test_multiple_changes_result_in_single_action(test_monitor):
    for _ in range(5):
        test_monitor.on_change()
        time.sleep(0.05)  # Wait less than debounce delay between changes
    
    time.sleep(0.2)  # Wait for debounce timer to expire
    assert test_monitor.action_performed
    
    # Reset and wait to ensure no more actions are performed
    test_monitor.action_performed = False
    time.sleep(0.2)
    assert not test_monitor.action_performed

def test_changes_after_action_trigger_new_action(test_monitor):
    test_monitor.on_change()
    time.sleep(0.2)  # Wait for first action to be performed
    assert test_monitor.action_performed

    test_monitor.action_performed = False
    test_monitor.on_change()
    time.sleep(0.2)  # Wait for second action to be performed
    assert test_monitor.action_performed

@pytest.mark.parametrize("debounce_delay", [0.1, 0.5, 1.0])
def test_custom_debounce_delay(debounce_delay):
    monitor = TestMonitor(debounce_delay)
    monitor.on_change()
    time.sleep(debounce_delay - 0.05)  # Wait slightly less than debounce delay
    assert not monitor.action_performed
    time.sleep(0.1)  # Wait a bit more to exceed debounce delay
    assert monitor.action_performed

def test_concurrent_changes(test_monitor):
    with patch('threading.Timer') as mock_timer:
        for _ in range(10):
            test_monitor.on_change()
        
        # Check that Timer was called 10 times
        assert mock_timer.call_count == 10
        
        # Check that cancel was called 9 times (not called for the first timer)
        assert sum(1 for call in mock_timer.mock_calls if call[0] == '().cancel') == 9


def test_abstract_method_not_implemented():
    with pytest.raises(TypeError, match="Can't instantiate abstract class"):
        DebouncedMonitorBase()