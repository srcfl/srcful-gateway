import re
import json
import select
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import unquote_plus

from server.blackboard import BlackBoard
from . import handler

import logging

logger = logging.getLogger(__name__)


def request_handler_factory(bb: BlackBoard):
    class Handler(BaseHTTPRequestHandler):
        def __init__(self, *args, **kwargs):

            logger.info("initializing a request handler")

            self.api_get_dict = {
                "crypto": handler.get.crypto.Handler(),
                "cypto/revive": handler.get.crypto.ReviveHandler(),
                "hello": handler.get.hello.Handler(),
                "name": handler.get.name.Handler(),
                "logger": handler.get.logger.Handler(),
                "inverter": handler.get.inverter.Handler(),
                "inverter/modbus/holding/{address}": handler.get.modbus.HoldingHandler(),
                "inverter/modbus/input/{address}": handler.get.modbus.InputHandler(),
                "inverter/supported": handler.get.supported.Handler(),
                "network": handler.get.network.NetworkHandler(),
                "network/address": handler.get.network.AddressHandler(),
                "uptime": handler.get.uptime.Handler(),
                "wifi": handler.get.wifi.Handler(),
                "wifi/scan": handler.get.wifi.ScanHandler(),
                "version": handler.get.version.Handler(),
                "supported": handler.get.supported.Handler(),
                "notification": handler.get.notification.ListHandler(),
                "notification/{id}": handler.get.notification.MessageHandler(),
            }

            self.api_post_dict = {
                "invertertcp": handler.post.modbusTCP.Handler(),
                "inverterrtu": handler.post.modbusRTU.Handler(),
                "invertersolarman": handler.post.modbusSolarman.Handler(),
                "wifi": handler.post.wifi.Handler(),
                "initialize": handler.post.initialize.Handler(),
                "inverter/modbus": handler.post.modbus.Handler(),
                "logger": handler.post.logger.Handler(),
                "echo": handler.post.echo.Handler(),
            }

            self.api_delete_dict = {
                "inverter": handler.delete.inverter.Handler(),
                "notification/{id}": handler.delete.notification.Handler(),
            }

            self.api_get = Handler.convert_keys_to_regex(self.api_get_dict)
            self.api_post = Handler.convert_keys_to_regex(self.api_post_dict)
            self.api_delete = Handler.convert_keys_to_regex(self.api_delete_dict)
            super(Handler, self).__init__(*args, **kwargs)

        @staticmethod
        def query_2_dict(query_string: str):
            return Handler.post_2_dict(query_string)

        @staticmethod
        def post_2_dict(post_data: str):
            if "=" not in post_data:
                return {}
            return {
                unquote_plus(k): unquote_plus(v)
                for k, v in (x.split("=") for x in post_data.split("&"))
            }

        @staticmethod
        def convert_keys_to_regex(api_dict):
            regex_dict = {}
            for key, value in api_dict.items():
                key = re.sub(r"\{(.+?)\}", r"(?P<\1>.+)", key)
                regex_dict[re.compile("^" + key + "$")] = value
            return regex_dict

        @staticmethod
        def get_api_handler(path: str, api_root: str, api_handler_regex: dict):
            if path.startswith(api_root):
                for pattern, _handler in api_handler_regex.items():
                    match = pattern.match(path[len(api_root) :])
                    if match:
                        return _handler, match.groupdict()
            return None, None

        @staticmethod
        def get_data(headers: dict, rfile):
            if "Content-Length" not in headers:
                return {}
            content_length = int(headers["Content-Length"])
            content = rfile.read(content_length).decode("utf-8")

            if content_length == 0 or len(content) == 0:
                return {}

            try:
                post_data = json.loads(content)
            except json.decoder.JSONDecodeError:
                post_data = Handler.post_2_dict(content)
            except Exception:
                logger.exception("Failed to parse post json data: %s", content)
                post_data = {}

            return post_data

        def send_api_response(self, code: int, response: str):
            self.send_response(code)
            self.send_header("Content-type", "application/json")
            response = bytes(response, "utf-8")
            self.send_header("Content-Length", len(response))
            self.end_headers()
            self.wfile.write(response)

        def pre_do(self, path: str):
            parts = path.split("?")
            query_string = parts[1] if len(parts) > 1 else ""
            return parts[0], Handler.query_2_dict(query_string)

        # this needs to be POST as this is a direct mapping of the http method
        def do_POST(self):
            path, query = self.pre_do(self.path)

            api_handler, params = Handler.get_api_handler(path, "/api/", self.api_post)
            if api_handler is not None:
                post_data = Handler.get_data(self.headers, self.rfile)

                rdata = handler.RequestData(bb, params, query, post_data)

                code, response = api_handler.do_post(rdata)
                self.send_api_response(code, response)
                return
            else:
                self.send_response(404)
                self.end_headers()
                return

        # this needs to be GET as this is a direct mapping of the http method
        def do_GET(self):
            path, query = self.pre_do(self.path)

            if path.startswith("/doc/") or path.endswith("/doc"):
                schema = self.get_doc(path[4:])
                self.send_api_response(200, schema)
                return

            api_handler, params = Handler.get_api_handler(path, "/api/", self.api_get)
            rdata = handler.RequestData(bb, params, query, {})

            if api_handler is not None:
                code, response = api_handler.do_get(rdata)
                self.send_api_response(code, response)
            else:
                # check if we have a post handler
                api_handler, params = Handler.get_api_handler(
                    path, "/api/", self.api_post
                )
                if api_handler is not None:
                    self.send_api_response(200, api_handler.jsonSchema())
                    return
                else:
                    code, htlm = handler.get.root.Handler().do_get(rdata)
                    html_bytes = bytes(htlm, "utf-8")

                    self.send_response(code)
                    self.send_header("Content-type", "text/html")
                    self.send_header("Content-Length", len(html_bytes))
                    self.end_headers()

                    self.wfile.write(html_bytes)

        # this needs to be DELETE as this is a direct mapping of the http method
        def do_DELETE(self):
            path, query = self.pre_do(self.path)

            api_handler, params = Handler.get_api_handler(
                path, "/api/", self.api_delete
            )
            if api_handler is not None:
                post_data = Handler.get_data(self.headers, self.rfile)

                rdata = handler.RequestData(bb, params, query, post_data)

                code, response = api_handler.do_delete(rdata)
                self.send_api_response(code, response)
                return
            else:
                self.send_response(404)
                self.end_headers()
                return

        def get_doc_dict(self, api_dict: dict, path: str):
            while path.startswith("/"):
                path = path[1:]
            ret = {}
            for key, _handler in api_dict.items():
                if key.startswith(path):
                    if hasattr(_handler, "schema"):
                        ret[key] = _handler.schema()
                    else:
                        ret[key] = {"status": "not documented"}
            return ret

        def get_doc(self, path: str):
            ret = {}
            ret["GET"] = self.get_doc_dict(self.api_get_dict, path)
            ret["POST"] = self.get_doc_dict(self.api_post_dict, path)
            ret["DELETE"] = self.get_doc_dict(self.api_delete_dict, path)
            return json.dumps(ret, indent=3)

    return Handler

class Server:
    _web_server: HTTPServer = None

    def __init__(self, web_host: tuple[str, int], bb: BlackBoard):
        self._web_server = HTTPServer(web_host, request_handler_factory(bb))
        
        self._web_server.timeout = 0.1
        #self._web_server.socket.setblocking(False)

    def close(self):
        if self._web_server:
            self._web_server.server_close()
            self._web_server = None

    def request_pending(self) -> bool:
        ready_to_read, _, _ = select.select([self._web_server.socket], [], [], 0)
        return ready_to_read

    def request_queue_size(self) -> int:
        return self._web_server.request_queue_size

    def handle_request(self):
        #logger.info("handling request")
        self._web_server.handle_request()

    def __del__(self):
        self.close()
