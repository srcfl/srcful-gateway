from ...profile_keys import (
    ProtocolKey,
    ProfileKey,
    RegistersKey,
    FunctionCodeKey,
    DeviceCategoryKey,
    DataTypeKey,
    EndiannessKey,
)
from ..profile import ModbusProfile
from ...common.types import ModbusDevice
from typing import List
from server.e_system.types import EBaseType
from server.devices.supported_devices.profile import RegisterInterval
from server.e_system.types import GridType, BatteryType, SolarType, LoadType, Current, Voltage, Power


class DeyeProfile(ModbusProfile):
    def __init__(self):
        super().__init__(deye_profile)

    def profile_is_valid(self, device: ModbusDevice) -> bool:
        return True

    def _get_esystem_data(self, device_sn: str, timestamp_ms: int, decoded_registers: List[RegisterInterval]) -> List[EBaseType]:

        esystem_data: List[EBaseType] = []

        L1_A = decoded_registers[610]
        L2_A = decoded_registers[611]
        L3_A = decoded_registers[612]
        L1_V = decoded_registers[598]
        L2_V = decoded_registers[599]
        L3_V = decoded_registers[600]

        grid_type = GridType(
            device_sn=device_sn,
            timestamp_ms=timestamp_ms,
            L1_A=Current(value=L1_A.decoded_value, unit=L1_A.unit),
            L2_A=Current(value=L2_A.decoded_value, unit=L2_A.unit),
            L3_A=Current(value=L3_A.decoded_value, unit=L3_A.unit),
            L1_V=Voltage(value=L1_V.decoded_value, unit=L1_V.unit),
            L2_V=Voltage(value=L2_V.decoded_value, unit=L2_V.unit),
            L3_V=Voltage(value=L3_V.decoded_value, unit=L3_V.unit),
        )

        BATT_P = decoded_registers[590]

        battery_type = BatteryType(
            device_sn=device_sn,
            timestamp_ms=timestamp_ms,
            power=Power(value=BATT_P.decoded_value, unit=BATT_P.unit),
        )

        PV_P_1 = decoded_registers[672]
        PV_P_2 = decoded_registers[673]
        PV_P_3 = decoded_registers[674]
        PV_P_4 = decoded_registers[675]

        solar_type = SolarType(
            device_sn=device_sn,
            timestamp_ms=timestamp_ms,
            power=Power(value=PV_P_1.decoded_value + PV_P_2.decoded_value + PV_P_3.decoded_value + PV_P_4.decoded_value, unit=PV_P_1.unit),
        )

        LOAD_P = decoded_registers[653]  # TODO: Incorrect, fix later

        load_type = LoadType(
            device_sn=device_sn,
            timestamp_ms=timestamp_ms,
            power=Power(value=LOAD_P.decoded_value, unit=LOAD_P.unit),
        )

        esystem_data.append(grid_type)
        esystem_data.append(battery_type)
        esystem_data.append(solar_type)
        esystem_data.append(load_type)

        return esystem_data


deye_profile = {
    ProfileKey.NAME: "deye",
    ProfileKey.MAKER: "Deye",
    ProfileKey.VERSION: "V1.1b3",
    ProfileKey.VERBOSE_ALWAYS: False,
    ProfileKey.DISPLAY_NAME: "Deye",
    ProfileKey.PROTOCOL: ProtocolKey.SOLARMAN,
    ProfileKey.DESCRIPTION: "Another inverter profile...",
    ProfileKey.SN: {
        RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
        RegistersKey.START_REGISTER: 3,
        RegistersKey.NUM_OF_REGISTERS: 8,
        RegistersKey.DATA_TYPE: DataTypeKey.STR,
        RegistersKey.UNIT: "",
        RegistersKey.DESCRIPTION: "Serial number",
        RegistersKey.SCALE_FACTOR: 1,
        RegistersKey.ENDIANNESS: EndiannessKey.BIG,
    },
    ProfileKey.ALWAYS_INCLUDE: [0],
    ProfileKey.REGISTERS_VERBOSE: [
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 0,
            RegistersKey.NUM_OF_REGISTERS: 125,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 125,
            RegistersKey.NUM_OF_REGISTERS: 125,
        },
        # {
        #     RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
        #     RegistersKey.START_REGISTER: 250,
        #     RegistersKey.NUM_OF_REGISTERS: 125,
        # },
        # {
        #     RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
        #     RegistersKey.START_REGISTER: 375,
        #     RegistersKey.NUM_OF_REGISTERS: 125,
        # },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 500,
            RegistersKey.NUM_OF_REGISTERS: 125,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 625,
            RegistersKey.NUM_OF_REGISTERS: 125,
        },
        # {
        #     RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
        #     RegistersKey.START_REGISTER: 750,
        #     RegistersKey.NUM_OF_REGISTERS: 51,
        # },
    ],
    ProfileKey.REGISTERS: [
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 609,
            RegistersKey.NUM_OF_REGISTERS: 1,
            RegistersKey.DATA_TYPE: DataTypeKey.U16,
            RegistersKey.UNIT: "Hz",
            RegistersKey.DESCRIPTION: "Grid frequency",
            RegistersKey.SCALE_FACTOR: 0.01,
            RegistersKey.ENDIANNESS: EndiannessKey.BIG,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 672,
            RegistersKey.NUM_OF_REGISTERS: 4,
            RegistersKey.DATA_TYPE: DataTypeKey.U16,
            RegistersKey.UNIT: "W",
            RegistersKey.DESCRIPTION: "DC Power",
            RegistersKey.SCALE_FACTOR: 1,
            RegistersKey.ENDIANNESS: EndiannessKey.BIG,
        },
    ],
    ProfileKey.KEYWORDS: ["deye", "high-flying"],
}
