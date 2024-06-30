import json
import logging

import server.crypto.crypto as crypto
import server.crypto.revive_run as revive_run

from ..handler import GetHandler
from ..requestData import RequestData

log = logging.getLogger(__name__)


class Handler(GetHandler):

    @property
    def DEVICE(self):
        return "deviceName"
    
    @property   
    def SERIAL_NO(self):
        return "serialNumber"
    
    @property
    def PUBLIC_KEY(self):
        return "publicKey"
    
    @property
    def COMPACT_KEY(self):
        return "compactKey"
    
    @property
    def CHIP_DEATH_COUNT(self):
        return "chipDeathCount"

    def schema(self) -> dict:
        return self.create_schema(
            "Get crypo chip information",
            returns={
                self.DEVICE: "string, device name",
                self.SERIAL_NO: "string, serial number as hex string",
                self.PUBLIC_KEY: "string, public key as hex string",
                self.COMPACT_KEY: "string, compact form of public key ecc swarm key used in Helium",
                self.CHIP_DEATH_COUNT: "int, number of times the chip has died"
                
            }
        )

    def do_get(self, data: RequestData):
        # return the json data {'serial:' crypto.serial, 'pubkey': crypto.publicKey}
        with crypto.Chip() as chip:
            pub_key = chip.get_public_key()
            ret = {}
            ret[self.DEVICE] = chip.get_device_name()
            ret[self.SERIAL_NO] = chip.get_serial_number().hex()
            ret[self.PUBLIC_KEY] = pub_key.hex()
            ret[self.COMPACT_KEY] = chip.public_key_to_compact(pub_key).hex()
            ret[self.CHIP_DEATH_COUNT] = data.bb.chip_death_count
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
