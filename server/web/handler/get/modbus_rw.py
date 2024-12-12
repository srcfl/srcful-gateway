import json
from ..handler import GetHandler
from enum import Enum
from ..requestData import RequestData
from typing import List
from server.devices.Device import Device
from server.devices.registerValue import RegisterValue
from server.devices.profile_keys import DataTypeKey, FunctionCodeKey

# Example query: inverter/modbus/holding/40069?size=2&type=float&endianess=big

# Parameter enum class
class RegisterType(Enum):
    DEVICE_ID = "device_id"
    FUNCTION_CODE = "function_code"
    ADDRESS = "address"
    SIZE = "size"
    TYPE = "type"
    ENDIANESS = "endianess"
    
class ReturnType(Enum):
    REGISTER = "register"
    SIZE = "size"
    RAW_VALUE = "raw_value"
    VALUE = "value"

class ModbusHandler(GetHandler):
    def schema(self):
        return {
            "type": "get",
            "description": "Get data from a modbus registger",
            "required": {
                RegisterType.DEVICE_ID: "int, device id",
                RegisterType.ADDRESS: "int, address of the register to read url parameter",
            },
            "optional": {
                RegisterType.FUNCTION_CODE: "int, function code to read the register (0x03 for holding, 0x04 for input)",
                RegisterType.SIZE: "int, size of the register to read (default: 1)",
                RegisterType.TYPE: "string, data type of the register to read (default: none)",
                RegisterType.ENDIANESS: "string, endianess of the register to read big or little. (default: big)",
            },
            "returns": {
                ReturnType.REGISTER: "int, address of the register read",
                ReturnType.SIZE: "int, size of the register read",
                ReturnType.RAW_VALUE: "string, hex representation of the raw value read",
                ReturnType.VALUE: "string, value read from the register, if applicable",
            },
        }

    def do_get(self, request_data: RequestData):
        address = request_data.post_params.get(RegisterType.ADDRESS, None)
        device_id = request_data.post_params.get(RegisterType.DEVICE_ID, None)
        function_code = request_data.post_params.get(RegisterType.FUNCTION_CODE, FunctionCodeKey.READ_INPUT_REGISTERS)
        size = int(request_data.query_params.get(RegisterType.SIZE, 1)) # default to 1 register (2 bytes)
        type = request_data.query_params.get(RegisterType.TYPE, DataTypeKey.U16)
        endianess = request_data.query_params.get(RegisterType.ENDIANESS, RegisterValue.Endianness.BIG)
        
        if device_id is None:
            return 400, json.dumps({"error": "missing device index"})
        if address is None:
            return 400, json.dumps({"error": "missing address"})
        if len(request_data.bb.devices.lst) == 0:
            return 400, json.dumps({"error": "No devices open"})

        raw = bytearray()
        
        try:
            datatype = RegisterValue.Type.from_str(
                request_data.query_params.get(RegisterType.TYPE, "none")
            )
            endianness = RegisterValue.Endianness.from_str(
                request_data.query_params.get(RegisterType.ENDIANESS, "big")
            )
            
            # find the device with 
            devices: List[Device] = request_data.bb.devices.lst
            device: Device = next((device for device in devices if device.get_SN() == device_id), None)
            
            if device is None:
                return 400, json.dumps({"error": "device not found"})
            
            raw, value = RegisterValue(
                address, size, self.get_register_type(), datatype, endianness
            ).read_value(device)

            ret = {
                ReturnType.REGISTER: address,
                ReturnType.SIZE: size,
                ReturnType.RAW_VALUE: raw.hex(),
            }
            if value is not None:
                ret[ReturnType.VALUE] = value

            return 200, json.dumps(ret)
        except Exception as e:
            return 400, json.dumps({"error": str(e)})

    def get_register_type(self):
        raise NotImplementedError()
