import logging
import requests
from server.inverters.supported_inverters.profiles import InverterProfile
from server.inverters.der import DER
from server.inverters.modbus import Modbus
from server.blackboard import BlackBoard
import server.crypto.crypto as crypto
import server.crypto.revive_run as revive_run
import random
import math

from .srcfulAPICallTask import SrcfulAPICallTask

log = logging.getLogger(__name__)

def generate_poisson_delay():
    AVERAGE_DELAY_MINUTES = 60
    """Generate exponentially distributed delay"""
    U = random.random()
    delay_minutes = -AVERAGE_DELAY_MINUTES * math.log(U)
    return int(delay_minutes * 60 * 1000)

def generate_entropy():
        return (random.getrandbits(32) << 32) | random.getrandbits(32)

class EntrophyTask(SrcfulAPICallTask):
    do_increase_chip_death_count = True  # prevents excessive incrementing of chip death count

    def __init__(self, event_time: int, bb: BlackBoard):
        super().__init__(event_time, bb)
        self.post_url = bb.entropy.endpoint
    
            
    def _create_jwt(self):
        with crypto.Chip() as chip:
            try:

                payload = {
                    "timestamp": self.get_time(),
                    "entropy": generate_entropy(),
                }

                headers = {
                    "alg": "ES256",
                    "typ": "JWT",
                    "device": chip.get_serial_number().hex(),
                    "opr": "entrophy"
                }

                jwt = chip.build_jwt(payload, headers, 5)
                EntrophyTask.do_increase_chip_death_count = True
            except crypto.Chip.Error as e:
                log.error("Error creating JWT: %s", e)
                raise e
        
        return jwt
    
    def post_data(self):
        if self.bb.entropy.do_mine:
            return super().post_data()
        else:
            return None

    def _data(self):
        retries = 5
        exception = None
    
        while retries > 0:
            try:
                jwt = self._create_jwt()
                return jwt
            except crypto.Chip.Error as e:
                exception = e
                if retries > 0:
                    retries -= 1
                    revive_run.as_process()
                
            except Exception as e:
                exception = e
                log.error("Error creating Entrophy JWT: %s", e)

        # if we end up here the chip has not been revived        
        if EntrophyTask.do_increase_chip_death_count:
            self.bb.increment_chip_death_count()
            EntrophyTask.do_increase_chip_death_count = False
        log.info("Incrementing chip death count to: %i ", self.bb.chip_death_count)
        raise exception


    def _on_200(self, reply):
        log.info("Response: %s", reply)
        self.adjust_time(self.get_time() + generate_poisson_delay())
        return self

    def _on_error(self, reply: requests.Response):
        log.warning("Error in harvest transport: %s", str(reply))
        return 0