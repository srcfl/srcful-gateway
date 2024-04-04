from unittest.mock import Mock, patch
from server.tasks.initializeTask import InitializeTask

import requests

## these currently make the actuall calls to the api


def test_executeTask():
    t = InitializeTask(0, {}, "aaa")
    assert t.is_initialized == None
    t._json = Mock(return_value=_internalJsonQuery())
    t.execute(0)
    t.t.join()
    t.execute(0)
    assert t._json.called
    assert t.is_initialized == False


def test_make_the_call_with_task():
    t = InitializeTask(0, {}, "aaa", True)

    t.execute_and_wait()

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

    m = m.replace("$var_idAndWallet", "aa:bb")
    m = m.replace("$var_sign", "123456789abcdef")
    return {"query": m}
