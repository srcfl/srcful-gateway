import json
import logging
from server.crypto import crypto

from ..handler import PostHandler
from ..requestData import RequestData

logger = logging.getLogger(__name__)


class Handler(PostHandler):
    def schema(self):
        return {
            "type": "post",
            "description": "Create a JWT token using the crypto chip",
            "required": {
                "barn": "object, the data payload for the JWT",
                "headers": "object, the headers for the JWT"
            },
            "optional": {
                "expires_in": "number, expiration time in minutes (default: 5)"
            },
            "returns": {
                "jwt": "string, the created JWT token",
                "headers": "object, headers associated with the JWT",
                "data": "object, the barn data used in the JWT"
            }
        }

    def do_post(self, data: RequestData):
        try:
            # Extract required parameters
            barn = data.data.get("barn")
            headers = data.data.get("headers")

            if barn is None:
                return 400, json.dumps({"error": "barn data is required"})

            if headers is None:
                return 400, json.dumps({"error": "headers are required"})

            # Optional expiration time (default 5 minutes)
            expires_in = data.data.get("expires_in", 5)

            # Create JWT using crypto chip
            with crypto.Chip() as chip:
                try:
                    jwt_token = chip.build_jwt(barn, headers, expires_in)
                    logger.info("JWT created successfully")

                    # Return JWT with data and headers
                    response = {
                        "jwt": jwt_token,
                        "headers": headers,
                        "data": barn,
                        "expires_in": expires_in
                    }

                    return 200, json.dumps(response)

                except crypto.ChipError as e:
                    logger.error("Error creating JWT: %s", e)
                    return 500, json.dumps({"error": f"Failed to create JWT: {str(e)}"})

        except Exception as e:
            logger.error("Unexpected error in JWT creation: %s", e)
            return 500, json.dumps({"error": f"Internal server error: {str(e)}"})
