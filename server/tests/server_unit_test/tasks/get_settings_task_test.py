import pytest

from server.crypto.crypto_state import CryptoState
from server.tasks.getSettingsTask import GetSettingsTask, handle_settings

from unittest.mock import Mock, patch

from server.tasks.saveSettingsTask import SaveSettingsTask

from server.app.blackboard import BlackBoard
from server.app.settings import Settings, ChangeSource

import server.crypto.crypto as crypto



@pytest.fixture
def blackboard():
    return BlackBoard(Mock(spec=CryptoState))

def test_make_the_call_with_task(blackboard):
    with patch("server.crypto.crypto.HardwareCrypto.atcab_init", return_value=crypto.ATCA_SUCCESS):
        with patch("server.crypto.crypto.HardwareCrypto.atcab_read_serial_number", return_value=(crypto.ATCA_SUCCESS, b'123456789012')):
            with patch("server.crypto.crypto.HardwareCrypto.atcab_sign", return_value=(crypto.ATCA_SUCCESS, b'123456789012')):
                with patch("server.crypto.crypto.HardwareCrypto.atcab_get_pubkey", return_value=(crypto.ATCA_SUCCESS, b'123456789012')):
                  t = GetSettingsTask(0, blackboard)
                  ret = t.execute(0)

    assert t.reply.status_code == 200
    assert "errors" in t.reply.json() or "settings" in t.reply.json()["data"]["gatewayConfiguration"]["configuration"]["data"]
    if "errors" in t.reply.json():
        assert isinstance(ret, SaveSettingsTask)
    else:
        assert ret is None

def test_get_settings_with_mock_chip(blackboard):
    with patch('server.crypto.crypto.Chip', return_value=crypto.Chip(crypto_impl=crypto.SoftwareCrypto())):
        t = GetSettingsTask(0, blackboard)
        t.execute(0)

    assert t.reply.status_code == 200
    assert "errors" not in t.reply.json()


def test_handle_settings_with_none(blackboard):
    ret = handle_settings(blackboard, {'data': None})
    assert isinstance(ret, SaveSettingsTask)

def test_handle_settings_with_wrong_format(blackboard):
    ret = handle_settings(blackboard, {"data": {"bork": {"bork": {"bork": None}}}})
    assert ret is None

def test_handle_settings_settings_are_updated(blackboard):
    new_settings = Settings()

    new_settings.harvest.add_endpoint("https://test.com", ChangeSource.BACKEND)

    ret = handle_settings(blackboard, {"data": new_settings.to_json()})
    assert ret is None

    assert blackboard.settings.harvest.endpoints == new_settings.harvest.endpoints