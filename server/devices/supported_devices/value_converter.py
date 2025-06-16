from typing import Tuple, Optional, Union
from server.devices.profile_keys import DataTypeKey, EndiannessKey
from server.devices.supported_devices.profile import RegisterInterval
import struct
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def _to_byte_array(registers: list[int]) -> bytearray:
    raw = bytearray()

    if not registers:
        return raw

    for register in registers:
        raw.extend(register.to_bytes(2, "big"))

    return raw


def _interpret_value(register_interval: RegisterInterval) -> Tuple[bytearray, Optional[Union[int, float, str]]]:

    raw = _to_byte_array(registers)

    logger.debug(f"Interpreting value - DataType: {register_interval.data_type}, Raw: {raw.hex()}, ScaleFactor: {register_interval.scale_factor}")

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
        if len(raw) > 2 and register_interval.endianness == EndiannessKey.LITTLE:
            # For little-endian, we'll read the bytes in reverse register order
            # but keep bytes within each register in their original order
            registers = [raw[i:i+2] for i in range(0, len(raw), 2)]
            value_bytes = bytearray().join(registers[::-1])
        else:
            value_bytes = raw

        if register_interval.data_type == DataTypeKey.U16:
            value = int.from_bytes(value_bytes[0:2], "big", signed=False)
            return value_bytes, value * register_interval.scale_factor

        elif register_interval.data_type == DataTypeKey.I16:
            value = int.from_bytes(value_bytes[0:2], "big", signed=True)
            return value_bytes, value * register_interval.scale_factor

        elif register_interval.data_type == DataTypeKey.U32:
            value = int.from_bytes(value_bytes[0:4], "big", signed=False)
            return value_bytes, value * register_interval.scale_factor

        elif register_interval.data_type == DataTypeKey.I32:
            value = int.from_bytes(value_bytes[0:4], "big", signed=True)
            return value_bytes, value * register_interval.scale_factor

        elif register_interval.data_type == DataTypeKey.F32:
            value = struct.unpack(">f", value_bytes[0:4])[0]
            return value_bytes, value * register_interval.scale_factor

        elif register_interval.data_type == DataTypeKey.U64:
            value = int.from_bytes(value_bytes[0:8], "big", signed=False)
            return value_bytes, value * register_interval.scale_factor

        elif register_interval.data_type == DataTypeKey.I64:
            value = int.from_bytes(value_bytes[0:8], "big", signed=True)
            return value_bytes, value * register_interval.scale_factor

        elif register_interval.data_type == DataTypeKey.STR:
            # For strings, we just decode the bytes as they are
            # Register order swapping (if any) is already handled above
            return value_bytes, value_bytes.decode("ascii").rstrip('\x00')

        return raw, None

    except Exception as e:
        logger.error(f"Error interpreting value: {str(e)}")
        return raw, None
