import json
from ..handler import GetHandler
from enum import Enum
from ..requestData import RequestData
from server.devices.registerValue import RegisterValue
from server.devices.profile_keys import DataTypeKey, FunctionCodeKey, EndiannessKey
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Example query: inverter/modbus/holding/40069?size=2&type=float&endianess=big

# Parameter enum class
class RegisterType(str, Enum):
    DEVICE_ID = "device_id"
    FUNCTION_CODE = "function_code"
    ADDRESS = "address"
    SIZE = "size"
    TYPE = "type"
    ENDIANESS = "endianess"
    SCALE_FACTOR = "scale_factor"
    
class ReturnType(str, Enum):
    REGISTER = "register"
    SIZE = "size"
    RAW_VALUE = "raw_value"
    SWAPPED_VALUE = "swapped_value"
    VALUE = "value"

class ModbusHandler(GetHandler):
    def schema(self):
        return {
            "type": "get",
            "description": "Get data from a modbus registger",
            "required": {
                RegisterType.DEVICE_ID: "string, device id",
                RegisterType.ADDRESS: "int, address of the register to read url parameter",
            },
            "optional": {
                RegisterType.FUNCTION_CODE: "int, function code to read the register (0x03 for holding, 0x04 for input)",
                RegisterType.SIZE: "int, size of the register to read (default: 1)",
                RegisterType.TYPE: "string, data type of the register to read (default: none)",
                RegisterType.ENDIANESS: "string, endianess of the register to read big or little. (default: big)",
                RegisterType.SCALE_FACTOR: "float, scale factor to apply to the value read (default: 1.0)",
            },
            "returns": {
                ReturnType.REGISTER: "int, address of the register read",
                ReturnType.SIZE: "int, size of the register read",
                ReturnType.RAW_VALUE: "string, hex representation of the raw value read",
                ReturnType.VALUE: "string, value read from the register, if applicable",
            },
        }

    def do_get(self, request_data: RequestData):
        device_id: str = request_data.query_params.get(RegisterType.DEVICE_ID, None)
        
        # Convert function code to enum if it's an integer
        raw_function_code = request_data.query_params.get(RegisterType.FUNCTION_CODE, FunctionCodeKey.READ_INPUT_REGISTERS)
        function_code: FunctionCodeKey = raw_function_code if isinstance(raw_function_code, FunctionCodeKey) else FunctionCodeKey(int(raw_function_code))
        
        address: int = int(request_data.query_params.get(RegisterType.ADDRESS, -1))
        size: int = int(request_data.query_params.get(RegisterType.SIZE, 1))
        
        # Convert type string to enum
        raw_type = request_data.query_params.get(RegisterType.TYPE, DataTypeKey.U16)
        data_type: DataTypeKey = raw_type if isinstance(raw_type, DataTypeKey) else DataTypeKey(raw_type)
        
        # Convert endianness string to enum
        raw_endianness = request_data.query_params.get(RegisterType.ENDIANESS, EndiannessKey.BIG)
        endianness: EndiannessKey = raw_endianness if isinstance(raw_endianness, EndiannessKey) else EndiannessKey(raw_endianness)
        
        scale_factor: float = float(request_data.query_params.get(RegisterType.SCALE_FACTOR, 1.0))
        
        logger.debug(f"address: {address}, device_id: {device_id}, function_code: {function_code}, size: {size}, type: {data_type}, endianness: {endianness}")
        
        if device_id is None:
            return 400, json.dumps({"error": "missing device index"})
        if address == -1:
            return 400, json.dumps({"error": "missing address"})
        if len(request_data.bb.devices.lst) == 0:
            return 400, json.dumps({"error": "No devices open"})

        raw = bytearray()
        
        device = request_data.bb.devices.find_sn(device_id)
        
        if device is None:
            return 400, json.dumps({"error": "device not found"})
        
        logger.debug(f"Using the device: {device.get_config()}")
        
        raw, swapped, value = RegisterValue(
            address=address,
            size=size,
            function_code=function_code,
            data_type=data_type,
            endianness=endianness,
            scale_factor=scale_factor
        ).read_value(device)

        ret = {
            ReturnType.REGISTER: address,
            ReturnType.SIZE: size,
            ReturnType.RAW_VALUE: raw.hex(),
            ReturnType.SWAPPED_VALUE: swapped.hex(),
            ReturnType.VALUE: value
        }

        return 200, json.dumps(ret)
            

    def get_register_type(self):
        raise NotImplementedError()
