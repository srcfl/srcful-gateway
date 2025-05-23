from typing import Protocol
from ..profile_keys import FunctionCodeKey


class ModbusDevice(Protocol):
    def read_registers(self, function_code: FunctionCodeKey, address: int, size: int) -> list:
        ...

    def write_registers(self, address: int, values: list) -> bool:
        """Write values to holding registers
        Args:
            address: Starting register address
            values: List of values to write
        Returns:
            bool: True if write was successful
        """
        ...
