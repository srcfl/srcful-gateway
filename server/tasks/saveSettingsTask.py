import logging
import requests

import server.crypto.crypto as crypto
from server.blackboard import BlackBoard
from server.settings import Settings

from .srcfulAPICallTask import SrcfulAPICallTask

log = logging.getLogger(__name__)



class SaveSettingsTask(SrcfulAPICallTask):
    def __init__(self, event_time: int, bb: BlackBoard, settings: Settings = None):
        super().__init__(event_time, bb)
        self.is_initialized = None
        self.post_url = "https://api.srcful.dev/"
        self.settings = settings if settings is not None else bb.settings

    def _build_jwt(self):
        
        message = crypto.jwtlify(self.settings.to_dict())
        with crypto.Chip() as chip:
            header = self._build_header(chip.get_serial_number().hex())
            message = header + "." + message
            signature = chip.get_signature(message)
            message = message + "." + crypto.base64_url_encode(signature).decode("utf-8")
            return message
        
    def _build_header(self, serial_number):
        ret = crypto.jwtlify({
            "alg": "ES256",
            "typ": "JWT",
            "device": serial_number,
            "subKey": "settings",
        })

        return ret


    def _json(self):
        jwt = self._build_jwt()
        
        m = """
            mutation SetGatewayConfigurationWithDeviceJWT {
                setConfiguration(deviceConfigurationInputType: {
                    jwt: $jwt
                }) {
                    success
                }
                }
            """

        m = m.replace("$jwt", f'"{jwt}"')


        log.info("Preparing settings with jwt %s", jwt)
        log.debug("Query: %s", m)

        return {"query": m}

    def _on_200(self, reply: requests.Response):
        if (
            reply.json()["data"]["setConfiguration"] is not None
            and reply.json()["data"]["setConfiguration"]["success"] is not None
        ):
            self.is_saved = reply.json()["data"]["setConfiguration"]["success"]
        else:
            self.is_saved = False

    def _on_error(self, reply: requests.Response) -> int:
        log.warning("Failed to save settings %s")
        self.is_saved = False
        return 0
