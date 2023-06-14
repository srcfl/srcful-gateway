from unittest.mock import Mock, patch
from server.tasks.initializeTask import InitializeTask

import requests

def test_makeTheCallWithTaskJson():
  # mock atecc608b.base64UrlEncode(atecc608b.getSignature(idAndWallet))

  with patch('server.tasks.initializeTask.atecc608b') as mock_atecc608b:
    mock_atecc608b.getSerialNumber.return_value = b"deadbeef"
    mock_atecc608b.base64UrlEncode.return_value = "deadbeef:123456789abcdef"

    t = InitializeTask(0, {}, "aaa")
    reply = requests.post(t.post_url, json=t._json())
    assert reply.status_code == 200

def test_makeTheCall():
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


  reply = requests.post("https://api.srcful.dev/", json={'query': m})
  assert reply.status_code == 200
  assert reply.json()['data']['gatewayInception'] == None
