import logging
import requests
import server.crypto.crypto as crypto
from server.blackboard import BlackBoard

from .srcfulAPICallTask import SrcfulAPICallTask

log = logging.getLogger(__name__)


class StartupInfoTask(SrcfulAPICallTask):
    def __init__(self, event_time: int, bb: BlackBoard):
        super().__init__(event_time, bb)
        self.post_url = "https://api.srcful.dev/"

    def _data(self):

        jwt = None

        with crypto.Chip() as chip:
            
            inverter_model = None
            inverter_profile_version = None

            if len(self.bb.devices.lst) > 0:
                inverter_model = self.bb.devices.lst[0].get_type()
                inverter_profile_version = self.bb.devices.lst[0].get_profile().version

            payload = {
                "firmware version": self.bb.get_version(),
                "inverter profile version": inverter_profile_version,
            }

            jwt = chip.build_jwt(payload, inverter_model, 5)

        return jwt

    def _on_200(self, reply: requests.Response):
        log.info("Response: %s", reply)

    def _on_error(self, reply: requests.Response) -> int:
        log.error("Error: %s", reply)
        return 0
