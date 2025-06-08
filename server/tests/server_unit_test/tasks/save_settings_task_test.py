import pytest

from server.crypto.crypto_state import CryptoState
from server.tasks.saveSettingsTask import SaveSettingsTask
from unittest.mock import Mock, patch

from server.app.blackboard import BlackBoard
from server.app.settings import Settings, ChangeSource

import server.crypto.crypto as crypto


@pytest.fixture
def blackboard():
    return BlackBoard(Mock(spec=CryptoState))


@pytest.fixture
def settings():
    ret = Settings()
    ret.harvest.add_endpoint("https://example.com")


def test_make_the_call_with_task(blackboard):
    with patch("server.crypto.crypto.HardwareCrypto.atcab_init", return_value=crypto.ATCA_SUCCESS):
        with patch("server.crypto.crypto.HardwareCrypto.atcab_read_serial_number", return_value=(crypto.ATCA_SUCCESS, b'123456789012')):
            with patch("server.crypto.crypto.HardwareCrypto.atcab_sign", return_value=(crypto.ATCA_SUCCESS, b'123456789012')):
                with patch("server.crypto.crypto.HardwareCrypto.atcab_get_pubkey", return_value=(crypto.ATCA_SUCCESS, b'123456789012')):
                    t = SaveSettingsTask(0, blackboard)
                    t.execute(0)

    assert t.reply.status_code == 200


def test_save_settings_with_mock_chip(blackboard):
    # this does not work with the static methods in Chip as they seem to become mocked out for some reason

    with patch('server.crypto.crypto.Chip', return_value=crypto.Chip(crypto_impl=crypto.SoftwareCrypto())):
        blackboard.settings.harvest.add_endpoint("https://example.com", ChangeSource.LOCAL)
        t = SaveSettingsTask(0, blackboard)
        t.execute(0)

    assert t.reply.status_code == 200
    assert "errors" not in t.reply.json()


def test_pem():
    import base64
    pk = bytes.fromhex("2f5d41eacf701c18eb1bdae549ee0232ed2b9f3dd2b983ff7b68240bbba84f7b4903d0a52a1ab3d47e7155c5f3455fdbe7997bf85b2258fee6644e16b7e8e9be")
    der = bytearray.fromhex("3059301306072A8648CE3D020106082A8648CE3D03010703420004")
    public_key_b64 = base64.b64encode(der + pk).decode("ascii")

    print(public_key_b64)
