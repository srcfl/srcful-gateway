from unittest.mock import Mock, patch
from server.tasks.initializeTask import InitializeTask
import server.crypto.crypto as crypto

import requests

## these currently make the actuall calls to the api


def test_executeTask():
    t = InitializeTask(0, {}, "aaa")
    assert t.is_initialized == None
    t._json = Mock(return_value=_internalJsonQuery())
    t.execute(0)
    assert t._json.called
    assert t.is_initialized == False


def test_make_the_call_with_task():

    with patch("server.crypto.crypto.HardwareCrypto.atcab_init", return_value=crypto.ATCA_SUCCESS):
        with patch("server.crypto.crypto.HardwareCrypto.atcab_read_serial_number", return_value=(crypto.ATCA_SUCCESS, b'123456789012')):
            with patch("server.crypto.crypto.HardwareCrypto.atcab_sign", return_value=(crypto.ATCA_SUCCESS, b'123456789012')):
                with patch("server.crypto.crypto.HardwareCrypto.atcab_get_pubkey", return_value=(crypto.ATCA_SUCCESS, b'123456789012')):
                  t = InitializeTask(0, {}, "aaa", True)
                  t.execute(0)

    assert t.reply.status_code == 200
    assert t.is_initialized is False


def test_makeTheCall():
    reply = requests.post("https://api.srcful.dev/", json=_internalJsonQuery())
    assert reply.status_code == 200
    assert (
        reply.json()["data"]["gatewayInception"]["initialize"]["initialized"] == False
    )


def _internalJsonQuery():
    # make a GraphQL
    m = """mutation {
      gatewayInception {
        initialize(gatewayInitialization:{idAndWallet:"$var_idAndWallet", signature:"$var_sign", dryRun:true}) {
          initialized
        }
      }
    }"""

    m = m.replace("$var_idAndWallet", "aa:bb:cc")
    m = m.replace("$var_sign", "123456789abcdef")
    return {"query": m}
