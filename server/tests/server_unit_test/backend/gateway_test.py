import pytest
from unittest.mock import Mock, patch
from server.backend.gateway import Gateway
from server.backend.der import DER
from server.backend.connection import Connection

@pytest.fixture
def gateway():
    return Gateway("TEST123")

@pytest.fixture
def mock_connection():
    connection = Mock(spec=Connection)
    connection.post.return_value = {
        "data": {
            "gateway": {
                "gateway": {
                    "ders": [
                        {"sn": "SOLAR001", "type": "solar"},
                        {"sn": "SOLAR002", "type": "Solar"}
                    ]
                }
            }
        }
    }
    return connection

def test_str_2_type_solar_lowercase():
    assert Gateway.str_2_type("solar") == DER.Type.SOLAR

def test_str_2_type_solar_capitalized():
    assert Gateway.str_2_type("Solar") == DER.Type.SOLAR

def test_str_2_type_invalid():
    with pytest.raises(ValueError, match="Invalid DER type: invalid"):
        Gateway.str_2_type("invalid")

def test_dict_2_ders():
    test_data = [
        {"sn": "SOLAR001", "type": "solar"},
        {"sn": "SOLAR002", "type": "Solar"}
    ]
    
    ders = Gateway.dict_2_ders(test_data)
    
    assert len(ders) == 2
    assert isinstance(ders[0], DER)
    assert ders[0].serial == "SOLAR001"
    assert ders[0].type == DER.Type.SOLAR
    assert ders[1].serial == "SOLAR002"
    assert ders[1].type == DER.Type.SOLAR

def test_get_ders_query():
    query = Gateway._get_ders_query("TEST123")
    
    # Verify query structure
    assert "gateway" in query
    assert 'id:"TEST123"' in query
    assert "ders" in query
    assert "sn" in query
    assert "type" in query

def test_get_ders(gateway, mock_connection):
    ders = gateway.get_ders(mock_connection)
    
    # Verify connection was called with correct query
    mock_connection.post.assert_called_once()
    query = mock_connection.post.call_args[0][0]
    assert 'id:"TEST123"' in query
    
    # Verify returned DERs
    assert len(ders) == 2
    assert isinstance(ders[0], DER)
    assert ders[0].serial == "SOLAR001"
    assert ders[0].type == DER.Type.SOLAR
    assert ders[1].serial == "SOLAR002"
    assert ders[1].type == DER.Type.SOLAR

def test_get_ders_empty_response(gateway):
    # Setup mock connection with empty response
    connection = Mock(spec=Connection)
    connection.post.return_value = {
        "data": {
            "gateway": {
                "gateway": {
                    "ders": []
                }
            }
        }
    }
    
    ders = gateway.get_ders(connection)
    
    assert len(ders) == 0

def test_get_ders_invalid_response(gateway):
    # Setup mock connection with invalid response
    connection = Mock(spec=Connection)
    connection.post.return_value = {"data": {"gateway": {"gateway": {"ders": [
        {"sn": "SOLAR001", "type": "invalid"}
    ]}}}}
    
    with pytest.raises(ValueError, match="Invalid DER type: invalid"):
        gateway.get_ders(connection)