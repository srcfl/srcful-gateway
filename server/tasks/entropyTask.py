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
from .task import Task

logger = logging.getLogger(__name__)

def generate_poisson_delay():
    AVERAGE_DELAY_MINUTES = 60
    """Generate exponentially distributed delay"""
    U = random.random()
    delay_minutes = -AVERAGE_DELAY_MINUTES * math.log(U)
    return 5000
    #return int(delay_minutes * 60 * 1000)

def generate_entropy(chip: crypto.Chip):
        random_bytes = chip.get_random()
        random_int = int.from_bytes(random_bytes, byteorder='big')

        # get the last 64 bits
        return random_int & 0xFFFFFFFFFFFFFFFF
        
class EntropyTransport(SrcfulAPICallTask):
    def __init__(self, event_time, bb, endpoint, jwt):
        super().__init__(event_time, bb)
        self.post_url = endpoint
        self.jwt = jwt

    def _data(self):
        return self.jwt

    def _on_200(self, reply):
        logger.info(f"Successfully sent entropy to {self.post_url}")
        return None  # No need to reschedule this task

    def _on_error(self, response):
        logger.error(f"Failed to send entropy to {self.post_url}: {response.text}")
        return 0  # Don't retry on error

class EntropyTask(Task):
    do_increase_chip_death_count = True  # prevents excessive incrementing of chip death count

    def __init__(self, event_time: int, bb: BlackBoard):
        super().__init__(event_time, bb)
    
            
    def _create_jwt(self):
        with crypto.Chip() as chip:
            try:

                payload = {
                    "timestamp": self.get_time(),
                    "entropy": generate_entropy(chip),
                }

                headers = {
                    "alg": "ES256",
                    "typ": "JWT",
                    "device": chip.get_serial_number().hex(),
                    "opr": "entropy"
                }

                jwt = chip.build_jwt(payload, headers, 5)
                EntropyTask.do_increase_chip_death_count = True
            except crypto.Chip.Error as e:
                logger.error("Error creating JWT: %s", e)
                raise e
        
        return jwt
    
    def execute(self, event_time):

        if self.bb.settings.entropy.do_mine:
            logger.info("Generating Entropy")
            # collect the tasks for each endpoint
            jwt = self._get_jwt()
            logger.info("Entropy JWT: %s", jwt)
            tasks = []
            logger.info("Entropy endpoints: %s", self.bb.settings.entropy.endpoints)
            for endpoint in self.bb.settings.entropy.endpoints:
                tasks.append(EntropyTransport(self.bb.time_ms() + 10, self.bb, endpoint, jwt))
            
            # finally we reschedule the task with a poisson delay
            self.adjust_time(self.bb.time_ms() + generate_poisson_delay())
            tasks.append(self)
            return tasks
        else:
            return None

    def _get_jwt(self):
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
                logger.error("Error creating Entrophy JWT: %s", e)

        # if we end up here the chip has not been revived        
        if EntropyTask.do_increase_chip_death_count:
            self.bb.increment_chip_death_count()
            EntropyTask.do_increase_chip_death_count = False
        logger.info("Incrementing chip death count to: %i ", self.bb.chip_death_count)
        raise exception