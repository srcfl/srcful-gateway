import pytest
import server.web.get.name as get_name
from unittest.mock import Mock, patch
from server.tasks.getNameTask import GetNameTask

@patch('server.web.get.name.GetNameTask')
def test_get(mock_task):

  class MockTask:
    def __init__(self):
      self.name = 'test_name'
      self.response = Mock()
      self.response.status = 200
      self.t = Mock()

    def execute(self, timeMS):
      pass

    def name(self):
      return self._name

  mock_task.return_value = MockTask()

  handler = get_name.Handler()
  code, jsonstr = handler.doGet({}, None, None)
  assert code == 200
  assert jsonstr == '{"name": "test_name"}'

@patch('server.web.get.name.GetNameTask')
def test_get_notfound(mock_task):

  class MockResponse:
    def __init__(self):
      self.status = 404
      self.body = 'not found'

  class MockTask:
    def __init__(self):
      self.name = None
      self.response = MockResponse()
      self.t = Mock()

    def execute(self, timeMS):
      pass

    def name(self):
      return self._name

  mock_task.return_value = MockTask()

  handler = get_name.Handler()
  code, jsonstr = handler.doGet({}, None, None)
  assert code == 404
  assert jsonstr == '{"body": "not found"}'