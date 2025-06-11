from abc import abstractmethod
from typing import List
import logging

logger = logging.getLogger(__name__)


class DeeController:
    def init():
        pass

    def deinit():
        pass


class DeeDecoder:
    def __init__(self):
        pass

    @abstractmethod
    def decode(self, harvest_data: dict) -> List[dict]:
        pass


class SungrowDeeDecoder(DeeDecoder):
    def __init__(self):
        self.grid_power = 0  # check
        self.grid_power_limit = 3000  # check
        self.instantaneous_battery_power = 0  # check
        self.battery_soc = 0  # check
        self.battery_max_charge_discharge_power = 5000  # check
        self.min_battery_soc = 5  # check
        self.max_battery_soc = 100  # check

    def decode(self, harvest_data: dict) -> List[dict]:

        logger.info(harvest_data)
        # Extract Grid Frequency from register 5035 (U16, little-endian)
        # Extract Total DC Power from registers 5016-5017 (U32, little-endian)
        # Register 5016: lower 16 bits, Register 5017: upper 16 bits
        lower_bits = harvest_data.get(5016, 0)
        upper_bits = harvest_data.get(5017, 0)

        # Combine into U32 value (little-endian: upper << 16 | lower)
        solar_power = (upper_bits << 16) | lower_bits

        # Extract Total Active Power from registers 13033-13034 (I32, little-endian)
        # Register 13033: lower 16 bits, Register 13034: upper 16 bits
        meter_lower = harvest_data.get(13009, 0)
        meter_upper = harvest_data.get(13010, 0)

        # Combine into I32 value (little-endian: upper << 16 | lower)
        meter_power_raw = (meter_upper << 16) | meter_lower

        # Convert to signed 32-bit integer
        if meter_power_raw > 0x7FFFFFFF:
            meter_power = meter_power_raw - 0x100000000
        else:
            meter_power = meter_power_raw

        self.grid_power = -meter_power  # sungrow meter is negative when importing...

        # Assign production/consumption based on sign
        # Positive = production (feeding back to grid), Positive = consumption (drawing from grid)
        if meter_power > 0:
            production = abs(meter_power)
            consumption = 0
        else:
            production = 0
            consumption = meter_power

        # Extract Battery Power from register 13021 (U16, big-endian)
        battery_power_raw = harvest_data.get(13021, 0)

        # Extract Running State from register 13000 to determine charge/discharge direction
        running_state = harvest_data.get(13000, 0)

        # Check bit flags for battery state
        is_charging = (running_state & 0x01) != 0      # bit 1
        is_discharging = (running_state & 0x02) != 0   # bit 2

        # Apply sign based on charge/discharge state
        if is_discharging:
            battery_power = battery_power_raw  # Positive when discharging (power flowing out)
        elif is_charging:
            battery_power = -battery_power_raw  # Negative when charging (power flowing in)
        else:
            battery_power = 0  # No activity
        self.instantaneous_battery_power = battery_power

        self.battery_soc = harvest_data.get(13022, 0) * 0.1

        meter = {
            "production": production,
            "consumption": consumption,
        }

        battery = {
            "power": battery_power,
        }

        solar = {
            "power": solar_power,
        }

        return [{"meter": meter}, {"battery": battery}, {"solar": solar}]
