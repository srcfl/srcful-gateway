# a class for interpreting a modbus register as a higher level datatype

import struct
from enum import Enum
from .inverters.modbus import Modbus


class RegisterValue:
    class RegisterType(Enum):
        HOLDING = "holding"
        INPUT = "input"

        @classmethod
        def from_str(cls, string):
            if string == "holding":
                return cls.HOLDING
            elif string == "input":
                return cls.INPUT
            else:
                raise Exception("Unsupported register type " + string)

    class Endianness(Enum):
        BIG = "big"
        LITTLE = "little"

        @classmethod
        def from_str(cls, string):
            if string == "big" or string == "be" or string == ">":
                return cls.BIG
            elif string == "little" or string == "le" or string == "<":
                return cls.LITTLE
            else:
                raise Exception("Unsupported endianess " + string)

    class Type(Enum):
        UINT = "uint"
        INT = "int"
        FLOAT = "float"
        ASCII = "ascii"
        UTF16 = "utf16"
        NONE = "none"

        @classmethod
        def from_str(cls, string):
            if string == "uint":
                return cls.UINT
            elif string == "int":
                return cls.INT
            elif string == "float":
                return cls.FLOAT
            elif string == "ascii":
                return cls.ASCII
            elif string == "utf16":
                return cls.UTF16
            elif string == "none" or string == "raw" or string == "":
                return cls.NONE
            else:
                raise Exception("Unsupported datatype " + string)

    def __init__(
        self,
        address,
        size,
        register_type: RegisterType,
        datatype: Type,
        endianness: Endianness,
    ):
        self.address = address
        self.size = size
        self.datatype = datatype
        self.endianness = endianness
        self.regType = register_type
    
    def _swap_words(self, data: bytearray) -> bytearray:
        """Swaps the two words in a 32-bit float value"""
        return data[2:4] + data[0:2]

    def read_value(self, inverter: Modbus):
        """Reads the value of the register from the inverter"""
        if self.regType == RegisterValue.RegisterType.HOLDING:
            registers = inverter.read_registers(0x03, self.address, self.size)
        elif self.regType == RegisterValue.RegisterType.INPUT:
            registers = inverter.read_registers(0x04, self.address, self.size)

        # currently we convert the raw values that are word based to bytearray
        self.raw = bytearray()
        for register in registers:
            byte_arr = register.to_bytes(2, "big")
            self.raw.extend(byte_arr)

        if self.datatype != RegisterValue.Type.NONE:
            return self.raw, self.get_value(self.raw)
        return self.raw, None

    def get_value(self, raw: bytearray):
        """Converts a list of bytes to a value based on the datatype and endianness of the register"""
        value = None
        endianness = self.endianness

        if self.datatype == RegisterValue.Type.UINT:
            value = int.from_bytes(raw, byteorder=endianness.value, signed=False)
        elif self.datatype == RegisterValue.Type.INT:
            value = int.from_bytes(raw, byteorder=endianness.value, signed=True)
        elif self.datatype == RegisterValue.Type.FLOAT:
            if endianness == RegisterValue.Endianness.BIG:
                endianness = ">"
            else:
                endianness = "<"
                
            raw = self._swap_words(raw)
            value = struct.unpack(f"{endianness}f", raw)[0]

        elif self.datatype == RegisterValue.Type.ASCII:
            value = raw.decode("ascii")
        elif self.datatype == RegisterValue.Type.UTF16:
            value = raw.decode("utf-16" + ("be" if endianness.value == "big" else "le"))
        else:
            raise Exception("Unsupported datatype " + self.datatype.value)

        return value
