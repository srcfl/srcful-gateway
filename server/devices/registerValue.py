import struct
from enum import Enum
from typing import Tuple, Optional, Union
from .profile_keys import DataType
from .inverters.modbus import Modbus
import logging

logger = logging.getLogger(__name__)

class RegisterValue:
    def __init__(
        self,
        address: int,
        size: int,
        function_code: int,
        data_type: DataType,
        scale_factor: float = 1.0,
    ):
        self.address = address
        self.size = size
        self.data_type = data_type
        self.function_code = function_code
        self.scale_factor = scale_factor

    def read_value(self, device: Modbus) -> Tuple[bytearray, Optional[Union[int, float, str]]]:
        """Reads and interprets register value from device"""
        # Read using the specified function code
        registers = device.read_registers(self.function_code, self.address, self.size)

        # Convert registers to bytearray
        raw = bytearray()
        for register in registers:
            raw.extend(register.to_bytes(2, "big"))

        value = self._interpret_value(raw)
        if value is not None and not isinstance(value, str):  # Only apply scale factor to numeric values
            value *= self.scale_factor
            
        return raw, value

    def _interpret_value(self, raw: bytearray) -> Optional[Union[int, float, str]]:
        """Interprets raw bytes according to data type"""
        try:
            if self.data_type == DataType.U16:
                return int.from_bytes(raw[0:2], "big", signed=False)
            
            elif self.data_type == DataType.I16:
                return int.from_bytes(raw[0:2], "big", signed=True)
            
            elif self.data_type == DataType.U32:
                return int.from_bytes(raw[0:4], "big", signed=False)
            
            elif self.data_type == DataType.I32:
                return int.from_bytes(raw[0:4], "big", signed=True)
            
            elif self.data_type == DataType.F32:
                # For F32, we need to keep the original byte order
                # Most Modbus devices use ABCD order for floats
                return struct.unpack(">f", raw[0:4])[0]
            
            elif self.data_type == DataType.STR:
                return raw.decode("ascii").strip('\x00')
            
        except Exception as e:
            logger.error(f"Error interpreting value: {str(e)}")
            return None
        
    def __str__(self):
        return f"RegisterValue(address={self.address}, size={self.size}, function_code={self.function_code}, data_type={self.data_type}, scale_factor={self.scale_factor})"
