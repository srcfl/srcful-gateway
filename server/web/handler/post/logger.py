import json
import logging

from ..requestData import RequestData
from ..handler import PostHandler

logger = logging.getLogger(__name__)


class Handler(PostHandler):
    def schema(self):
        return {
            "type": "post",
            "description": "set the log level of a logger",
            "required": {
                "logger": "string, name of logger i.e. server.web.server",
                "level": "string, name of level i.e. DEBUG, INFO, WARNING, ERROR, CRITICAL",
            },
            "returns": {
                "level": "boolean, true if the logger was valid and the level was set"
            },
        }

    def json_schema(self):
        return json.dumps(self.schema())

    def do_post(self, data: RequestData):
        if "logger" in data.data and "level" in data.data:
            # check that the logger and level are valid
            try:
                # check that the logger actually exits in the logging module - we cannot directl use getLogger as this will create the logger
                if (
                    data.data["logger"] != "root"
                    and data.data["logger"]
                    not in logging.root.manager.loggerDict
                ):
                    return 200, json.dumps({"level": False})

                the_logger = logging.getLogger(data.data["logger"])
                level = logging.getLevelName(data.data["level"])
                the_logger.setLevel(level)
                return 200, json.dumps({"level": True})
            except Exception as e:
                logger.error("Failed to set logger level: %s", data.data)
                logger.error(e)
                return 200, json.dumps({"level": False})

        else:
            # return a bad request and append the json schema
            return 400, json.dumps({"status": "bad request", "schema": self.schema()})
