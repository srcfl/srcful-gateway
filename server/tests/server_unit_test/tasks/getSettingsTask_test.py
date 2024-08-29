import pytest

from server.tasks.getSettingsTask import GetSettingsTask

from unittest.mock import Mock, patch

from server.tasks.saveSettingsTask import SaveSettingsTask

from server.blackboard import BlackBoard
from server.settings import Settings, ChangeSource

import server.crypto.crypto as crypto

from server.tests.server_unit_test.crypto.mockChip import patched_chip, mock_crypto_chip


@pytest.fixture
def blackboard():
    return BlackBoard()

def test_make_the_call_with_task(blackboard):
    with patch("server.crypto.crypto.atcab_init", return_value=crypto.ATCA_SUCCESS):
        with patch("server.crypto.crypto.atcab_read_serial_number", return_value=crypto.ATCA_SUCCESS):
            with patch("server.crypto.crypto.atcab_sign", return_value=crypto.ATCA_SUCCESS):
                with patch("server.crypto.crypto.atcab_get_pubkey", return_value=crypto.ATCA_SUCCESS):
                  t = GetSettingsTask(0, blackboard)
                  ret = t.execute(0)

    assert t.reply.status_code == 200
    assert "errors" in t.reply.json()
    assert isinstance(ret, SaveSettingsTask)

def test_get_settings_with_mock_chip(blackboard, patched_chip):
    with patch('server.crypto.crypto.Chip.__new__', return_value=patched_chip):
        t = GetSettingsTask(0, blackboard)
        t.execute(0)

    assert t.reply.status_code == 200
    assert "errors" not in t.reply.json()


def test_handle_settings_with_none(blackboard):
    t = GetSettingsTask(0, blackboard)
    ret = t._handle_settings({'data': {'gatewayConfiguration': {'configuration': {'data': None}}}})
    assert isinstance(ret, SaveSettingsTask)

def test_handle_settings_with_wrong_format(blackboard):
    t = GetSettingsTask(0, blackboard)
    ret = t._handle_settings({"data": {"bork": {"bork": {"bork": None}}}})
    assert ret is None

def test_handle_settings_settings_are_updated(blackboard):
    new_settings = Settings()

    new_settings.harvest.add_endpoint("https://test.com", ChangeSource.BACKEND)

    t = GetSettingsTask(0, blackboard)
    ret = t._handle_settings({"data": {"gatewayConfiguration": {"configuration": {"data": new_settings.to_dict()}}}})
    assert ret is None

    assert blackboard.settings.harvest.endpoints == new_settings.harvest.endpoints