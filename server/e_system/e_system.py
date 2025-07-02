from enum import Enum
from typing import List, Tuple

from server.devices.ICom import ICom
from .types import EBaseType, EBatteryType, ESolarType, ELoadType, EGridType, EPower
from dataclasses import replace



class ESystemState(Enum):
    SELF_CONSUMPTION = "self-consumption"
    STOP = "stop"


class ESystemTemplate:
    """
    ESystemTemplate is a class that represents a template for an energy system.
    It contains lists of device serial numbers from wich the batteries, solar panels, loads, and grid type objects will be created.
    This class is immutable and new instances are created when things are changed.
    """

    _battery_sn_list: List[str]
    _solar_sn_list: List[str]
    _load_sn_list: List[str]
    _grid_sn_list: List[str]

    _state: ESystemState

    def __init__(self):
        self._battery_sn_list = []
        self._solar_sn_list = []
        self._load_sn_list = []
        self._grid_sn_list = []
        self._state = ESystemState.STOP

    @property
    def state(self) -> ESystemState:
        return self._state
    
    def set_state(self, state: ESystemState):
        self._state = state

    def sn_list(self) -> List[str]:
        # return a list of unique serial numbers
        return [sn for sn in set(self._battery_sn_list + self._solar_sn_list + self._load_sn_list + self._grid_sn_list)]

    @property
    def battery_sn_list(self) -> List[str]:
        return self._battery_sn_list
    
    @property
    def solar_sn_list(self) -> List[str]:
        return self._solar_sn_list  
    
    @property
    def load_sn_list(self) -> List[str]:
        return self._load_sn_list
    
    @property
    def grid_sn_list(self) -> List[str]:
        return self._grid_sn_list
    
    def add_battery_sn(self, device:ICom) -> bool:
        if EBatteryType in [type(part) for part in device.get_esystem_data()]:
            self._battery_sn_list.append(device.get_SN())
            return True
        return False
    
    def add_solar_sn(self, device:ICom) -> bool:
        if ESolarType in [type(part) for part in device.get_esystem_data()]:
            self._solar_sn_list.append(device.get_SN())
            return True
        return False
    
    def add_load_sn(self, device:ICom) -> bool:
        if ELoadType in [type(part) for part in device.get_esystem_data()]:
            self._load_sn_list.append(device.get_SN())
            return True
        return False
    
    def add_grid_sn(self, device:ICom) -> bool:
        if EGridType in [type(part) for part in device.get_esystem_data()]:
            self._grid_sn_list.append(device.get_SN())
            return True
        return False

class ESystem:
    """
    ESystem is a class that represents an energy system.
    It contains a list of batteries, solar panels, loads, and grid.
    This class is immutable and new instances are created when things are changed.
    """

    batteries: List[EBatteryType]
    solar: List[ESolarType]
    load: List[ELoadType]
    grid: List[EGridType]

    def __init__(self, template: ESystemTemplate, parts: List[EBaseType]):
        """
        Create a new ESystem instance.
        battery_sns, solar_sns, load_sns, grid_sns are the serial numbers of the batteries, solar panels, loads, and grid this esystem should contain.
        parts is a list of EBaseType objects.
        """

        # Store the serial numbers of the batteries, solar panels, loads, and grid as copies.
        self.template = template

        self.batteries = []
        self.solar = []
        self.load = []
        self.grid = []

        for part in parts:
            self._add_part(part)

    def add_part(self, part: EBaseType) -> 'ESystem':
        return self.add_parts([part])

    def add_parts(self, parts: List[EBaseType]) -> 'ESystem':
        ret = ESystem(self.template, self.batteries + self.solar + self.load + self.grid + parts)
        return ret

    def _add_part(self, part: EBaseType):
        if isinstance(part, EBatteryType) and part.device_sn in self.template.battery_sn_list:
            self.batteries.append(part)
        elif isinstance(part, ESolarType) and part.device_sn in self.template.solar_sn_list:
            self.solar.append(part)
        elif isinstance(part, ELoadType) and part.device_sn in self.template.load_sn_list:
            self.load.append(part)
        elif isinstance(part, EGridType) and part.device_sn in self.template.grid_sn_list:
            self.grid.append(part)
        else:
            raise ValueError(f"Invalid part type: {type(part)}")

    def get_solar_power(self) -> EPower:
        return EPower(value=sum(solar.power.value for solar in self.solar))

    def get_battery_power(self) -> EPower:
        return EPower(value=sum(battery.power.value for battery in self.batteries))

    def get_load_power(self) -> EPower:
        return EPower(value=sum(load.power.value for load in self.load))

    def get_grid_power(self) -> EPower:
        return EPower(value=sum(grid.total_power().value for grid in self.grid))

    def get_oldest_timestamp(self) -> int:
        return min(part.timestamp_ms for part in self.batteries + self.solar + self.load + self.grid)

    def get_newest_timestamp(self) -> int:
        return max(part.timestamp_ms for part in self.batteries + self.solar + self.load + self.grid)

    def get_timestamp_range(self) -> Tuple[int, int]:
        return self.get_oldest_timestamp(), self.get_newest_timestamp()

    def self_consumption_battery(self) -> 'ESystem':
        '''
            Solve the power balance using batteries only, try to get the grid power to 0.
            Return a new ESystem with the new battery power.
        '''

        if len(self.batteries) == 0:
            raise ValueError("No batteries found in ESystem")
        if len(self.batteries) > 1:
            raise ValueError("Multiple batteries found in ESystem, not supported yet")

        # 0 = solar + load + battery -> battery = -solar - load
        # TODO: this is limited to one battery for now. For multiple batteries we would need to know the state of charge of each battery and do some balancing there
        new_battery_power = -self.get_solar_power().value - self.get_load_power().value
        new_battery = replace(self.batteries[0], power=EPower(value=new_battery_power))
        return ESystem(self.template, self.solar + self.load + self.grid + [new_battery])

    def get_esystem_data(self) -> List[EBaseType]:
        return list(self.batteries) + list(self.solar) + list(self.load) + list(self.grid)  # explicit list to avoid type errors