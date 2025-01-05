import json
from ..handler import GetHandler
from enum import Enum
from ..requestData import RequestData
from server.devices.registerValue import RegisterValue
from server.devices.profile_keys import DataTypeKey, FunctionCodeKey, EndiannessKey
import logging
from typing import List, Dict, Union, Tuple


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Example query: inverter/modbus/holding/40069?size=2&type=float&endianess=big

# Parameter enum class
class ModbusParameter(str, Enum):
    DEVICE_ID = "device_id"
    FUNCTION_CODE = "function_code"
    ADDRESS = "address"
    SIZE = "size"
    TYPE = "type"
    ENDIANESS = "endianess"
    SCALE_FACTOR = "scale_factor"
    VALUES = "values"
    
    
class ReturnType(str, Enum):
    REGISTER = "register"
    SIZE = "size"
    RAW_VALUE = "raw_value"
    SWAPPED_VALUE = "swapped_value"
    VALUE = "value"
    SUCCESS = "success"


class ModbusHandler(GetHandler):
    def schema(self):
        return {
            "type": "get",
            "description": "Get data from a modbus register or write to registers",
            "required": {
                ModbusParameter.DEVICE_ID: "string, device id",
                ModbusParameter.ADDRESS: "int, address of the register",
            },
            "optional": {
                ModbusParameter.FUNCTION_CODE: "int, function code (0x03=read holding, 0x04=read input, 0x10=write multiple)",
                ModbusParameter.SIZE: "int, size of the register to read (default: 1)",
                ModbusParameter.TYPE: "string, data type of the register (default: none)",
                ModbusParameter.ENDIANESS: "string, endianess of the register big or little. (default: big)",
                ModbusParameter.SCALE_FACTOR: "float, scale factor to apply to the value (default: 1.0)",
                ModbusParameter.VALUES: "string, comma-separated values for writing (required for write operations)",
            },
            "returns": {
                ReturnType.REGISTER: "int, address of the register",
                ReturnType.SIZE: "int, size of the register",
                ReturnType.RAW_VALUE: "string, hex representation of the raw value (read only)",
                ReturnType.VALUE: "string/number, value read from register or success status for write",
                ReturnType.SUCCESS: "boolean, indicates if write operation was successful (write only)",
            },
        }

    def do_get(self, request_data: RequestData) -> Tuple[int, str]:
        try:
            # Parse common parameters
            device_id: str = request_data.query_params.get(ModbusParameter.DEVICE_ID, None)
            if device_id is None:
                return 400, json.dumps({"error": "missing device index"})
                
            address: int = int(request_data.query_params.get(ModbusParameter.ADDRESS, -1))
            if address == -1:
                return 400, json.dumps({"error": "missing address"})
                
            if len(request_data.bb.devices.lst) == 0:
                return 400, json.dumps({"error": "No devices open"})

            device = request_data.bb.devices.find_sn(device_id)
            if device is None:
                return 400, json.dumps({"error": "device not found"})
                
            # Convert function code to enum if it's an integer
            raw_function_code = request_data.query_params.get(ModbusParameter.FUNCTION_CODE, FunctionCodeKey.READ_INPUT_REGISTERS)
            
            try:
                function_code_int = int(raw_function_code)
            except ValueError:
                return 400, json.dumps({"error": f"function code must be a number"})
                
            # Check if function code exists in enum
            if function_code_int not in [e.value for e in FunctionCodeKey]:
                return 400, json.dumps({"error": f"invalid function code: {function_code_int}"})
                
            function_code = FunctionCodeKey(function_code_int)  # Safe to convert now
            
            # Handle write operations
            if function_code == FunctionCodeKey.WRITE_MULTIPLE_REGISTERS:
                return self._handle_write(request_data, device, address, function_code)
            
            elif function_code == FunctionCodeKey.READ_HOLDING_REGISTERS or function_code == FunctionCodeKey.READ_INPUT_REGISTERS:
                return self._handle_read(request_data, device, address, function_code)
            else:
                return 400, json.dumps({"error": "invalid function code"})
                
        except Exception as e:
            logger.error(f"Error in modbus handler: {str(e)}")
            return 500, json.dumps({"error": str(e)})

    def _handle_write(self, request_data: RequestData, device, address: int, function_code: FunctionCodeKey) -> Tuple[int, str]:
        """Handle write operations"""
        values = request_data.query_params.get(ModbusParameter.VALUES, None)
        if values is None:
            return 400, json.dumps({"error": "missing values parameter for write operation"})
            
        try:
            values_list = [int(value) for value in values.split(",")]
        except ValueError:
            return 400, json.dumps({"error": "invalid values format - must be comma-separated integers"})
            
        success = RegisterValue.write_multiple(device, address, values_list)
        
        ret = {
            "address": address,
            "success": success,
            "values": values_list
        }
        
        return 200, json.dumps(ret)

    def _handle_read(self, request_data: RequestData, device, address: int, function_code: FunctionCodeKey) -> Tuple[int, str]:
        """Handle read operations"""
        size: int = int(request_data.query_params.get(ModbusParameter.SIZE, 1))
        
        # Convert type string to enum
        raw_type = request_data.query_params.get(ModbusParameter.TYPE, DataTypeKey.U16)
        data_type: DataTypeKey = raw_type if isinstance(raw_type, DataTypeKey) else DataTypeKey(raw_type)
        
        # Convert endianness string to enum
        raw_endianness = request_data.query_params.get(ModbusParameter.ENDIANESS, EndiannessKey.BIG)
        endianness: EndiannessKey = raw_endianness if isinstance(raw_endianness, EndiannessKey) else EndiannessKey(raw_endianness)
        
        scale_factor: float = float(request_data.query_params.get(ModbusParameter.SCALE_FACTOR, 1.0))
        
        logger.debug(f"Reading - address: {address}, device_id: {device.get_SN()}, function_code: {function_code}, size: {size}, type: {data_type}, endianness: {endianness}")
        
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
