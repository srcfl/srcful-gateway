import server.web.handler.post.logger as post_logger
import json
import logging
from server.web.handler.requestData import RequestData

logger = logging.getLogger(__name__)

def test_post_root():
    handler = post_logger.Handler()
    obj = {'logger': 'root', 'level': 'INFO'}
    request_data = RequestData({}, {}, {}, obj, None, None, None)
    result = handler.doPost(request_data)
    assert result[0] == 200
    assert result[1] == json.dumps({'level': True})

def test_post_this():
    handler = post_logger.Handler()
    obj = {'logger': logger.name, 'level': 'INFO'}
    request_data = RequestData({}, {}, {}, obj, None, None, None)
    result = handler.doPost(request_data)
    assert result[0] == 200
    assert result[1] == json.dumps({'level': True})

def test_post_wrong_logger():
    handler = post_logger.Handler()
    obj = {'logger':'dret', 'level':'INFO'}
    request_data = RequestData({}, {}, {}, obj, None, None, None)
    result = handler.doPost(request_data)
    assert result[0] == 200
    assert result[1] == json.dumps({'level': False})

def test_post_wrong_level():
    handler = post_logger.Handler()
    obj = {'logger':'root', 'level':'dret'}
    request_data = RequestData({}, {}, {}, obj, None, None, None)
    result = handler.doPost(request_data)
    assert result[0] == 200
    assert result[1] == json.dumps({'level': False})

def test_post_no_logger():
    handler = post_logger.Handler()
    obj = {'level':'INFO'}
    request_data = RequestData({}, {}, {}, obj, None, None, None)
    result = handler.doPost(request_data)
    assert result[0] == 400
    assert result[1] == json.dumps({'status': 'bad request', 'schema': handler.jsonDict()})
