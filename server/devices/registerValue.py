import struct
from typing import Tuple, Optional, Union
from .profile_keys import DataTypeKey, FunctionCodeKey, EndiannessKey
from .common.types import ModbusProtocol
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class RegisterValue:
    def __init__(
        self,
        address: int,
        size: int = 1,
        function_code: FunctionCodeKey = FunctionCodeKey.READ_INPUT_REGISTERS,
        data_type: DataTypeKey = DataTypeKey.U16,
        scale_factor: float = 1.0,
        endianness: EndiannessKey = EndiannessKey.BIG,
    ):
        self.address: int = address
        self.size: int = size
        self.data_type: DataTypeKey = data_type
        self.function_code: FunctionCodeKey = function_code
        self.scale_factor: float = scale_factor
        self.endianness: EndiannessKey = endianness
        
    def read_value(self, device: ModbusProtocol) -> Tuple[bytearray, bytearray, Optional[Union[int, float, str]]]:
        """Reads and interprets register value from device
        Returns:
            Tuple containing:
            - raw_bytes: Original bytes as they are in memory
            - swapped_bytes: Bytes after endianness swapping
            - value: Interpreted value
        """
        # Read using the specified function code
        registers = device.read_registers(self.function_code, self.address, self.size)
        
        raw = bytearray()
        
        if not registers:
            return raw, raw, None

        # Create raw bytes in original order
        for register in registers:
            raw.extend(register.to_bytes(2, "big"))

        # Get swapped bytes and interpreted value
        swapped, value = self._interpret_value(raw)
        return raw, swapped, value

    def write_value(self, device: ModbusProtocol, value: Union[int, float, str]) -> bool:
        """Writes a value to the device's registers
        Args:
            device: The Modbus device to write to
            value: The value to write (will be converted based on data_type)
        Returns:
            bool: True if write was successful, False otherwise
        """
        try:
            # Scale the value before converting to bytes (inverse of read scaling)
            if isinstance(value, (int, float)):
                value = value / self.scale_factor

            # Convert the value to bytes
            value_bytes = self._value_to_bytes(value)
            
            # Split into 16-bit registers
            registers = []
            for i in range(0, len(value_bytes), 2):
                register_bytes = value_bytes[i:i+2]
                registers.append(int.from_bytes(register_bytes, "big"))

            # Write the registers
            if hasattr(device, 'write_registers'):
                return device.write_registers(self.address, registers)
            else:
                logger.error("Device does not support writing registers")
                return False

        except Exception as e:
            logger.error(f"Error writing value: {str(e)}")
            return False

    def _value_to_bytes(self, value: Union[int, float, str]) -> bytearray:
        """Converts a value to its byte representation based on data type
        Args:
            value: The value to convert
        Returns:
            bytearray: The byte representation of the value
        """
        try:
            if self.data_type == DataTypeKey.U16:
                return bytearray(int(value).to_bytes(2, "big", signed=False))
            
            elif self.data_type == DataTypeKey.I16:
                return bytearray(int(value).to_bytes(2, "big", signed=True))
            
            elif self.data_type == DataTypeKey.U32:
                value_bytes = bytearray(int(value).to_bytes(4, "big", signed=False))
                
            elif self.data_type == DataTypeKey.I32:
                value_bytes = bytearray(int(value).to_bytes(4, "big", signed=True))
                
            elif self.data_type == DataTypeKey.F32:
                value_bytes = bytearray(struct.pack(">f", float(value)))
                
            elif self.data_type == DataTypeKey.STR:
                # Pad string to fill registers
                padded = str(value).ljust(self.size * 2, '\x00')
                value_bytes = bytearray(padded.encode('ascii'))
            else:
                raise ValueError(f"Unsupported data type: {self.data_type}")

            # For multi-register values, handle endianness
            if len(value_bytes) > 2 and self.endianness == EndiannessKey.LITTLE:
                # Split into registers and reverse their order
                registers = [value_bytes[i:i+2] for i in range(0, len(value_bytes), 2)]
                value_bytes = bytearray().join(registers[::-1])
                
            return value_bytes

        except Exception as e:
            logger.error(f"Error converting value to bytes: {str(e)}")
            raise

    def _interpret_value(self, raw: bytearray) -> Tuple[bytearray, Optional[Union[int, float, str]]]:
        """Interprets raw bytes according to data type
        Returns:
            Tuple containing:
            - swapped_bytes: Bytes after endianness swapping
            - value: Interpreted value
        """
        logger.debug(f"Interpreting value - DataType: {self.data_type}, Raw: {raw.hex()}, ScaleFactor: {self.scale_factor}")
        
        try:
            # Handle register pair endianness (if applicable)
            # Example for a 32-bit value (2 registers, 4 bytes total):
            # Original bytes: [0x12][0x34][0x56][0x78]
            # Register 1: [0x12][0x34]
            # Register 2: [0x56][0x78]
            #
            # Big Endian (default): [R1][R2] = [0x12][0x34][0x56][0x78] = 0x12345678
            # Little Endian:        [R2][R1] = [0x56][0x78][0x12][0x34] = 0x56781234
            #
            # Note: Bytes within each register stay in big-endian order
            # as per Modbus specification. We only swap the register order,
            # not the bytes within registers.
            
            # For multi-register values, we need to:
            # 1. Keep the raw bytes as they are for big-endian
            # 2. For little-endian, interpret the value by swapping register order
            value_bytes = raw
            if len(raw) > 2 and self.endianness == EndiannessKey.LITTLE:
                # For little-endian, we'll read the bytes in reverse register order
                # but keep bytes within each register in their original order
                registers = [raw[i:i+2] for i in range(0, len(raw), 2)]
                value_bytes = bytearray().join(registers[::-1])
            else:
                value_bytes = raw

            if self.data_type == DataTypeKey.U16:
                value = int.from_bytes(value_bytes[0:2], "big", signed=False)
                return value_bytes, value * self.scale_factor
            
            elif self.data_type == DataTypeKey.I16:
                value = int.from_bytes(value_bytes[0:2], "big", signed=True)
                return value_bytes, value * self.scale_factor
            
            elif self.data_type == DataTypeKey.U32:
                value = int.from_bytes(value_bytes[0:4], "big", signed=False)
                return value_bytes, value * self.scale_factor
            
            elif self.data_type == DataTypeKey.I32:
                value = int.from_bytes(value_bytes[0:4], "big", signed=True)
                return value_bytes, value * self.scale_factor
            
            elif self.data_type == DataTypeKey.F32:
                value = struct.unpack(">f", value_bytes[0:4])[0]
                return value_bytes, value * self.scale_factor
            
            elif self.data_type == DataTypeKey.STR:
                # For strings, we just decode the bytes as they are
                # Register order swapping (if any) is already handled above
                return value_bytes, value_bytes.decode("ascii").rstrip('\x00')
            
            return raw, None
            
        except Exception as e:
            logger.error(f"Error interpreting value: {str(e)}")
            return raw, None
        
    def __str__(self):
        return f"RegisterValue(address={self.address}, size={self.size}, function_code={self.function_code}, data_type={self.data_type}, scale_factor={self.scale_factor})"
