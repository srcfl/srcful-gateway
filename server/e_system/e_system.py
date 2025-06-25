from typing import List, Tuple
from .types import EBaseType, EBatteryType, ESolarType, ELoadType, EGridType, EPower
from dataclasses import replace

class ESystem:
    """
    ESystem is a class that represents an energy system.
    It contains a list of batteries, solar panels, loads, and grid.
    This class is immutable and new instances are created when things are changed.
    """

    batteries:List[EBatteryType]
    solar:List[ESolarType]
    load:List[ELoadType]
    grid:List[EGridType]

    def __init__(self, battery_sns:List[str], solar_sns:List[str], load_sns:List[str], grid_sns:List[str], parts:List[EBaseType]):
        """
        Create a new ESystem instance.
        battery_sns, solar_sns, load_sns, grid_sns are the serial numbers of the batteries, solar panels, loads, and grid this esystem should contain.
        parts is a list of EBaseType objects.
        """

        # Store the serial numbers of the batteries, solar panels, loads, and grid as copies.
        self.battery_sn_list:List[str] = battery_sns.copy()
        self.solar_sn_list:List[str] = solar_sns.copy()
        self.load_sn_list:List[str] = load_sns.copy()
        self.grid_sn_list:List[str] = grid_sns.copy()

        self.batteries = []
        self.solar = []
        self.load = []
        self.grid = []

        for part in parts:
            self._add_part(part)

    def add_part(self, part:EBaseType) -> 'ESystem':
        return self.add_parts([part])

    def add_parts(self, parts:List[EBaseType]) -> 'ESystem':
        ret = ESystem(self.battery_sn_list, self.solar_sn_list, self.load_sn_list, self.grid_sn_list,
                      self.batteries + self.solar + self.load + self.grid + parts)
        return ret

    def _add_part(self, part:EBaseType):
        if isinstance(part, EBatteryType) and part.device_sn in self.battery_sn_list:
            self.batteries.append(part)
        elif isinstance(part, ESolarType) and part.device_sn in self.solar_sn_list:
            self.solar.append(part)
        elif isinstance(part, ELoadType) and part.device_sn in self.load_sn_list:
            self.load.append(part)
        elif isinstance(part, EGridType) and part.device_sn in self.grid_sn_list:
            self.grid.append(part)
        else:
            raise ValueError(f"Invalid part type: {type(part)}")

    def get_solar_power(self) -> EPower:
        return EPower(sum(solar.power.value for solar in self.solar))
    
    def get_battery_power(self) -> EPower:
        return EPower(sum(battery.power.value for battery in self.batteries))
    
    def get_load_power(self) -> EPower:
        return EPower(sum(load.power.value for load in self.load))
    
    def get_grid_power(self) -> EPower:
        return EPower(sum(grid.total_power().value for grid in self.grid))
    
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
        # 0 = solar + load + battery -> battery = -solar - load
        # TODO: this is limited to one battery for now.
        new_battery_power = -self.get_solar_power().value - self.get_load_power().value
        new_battery = replace(self.batteries[0], power=EPower(new_battery_power))
        return ESystem(self.battery_sn_list, self.solar_sn_list, self.load_sn_list, self.grid_sn_list, [new_battery])
