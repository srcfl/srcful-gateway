import json
import logging
import subprocess

import server.crypto.crypto as crypto

from ..handler import GetHandler
from ..requestData import RequestData

log = logging.getLogger(__name__)


def run_revive_script():
    # Specify the script and arguments
    command = ['python', './server/crypto/revive.py']

    # Run the command as a subprocess and capture the output
    result = subprocess.run(command, capture_output=True, text=True, check=False)    # Check if the subprocess executed successfully
    log.debug("Revive Script output: %S", result.stdout)
    if result.returncode != 0:
        log.error("Revive Script Error:", result.stderr)

    return result.stdout


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
    
class ReviveHandler(GetHandler):
    def schema(self) -> dict:
        self.create_schema(
            "Revive the crypto chip, this command takes aproximately 10 seconds to execute.",
            returns={"status": "string, status of the revival"}
        )

    def do_get(self, data: RequestData):
        # we execute the revive command as a separate process and collect the output
        
        
        return 200, json.dumps({"status": run_revive_script()})
