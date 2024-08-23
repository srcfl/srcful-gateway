import pytest

from server.tasks.saveSettingsTask import SaveSettingsTask
from unittest.mock import Mock, patch

from server.blackboard import BlackBoard
from server.settings import Settings

import server.crypto.crypto as crypto


@pytest.fixture
def blackboard():
    return BlackBoard()

@pytest.fixture
def settings():
    ret = Settings()
    ret.harvest.add_endpoint("https://example.com")


def test_make_the_call_with_task(blackboard):
    with patch("server.crypto.crypto.atcab_init", return_value=crypto.ATCA_SUCCESS):
        with patch("server.crypto.crypto.atcab_read_serial_number", return_value=crypto.ATCA_SUCCESS):
            with patch("server.crypto.crypto.atcab_sign", return_value=crypto.ATCA_SUCCESS):
                with patch("server.crypto.crypto.atcab_get_pubkey", return_value=crypto.ATCA_SUCCESS):
                  t = SaveSettingsTask(0, blackboard)
                  t.execute(0)

    assert t.reply.status_code == 200
    assert t.is_saved is False