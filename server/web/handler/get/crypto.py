import json
import logging

import server.crypto.crypto as crypto
import server.crypto.revive_run as revive_run

from ..handler import GetHandler
from ..requestData import RequestData

log = logging.getLogger(__name__)


class Handler(GetHandler):
    def schema(self) -> dict:
        return self.create_schema(
            "Get crypo chip information",
            returns={
                "device": "string, device name",
                "serialNumber": "string, serial number",
                "publikKey": "string, public key",
                "chipDeathCount": "int, number of times the chip has died"
                
            }
        )

    def do_get(self, data: RequestData):
        # return the json data {'serial:' crypto.serial, 'pubkey': crypto.publicKey}
        with crypto.Chip() as chip:
            ret = chip.get_chip_info()
            ret['chipDeathCount'] = data.bb.chip_death_count
        return 200, json.dumps(ret)


class ReviveHandler(GetHandler):
    def schema(self) -> dict:
        return self.create_schema(
            "Revive the crypto chip, this command takes aproximately 10 seconds to execute.",
            returns={"status": "string, status of the revival"}
        )

    def do_get(self, data: RequestData):
        # we execute the revive command as a separate process and collect the output
        
        return 200, json.dumps({"status": revive_run.as_process()})
