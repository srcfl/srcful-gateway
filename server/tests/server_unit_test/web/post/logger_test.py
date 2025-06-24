from unittest.mock import Mock
from server.crypto.crypto_state import CryptoState
import server.web.handler.post.logger as post_logger
import json
import logging
from server.web.handler.requestData import RequestData
from server.app.blackboard import BlackBoard
import pytest

logger = logging.getLogger(__name__)


def test_post_root(blackboard):
    handler = post_logger.Handler()
    obj = {'logger': 'root', 'level': 'INFO'}
    result = handler.do_post(RequestData(blackboard, {}, {}, obj))
    assert result[0] == 200
    assert result[1] == json.dumps({'level': True})


def test_post_this(blackboard):
    handler = post_logger.Handler()
    obj = {'logger': logger.name, 'level': 'INFO'}
    result = handler.do_post(RequestData(blackboard, {}, {}, obj))
    assert result[0] == 200
    assert result[1] == json.dumps({'level': True})


def test_post_wrong_logger(blackboard):
    handler = post_logger.Handler()
    obj = {'logger': 'dret', 'level': 'INFO'}
    result = handler.do_post(RequestData(blackboard, {}, {}, obj))
    assert result[0] == 200
    assert result[1] == json.dumps({'level': False})


def test_post_wrong_level(blackboard):
    handler = post_logger.Handler()
    obj = {'logger': 'root', 'level': 'dret'}
    result = handler.do_post(RequestData(blackboard, {}, {}, obj))
    assert result[0] == 200
    assert result[1] == json.dumps({'level': False})


def test_post_no_logger(blackboard):
    handler = post_logger.Handler()
    obj = {'level': 'INFO'}
    result = handler.do_post(RequestData(blackboard, {}, {}, obj))
    assert result[0] == 400
    assert result[1] == json.dumps({'status': 'bad request', 'schema': handler.schema()})
