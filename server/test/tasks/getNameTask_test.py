from unittest.mock import Mock, patch
from server.tasks.getNameTask import GetNameTask

import requests

# these tests currently rely on the api being up and running

def test_makeTheCallWithTaskJson():
  t = GetNameTask(0, {})
  reply = requests.post(t.post_url, json=t._json())
  assert reply.status_code == 200

def test_makeTheCallWithExecute():
  t = GetNameTask(0, {})
  t.execute(0)
  t.t.join()
  t.execute(0)
  assert t.name != None

# test_makeTheCall():
# make a GraphQL query
# = """{
# gatewayConfiguration {
#	  gatewayName(id:$var_id) {
#     name
#   }
# }
#"""
#
# = q.replace('$var_id', '"wabi"')
#
#eply = requests.post("https://api.srcful.dev/", json={'query': q})
#ssert reply.status_code == 200
#ssert reply.json()['data']['gatewayConfiguration']['gatewayName']['name'] == 'Macho Beige Gecko'
