from server.web.socket.settings_subscription import GraphQLSubscriptionClient
from server.tests.server_unit_test.crypto.mockChip import patched_chip, mock_crypto_chip, MockCryptoChip
import pytest
from server.blackboard import BlackBoard
from unittest.mock import patch
import server.crypto.crypto as crypto

@pytest.fixture
def blackboard():
    return BlackBoard()

def test_get_settings_with_chip(blackboard):
    client = GraphQLSubscriptionClient(blackboard, "ws://example.com")

    # here we manually patch so we can use the normal chip class
    with patch("server.crypto.crypto.atcab_init", return_value=crypto.ATCA_SUCCESS):
        with patch("server.crypto.crypto.atcab_read_serial_number", return_value=crypto.ATCA_SUCCESS):
            with patch("server.crypto.crypto.atcab_sign", return_value=crypto.ATCA_SUCCESS):
                    ret = client._get_subscription_query(crypto.Chip)

    assert len(ret) > 0

def test_get_settings_with_mock_chip(blackboard, patched_chip):
    # patched chip is needed so the mock chip can be used as this is what actually patches the crypto functions
    client = GraphQLSubscriptionClient(blackboard, "ws://example.com")

    ret = client._get_subscription_query(MockCryptoChip)

    with MockCryptoChip() as chip:
        assert chip.serial_number.hex() in ret

    assert True