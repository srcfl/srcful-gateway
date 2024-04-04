import json
import server.crypto.crypto as crypto

from ..handler import GetHandler
from ..requestData import RequestData


class Handler(GetHandler):
    def schema(self) -> dict:
        self.create_schema(
            "Get crypo chip information",
            returns={
                "device": "string, device name",
                "serialNumber": "string, serial number",
                "publikKey": "string, public key",
                "publicKey_pem": "string, public key in pem format",
            }
        )

    def do_get(self, data: RequestData):
        # return the json data {'serial:' crypto.serial, 'pubkey': crypto.publicKey}
        with crypto.Chip() as chip:
            ret = chip.get_chip_info()
            ret["publicKey_pem"] = chip.public_key_2_pem(chip.get_public_key())
        
        return 200, json.dumps(ret)
