import json
from ..handler import GetHandler
from ..requestData import RequestData
# from ....devices.supported_devices.profiles import InverterProfiles
from ....devices.profile_keys import ProtocolKey
from ....devices.supported_devices.profiles import ModbusDeviceProfiles

class Handler(GetHandler):
    def schema(self):
        # Schema is on line 15
        return self.create_schema("returns the supported inverters", 
                                  returns={"inverters": "{\"name\": backend name, \"dname\": display name, \"proto\": protocol (mb (modbus) or sol (solarman))}"})

    def get_supported_inverters(self):
        supported_inverters = ModbusDeviceProfiles().get_supported_devices()

        # The protocol part is temporarily hardcoded since we only support modbus and solarman
        supported_inverters = [{'name': profile.name, 'dname': profile.display_name, 'proto': 'mb' if profile.protocol == ProtocolKey.MODBUS else 'sol'} for profile in supported_inverters]
        
        # Add SunSpec and Enphase to the supported inverters
        supported_inverters.append({'name': 'sunspec', 'dname': 'SunSpec Compatible Device', 'proto': 'sunspec'})
        supported_inverters.append({'name': 'enphase', 'dname': 'Enphase', 'proto': 'rest'})
        
        ret = {"inverters": supported_inverters}
        return ret

    def do_get(self, data: RequestData):
        
        return 200, json.dumps(self.get_supported_inverters())