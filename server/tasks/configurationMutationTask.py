import json
import logging
from typing import Dict, Any

from server.blackboard import BlackBoard
from server.tasks.srcfulAPICallTask import SrcfulAPICallTask
import server.crypto.crypto as crypto

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class ConfigurationMutationTask(SrcfulAPICallTask):
    def __init__(self, event_time: int, bb: BlackBoard, subkey: str, data: Dict[str, Any]):
        super().__init__(event_time, bb)
        self.subkey = subkey
        self.data = data
        self.is_saved = False
        self.post_url = "https://api.srcful.dev/"

    def _build_jwt(self):
        message = crypto.jwtlify(self.data)
        with crypto.Chip() as chip:
            header = self._build_header(chip.get_serial_number().hex())
            message = header + "." + message
            signature = chip.get_signature(message)
            message = message + "." + crypto.base64_url_encode(signature).decode("utf-8")
            return message
        
    def _build_header(self, serial_number):
        return crypto.jwtlify({
            "alg": "ES256",
            "typ": "JWT",
            "device": serial_number,
            "subKey": self.subkey,
        })

    def _json(self):
        jwt = self._build_jwt()
        
        mutation = """
            mutation SetGatewayConfigurationWithDeviceJWT {
                setConfiguration(deviceConfigurationInputType: {
                    jwt: $jwt
                }) {
                    success
                }
            }
        """

        mutation = mutation.replace("$jwt", f'"{jwt}"')

        logger.debug("Preparing configuration mutation with jwt %s", jwt)
        logger.debug("Query: %s", mutation)

        return {"query": mutation}

    def _on_200(self, reply):
        if (
            reply.json()["data"]["setConfiguration"] is not None
            and reply.json()["data"]["setConfiguration"]["success"] is not None
        ):
            self.is_saved = reply.json()["data"]["setConfiguration"]["success"]
        else:
            self.is_saved = False

    def _on_error(self, reply):
        logger.warning("Failed to mutate configuration %s", self.subkey)
        self.is_saved = False