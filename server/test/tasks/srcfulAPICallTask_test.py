import server.tasks.srcfulAPICallTask as apiCall

def test_createSrcfulAPICall():
  t = apiCall.SrcfulAPICallTask(0, {})
  assert t is not None

