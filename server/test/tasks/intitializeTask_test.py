from unittest.mock import Mock, patch
from server.tasks.initializeTask import InitializeTask

import requests

## these currently make the actuall calls to the api

def test_executeTask():
  
  t = InitializeTask(0, {}, "aaa")
  assert t.isInitialized == None
  t._json = Mock(return_value=_internalJsonQuery())
  t.execute(0)
  t.t.join()
  t.execute(0)
  assert t._json.called
  assert t.isInitialized == False

def test_makeTheCallWithTaskJson():
  # mock atecc608b.base64UrlEncode(atecc608b.getSignature(idAndWallet))

  with patch('server.tasks.initializeTask.atecc608b') as mock_atecc608b:
    mock_atecc608b.getSerialNumber.return_value = b"deadbeef"
    mock_atecc608b.getSignature.return_value = b"123456789abcdef"

    t = InitializeTask(0, {}, "aaa")
    theJson = t._json()
    # inject dryRun into the json
    theJson['query'] = theJson['query'].replace('gatewayInitialization:{idAndWallet', 'gatewayInitialization:{dryRun:true, idAndWallet')
    reply = requests.post(t.post_url, json=theJson)
    assert reply.status_code == 200
    assert reply.json()['data']['gatewayInception']['initialize']['initialized'] == False

def test_makeTheCall():
  reply = requests.post("https://api.srcful.dev/", json=_internalJsonQuery())
  assert reply.status_code == 200
  assert reply.json()['data']['gatewayInception']['initialize']['initialized'] == False

def _internalJsonQuery():
  # make a GraphQL
  m = """mutation {
      gatewayInception {
        initialize(gatewayInitialization:{idAndWallet:"$var_idAndWallet", signature:"$var_sign", dryRun:true}) {
          initialized
        }
      }
    }"""

  m = m.replace('$var_idAndWallet', "aa:bb")
  m = m.replace('$var_sign', "123456789abcdef")
  return {'query': m}