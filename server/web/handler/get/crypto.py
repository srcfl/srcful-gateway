import json
import logging
from server.crypto.crypto_state import CryptoState
import server.crypto.revive_run as revive_run
from ..handler import GetHandler
from ..requestData import RequestData

log = logging.getLogger(__name__)


class Handler(GetHandler):

    def schema(self) -> dict:
        return self.create_schema(
            "Get crypo chip information",
            returns={
                CryptoState.device_key(): "string, device name",
                CryptoState.serial_no_key(): "string, serial number as hex string",
                CryptoState.public_key_key(): "string, public key as hex string",
                CryptoState.compact_key_key(): "string, compact form of public key ecc swarm key used in Helium",
                CryptoState.chip_death_count_key(): "int, number of times the chip has died"
                
            }
        )
    
    def do_get(self, data: RequestData):
        ret = data.bb.crypto_state().to_dict(data.bb.chip_death_count)
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
