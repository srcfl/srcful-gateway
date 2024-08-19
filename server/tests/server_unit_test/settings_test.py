import pytest
import json
from server.settings import Settings  # Replace 'your_module' with the actual module name


def test_harvest_add_endpoint():
    settings = Settings()
    settings.harvest.add_endpoint("https://example.com")
    assert "https://example.com" in settings.harvest.endpoints

def test_harvest_remove_endpoint():
    settings = Settings()
    settings.harvest.add_endpoint("https://example.com")
    settings.harvest.remove_endpoint("https://example.com")
    assert "https://example.com" not in settings.harvest.endpoints

def test_harvest_clear_endpoints():
    settings = Settings()
    settings.harvest.add_endpoint("https://example.com")
    settings.harvest.add_endpoint("https://test.com")
    settings.harvest.clear_endpoints()
    assert len(settings.harvest.endpoints) == 0

def test_harvest_endpoints_property():
    settings = Settings()
    settings.harvest.add_endpoint("https://example.com")
    endpoints = settings.harvest.endpoints
    endpoints.append("https://test.com")
    assert "https://test.com" not in settings.harvest.endpoints

def test_to_json():
    settings = Settings()
    settings.harvest.add_endpoint("https://example.com")
    settings.harvest.add_endpoint("https://test.com")
    json_str = settings.to_json()
    expected = '''{
    "settings": {
        "harvest": {
            "endpoints": [
                "https://example.com",
                "https://test.com"
            ]
        }
    }
}'''
    assert json_str == expected

def test_from_json():
    settings = Settings()
    json_str = '''{
    "settings": {
        "harvest": {
            "endpoints": [
                "https://example.com",
                "https://test.com"
            ]
        }
    }
}'''
    settings.from_json(json_str)
    assert settings.harvest.endpoints == ["https://example.com", "https://test.com"]

def test_from_json_clears_existing_endpoints():
    settings = Settings()
    settings.harvest.add_endpoint("https://old.com")
    json_str = '''{
    "settings": {
        "harvest": {
            "endpoints": [
                "https://new.com"
            ]
        }
    }
}'''
    settings.from_json(json_str)
    assert settings.harvest.endpoints == ["https://new.com"]

def test_invalid_json():
    settings = Settings()
    with pytest.raises(json.JSONDecodeError):
        settings.from_json("invalid json")

def test_missing_keys_in_json():
    settings = Settings()
    with pytest.raises(KeyError):
        settings.from_json('{"invalid": "structure"}')