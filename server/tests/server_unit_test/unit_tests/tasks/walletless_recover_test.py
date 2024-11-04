from unittest.mock import Mock, patch
from server.tasks.walletlessRecoverTask import WalletlessRecoverTask
import server.crypto.crypto as crypto

import requests

## these currently make the actuall calls to the api


def test_executeTask():
    t = WalletlessRecoverTask(0, {}, "aaa", "bbb")
    assert t.prv == ""
    assert t.pub == ""

    t._json = Mock(return_value=t._build_mutation("aaa", "bbb", "ccc"))
    t.execute(0)
    assert t._json.called

def test_on_200():
    t = WalletlessRecoverTask(0, {}, "aaa", "bbb")

    response = Mock()
    response.json.return_value = example_return_data()

    t._on_200(response)
    assert t.prv == "ccc"
    assert t.pub == "ddd"


def test_make_the_call_with_task():

    with patch("server.crypto.crypto.HardwareCrypto.atcab_init", return_value=crypto.ATCA_SUCCESS):
        with patch("server.crypto.crypto.HardwareCrypto.atcab_get_pubkey", return_value=(crypto.ATCA_SUCCESS, b'123456789012')):
            with patch("server.crypto.crypto.HardwareCrypto.atcab_sign", return_value=(crypto.ATCA_SUCCESS, b'123456789012')):
                with patch("server.crypto.crypto.HardwareCrypto.atcab_get_pubkey", return_value=(crypto.ATCA_SUCCESS, b'123456789012')):
                  t = WalletlessRecoverTask(0, {}, "aaa", "bbb")
                  assert t.execute(0) == None

    # this should fail
    assert t.reply.status_code == 400


def example_return_data():
    return {"data": {"walletlessSigning": {"recover": {"privateKey": "ccc", "publicKey": "ddd"}}}}
