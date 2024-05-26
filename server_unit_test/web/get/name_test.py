import pytest
import server.web.handler.get.name as get_name
from unittest.mock import Mock, patch

from server.tasks.getNameTask import GetNameTask


@patch("server.web.handler.get.name.GetNameTask")
def test_get(mock_task):
    class MockTask:
        def __init__(self):
            self.name = "test_name"
            self.reply = Mock()
            self.reply.status = 200

            assert hasattr(GetNameTask(0, None), "reply")

        def execute(self, timeMS):
            pass

        def name(self):
            return self.name

    mock_task.return_value = MockTask()

    handler = get_name.Handler()
    code, jsonstr = handler.do_get(None)
    assert code == 200
    assert jsonstr == '{"name": "test_name"}'


@patch("server.web.handler.get.name.GetNameTask")
def test_get_notfound(mock_task):
    class MockResponse:
        def __init__(self):
            self.status = 404
            self.body = "not found"

    class MockTask:
        def __init__(self):
            self.name = None
            self.reply = MockResponse()

            assert hasattr(GetNameTask(0, None), "reply")

        def execute(self, timeMS):
            pass

        def name(self):
            return self.name

    mock_task.return_value = MockTask()

    handler = get_name.Handler()
    code, jsonstr = handler.do_get(None)
    assert code == 404
    assert jsonstr == '{"body": "not found"}'
