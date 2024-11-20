# server/web/handler/post/entropy.py

import json
import time
from ..handler import PostHandler
from ..requestData import RequestData
from server.app.settings.settings_observable import ChangeSource
import server.crypto.crypto as crypto

class Handler(PostHandler):
    def schema(self):
        return self.create_schema(
            description="Update entropy settings and return status",
            optional={
                "do_mine": "boolean, optional",
                "mqtt_broker": "string, optional",
                "mqtt_port": "integer, optional",
                "mqtt_topic": "string, optional"
            },
            returns={
                "updated": "boolean, whether any settings were updated",
                "settings": "object, current entropy settings",
                "timestamp": "integer, current timestamp (if do_mine is true)",
                "serial": "string, crypto chip serial number (if do_mine is true)",
                "signature": "string, signature (if do_mine is true) - signature of the timestamp and serial concatenated"
            }
        )

    def do_post(self, data: RequestData):
        bb = data.bb
        entropy_settings = bb.settings.entropy
        updated = False

        # Update settings if provided
        # as the settings are updated any listeners are triggered
        # and the entropy task is added to the queue
        if 'do_mine' in data.data:
            entropy_settings.set_do_mine(data.data['do_mine'], ChangeSource.LOCAL)
            updated = True
        if 'mqtt_broker' in data.data:
            entropy_settings.set_mqtt_broker(data.data['mqtt_broker'], ChangeSource.LOCAL)
            updated = True
        if 'mqtt_port' in data.data:
            entropy_settings.set_mqtt_port(data.data['mqtt_port'], ChangeSource.LOCAL)
            updated = True
        if 'mqtt_topic' in data.data:
            entropy_settings.set_mqtt_topic(data.data['mqtt_topic'], ChangeSource.LOCAL)
            updated = True

        # Prepare response
        response = {
            "updated": updated,
            "settings": entropy_settings.to_dict()
        }

        # Add additional information if entropy mining is turned on
        if entropy_settings.do_mine:
            timestamp = int(time.time())
            response["timestamp"] = timestamp

            with crypto.Chip() as chip:
                serial = chip.get_serial_number()
                response["serial"] = serial.hex()

                # Create a signature of the timestamp and serial
                message = f"{timestamp}{serial}"
                signature = chip.get_signature(message).hex()
                response["signature"] = signature

        return 200, json.dumps(response)