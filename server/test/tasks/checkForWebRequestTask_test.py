from ...tasks.checkForWebRequestTask import CheckForWebRequest


def test_create():
  t = CheckForWebRequest(0, {}, None)
  assert t is not None