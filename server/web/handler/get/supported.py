import json
from ..handler import GetHandler
from ..requestData import RequestData
from ....inverters.supported_inverters.profiles import InverterProfiles
from ....inverters.enums import ProtocolKey

class Handler(GetHandler):
    def schema(self):
        # Schema is on line 15
        return self.create_schema("returns the supported inverters", 
                                  returns={"inverters": "{\"name\": backend name, \"dname\": display name, \"proto\": protocol (mb (modbus) or sol (solarman))}"})

    def get_supported_inverters(self):
        supported_inverters = InverterProfiles().get_supported_inverters()

        # The protocol part is temporarily hardcoded since we only support modbus and solarman
        supported_inverters = [{'name': profile.name, 'dname': profile.display_name, 'proto': 'mb' if profile.protocol == ProtocolKey.MODBUS.value else 'sol'} for profile in supported_inverters]
        
        ret = {"inverters": supported_inverters}
        return ret

    def do_get(self, data: RequestData):
        
        return 200, json.dumps(self.get_supported_inverters())