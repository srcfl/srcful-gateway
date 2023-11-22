import server.web.post.logger as post_logger
import json
import logging

logger = logging.getLogger(__name__)

def test_post_root():
    handler = post_logger.Handler()
    result = handler.doPost({"logger":"root", "level":"INFO"}, {}, None, None)
    assert result[0] == 200
    assert result[1] == json.dumps({"level": True})

def test_post_this():
    handler = post_logger.Handler()
    result = handler.doPost({"logger":logger.name, "level":"INFO"}, {}, None, None)
    assert result[0] == 200
    assert result[1] == json.dumps({"level": True})

def test_post_wrong_logger():
    handler = post_logger.Handler()
    result = handler.doPost({"logger":"dret", "level":"INFO"}, {}, None, None)
    assert result[0] == 200
    assert result[1] == json.dumps({"level": False})

def test_post_wrong_level():
    handler = post_logger.Handler()
    result = handler.doPost({"logger":"root", "level":"dret"}, {}, None, None)
    assert result[0] == 200
    assert result[1] == json.dumps({"level": False})

def test_post_no_logger():
    handler = post_logger.Handler()
    result = handler.doPost({"level":"INFO"}, {}, None, None)
    assert result[0] == 400
    assert result[1] == json.dumps({"status": "bad request", "schema": handler.jsonDict()})
