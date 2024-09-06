import logging
import requests
from server.inverters.supported_inverters.profiles import InverterProfile
from server.inverters.der import DER
from server.inverters.modbus import Modbus
from server.blackboard import BlackBoard
import server.crypto.crypto as crypto
import server.crypto.revive_run as revive_run

from .srcfulAPICallTask import SrcfulAPICallTask

log = logging.getLogger(__name__)


class IHarvestTransport(SrcfulAPICallTask):
    pass


class ITransportFactory:
    def __call__(self, event_time: int, bb: BlackBoard, der: DER, barn: dict) -> IHarvestTransport:
        pass


class HarvestTransport(IHarvestTransport):
    do_increase_chip_death_count = True  # prevents excessive incrementing of chip death count

    def __init__(self, event_time: int, bb: BlackBoard, barn: dict, der_profile: InverterProfile):
        super().__init__(event_time, bb)
        self.barn = barn
        self.der_profile = der_profile

    def _create_jwt(self):
        with crypto.Chip() as chip:
            try:
                name = ""
                jwt = chip.build_jwt(self.barn, name, 5)
                HarvestTransport.do_increase_chip_death_count = True
            except crypto.Chip.Error as e:
                log.error("Error creating JWT: %s", e)
                raise e
        
        return jwt

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
                log.error("Error creating JWT: %s", e)

        # if we end up here the chip has not been revived        
        if HarvestTransport.do_increase_chip_death_count:
            self.bb.increment_chip_death_count()
            HarvestTransport.do_increase_chip_death_count = False
        log.info("Incrementing chip death count to: %i ", self.bb.chip_death_count)
        raise exception

    def _on_200(self, reply):
        log.info("Response: %s", reply)

    def _on_error(self, reply: requests.Response):
        log.warning("Error in harvest transport: %s", str(reply))
        return 0
    

class HarvestTransportTimedSignature(HarvestTransport):

    # header and signature are class variables
    _header = None
    _signature_base64 = None

    def __init__(self, event_time: int, bb: BlackBoard, barn: dict, der_profile: InverterProfile):
        super().__init__(event_time, bb, barn, der_profile)

    def _create_header(self):
        with crypto.Chip() as chip:
            HarvestTransportTimedSignature._header = chip.build_header(self.der_profile.name.lower())
            HarvestTransportTimedSignature._header["valid_until"] = self.bb.time_ms() + 60000 * 45  # 45 minutes from now is the time to live

            HarvestTransportTimedSignature._signature_base64 = chip.get_signature(crypto.Chip.jwtlify(HarvestTransportTimedSignature._header))
            HarvestTransportTimedSignature._signature_base64 = crypto.Chip.base64_url_encode(HarvestTransportTimedSignature._signature_base64).decode("utf-8")
            
    def _data(self):
        if self._time_to_renew_header():
            self._create_header()

        jwt = crypto.Chip.jwtlify(HarvestTransportTimedSignature._header) + "." + crypto.Chip.jwtlify(self.barn) + "." + HarvestTransportTimedSignature._signature_base64

        # log.debug("JWT: %s", jwt)

        return jwt
    
    def _time_to_renew_header(self):
        return HarvestTransportTimedSignature._header is None or self._header["valid_until"] < self.bb.time_ms() + 60000 * 15   # 15 minutes before the header expires
    
class LocalHarvestTransportTimedSignature(HarvestTransportTimedSignature):

    def __init__(self, event_time: int, bb: BlackBoard, barn: dict, der_profile: InverterProfile):
        super().__init__(event_time, bb, barn, der_profile)
    
    def _create_header(self):
        log.info("Creating New Header...")
        super()._create_header()
        log.debug("Created New Header: %s", HarvestTransportTimedSignature._header)
        log.debug("Created New Signature: %s", HarvestTransportTimedSignature._signature_base64)

    def execute(self, event_time):
        try:
            jwt = self._data()
            log.debug("No sending in local harvest burning that barn!")
            #log.info("JWT: %s", jwt)
        except crypto.Chip.Error as e:
            log.error("Error creating JWT: %s", e)
            return 0


# Some factories
class DefaultHarvestTransportFactory(ITransportFactory):
    def __call__(self, event_time: int, bb: BlackBoard, barn: dict, der: DER) -> HarvestTransport:
        return HarvestTransport(event_time, bb, barn, der.get_profile())
    
class TimedSignatureHarvestTransportFactory(ITransportFactory):
    def __call__(self, event_time: int, bb: BlackBoard, barn: dict, der: DER) -> HarvestTransport:
        return HarvestTransportTimedSignature(event_time, bb, barn, der.get_profile())
    
class LocalTimedSignatureHarvestTransportFactory(ITransportFactory):
    def __call__(self, event_time: int, bb: BlackBoard, barn: dict, der: DER) -> HarvestTransport:
        return LocalHarvestTransportTimedSignature(event_time, bb, barn, der.get_profile())