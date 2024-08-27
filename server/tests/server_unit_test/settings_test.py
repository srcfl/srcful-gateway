import pytest
import json
from server.settings import Settings  # Replace 'your_module' with the actual module name

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