from server.crypto.crypto_state import CryptoState
from server.web.socket.settings_subscription import GraphQLSubscriptionClient
import pytest
from server.app.blackboard import BlackBoard
from unittest.mock import Mock, patch
import server.crypto.crypto as crypto
from server.app.settings import ChangeSource

@pytest.fixture
def blackboard():
    return BlackBoard(Mock(spec=CryptoState))

def test_get_settings_with_chip(blackboard):
    client = GraphQLSubscriptionClient(blackboard, "ws://example.com")

    # here we manually patch so we can use the normal chip class
    with patch("server.crypto.crypto.HardwareCrypto.atcab_init", return_value=crypto.ATCA_SUCCESS):
        with patch("server.crypto.crypto.HardwareCrypto.atcab_read_serial_number", return_value=(crypto.ATCA_SUCCESS, b'123456789012')):
            with patch("server.crypto.crypto.HardwareCrypto.atcab_sign", return_value=(crypto.ATCA_SUCCESS, b'123456789012')):
                    ret = client._get_subscription_query(crypto.Chip)

    assert len(ret) > 0

def test_get_settings_with_mock_chip(blackboard):
    # patched chip is needed so the mock chip can be used as this is what actually patches the crypto functions
    client = GraphQLSubscriptionClient(blackboard, "ws://example.com")

    def create_chip():
         return crypto.Chip(crypto_impl=crypto.SoftwareCrypto())

    ret = client._get_subscription_query(create_chip)

    with create_chip() as chip:
        assert chip.get_serial_number().hex() in ret

    assert True

def test_on_message(blackboard):
    client = GraphQLSubscriptionClient(blackboard, "ws://example.com")
    blackboard.settings.harvest.clear_endpoints(ChangeSource.BACKEND)

    client.on_message(None, '{"type":"data","id":"1","payload":{"data":{"configurationDataChanges":{"data":"{\\u0022settings\\u0022: {\\u0022harvest\\u0022: {\\u0022endpoints\\u0022: [\\u0022https://mainnet.srcful.dev/gw/data/\\u0022]}}}","subKey":"settings"}}}}')
    assert blackboard.settings.harvest.endpoints == ['https://mainnet.srcful.dev/gw/data/']

def test_on_message_empty_message():
    client = GraphQLSubscriptionClient(blackboard, "ws://example.com")
    client.on_message(None, '')
    assert True

def test_on_message_none_message():
    client = GraphQLSubscriptionClient(blackboard, "ws://example.com")
    client.on_message(None, None)
    assert True