from enum import Enum
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class State(Enum):
    NO_ACTION = "no_action"
    DISCHARGE_BATTERY = "discharge_battery"
    CHARGE_BATTERY = "charge_battery"
    OVER_LIMIT = "over_limit"


def _get_available_range(number, min_val, max_val):
    lower_distance = number - min_val
    upper_distance = max_val - number
    return lower_distance, upper_distance


def handle_fuse_limit(L1_A, L2_A, L3_A, L1_V, grid_current_limit, instantaneous_battery_power, battery_soc, battery_max_charge_discharge_power, min_battery_soc, max_battery_soc) -> tuple[int, State]:

    # This is how much we can decrease/increase the power with, best case with battery_max_charge_discharge_power * 2 if we are charging at max or discharging at max
    available_power_to_reduce_with, available_power_to_increase_with = _get_available_range(instantaneous_battery_power, -battery_max_charge_discharge_power, battery_max_charge_discharge_power)
    logger.info(f"Available power to reduce with: {available_power_to_reduce_with}, Available power to increase with: {available_power_to_increase_with}")

    max_current = max(L1_A, L2_A, L3_A)  # Max current in any phase
    min_current = min(L1_A, L2_A, L3_A)  # Min current in any phase

    # Over import limit (importing too much power from grid)
    if max_current > grid_current_limit:
        logger.info(f"Over import limit: {max_current} A > {grid_current_limit} A")
        if battery_soc < min_battery_soc:
            logger.info(f"Battery SoC is under min, we can't discharge to reduce import")
            return 0, State.NO_ACTION

        excess_current = (max_current - grid_current_limit) * 3
        power_excess = int(excess_current * L1_V)
        logger.info(f"Power excess: {power_excess} W")

        if available_power_to_reduce_with >= power_excess:
            new_battery_power_setpoint = instantaneous_battery_power - power_excess
            logger.info(f"Reducing import by discharging battery: {new_battery_power_setpoint} W from {instantaneous_battery_power} W, decrease by {power_excess} W")
            return new_battery_power_setpoint, State.DISCHARGE_BATTERY
        else:
            logger.info(f"Can't discharge enough, over limit by {power_excess - available_power_to_reduce_with} W, discharging at max power")
            return -battery_max_charge_discharge_power, State.DISCHARGE_BATTERY

    # Over export limit (exporting too much power to grid)
    elif min_current < -grid_current_limit:
        logger.info(f"Over export limit: {min_current} A < {-grid_current_limit} A")
        if battery_soc >= max_battery_soc:
            logger.info(f"Battery SoC is over max, we can't charge to reduce export")
            return 0, State.NO_ACTION

        excess_current = (-grid_current_limit - min_current) * 3  # How much we're over the export limit
        power_excess = int(excess_current * L1_V)
        logger.info(f"Power excess: {power_excess} W")

        if available_power_to_increase_with >= power_excess:
            new_battery_power_setpoint = instantaneous_battery_power + power_excess
            logger.info(f"Reducing export by charging battery: {new_battery_power_setpoint} W from {instantaneous_battery_power} W, increase by {power_excess} W")
            return new_battery_power_setpoint, State.CHARGE_BATTERY
        else:
            logger.info(f"Can't charge enough, over export limit by {power_excess - available_power_to_increase_with} W, charging at max power")
            return battery_max_charge_discharge_power, State.CHARGE_BATTERY

    else:
        # Within limits
        return 0, State.NO_ACTION
