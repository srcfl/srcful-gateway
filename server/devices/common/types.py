from typing import Protocol
from ..profile_keys import FunctionCodeKey

class ModbusProtocol(Protocol):
    def read_registers(self, function_code: FunctionCodeKey, address: int, size: int) -> list:
        ...