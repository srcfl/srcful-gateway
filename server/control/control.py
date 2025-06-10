from enum import Enum

debug = True


def log(message):
    if debug:
        print(message)


class State(Enum):
    NO_ACTION = "no_action"
    DISCHARGE_BATTERY = "discharge_battery"
    CHARGE_BATTERY = "charge_battery"
    OVER_LIMIT = "over_limit"


def _get_distances(number, min_val, max_val):
    lower_distance = number - min_val
    upper_distance = max_val - number
    return lower_distance, upper_distance


def check_import_export_limits(grid_power, grid_power_limit, instantaneous_battery_power, battery_soc, battery_max_charge_discharge_power, min_battery_soc, max_battery_soc) -> tuple[int, State]:

    # This is how much we can decrease/increase the power with, best case with battery_max_charge_discharge_power * 2 if we are charging at max or discharging at max
    available_power_to_reduce_with, available_power_to_increase_with = _get_distances(instantaneous_battery_power, -battery_max_charge_discharge_power, battery_max_charge_discharge_power)
    log(f"Available power to reduce with: {available_power_to_reduce_with}, Available power to increase with: {available_power_to_increase_with}")

    # Over import limit (importing too much power from grid)
    if grid_power > grid_power_limit:
        if battery_soc < min_battery_soc:
            log(f"Battery SoC is under min, we can't discharge to reduce import")
            return 0, State.NO_ACTION

        power_excess = grid_power - grid_power_limit
        if available_power_to_reduce_with >= power_excess:
            new_battery_power_setpoint = instantaneous_battery_power - power_excess
            log(f"Reducing import by discharging battery: {new_battery_power_setpoint} W from {instantaneous_battery_power} W, decrease by {power_excess} W")
            return new_battery_power_setpoint, State.DISCHARGE_BATTERY
        else:
            log(f"Can't discharge enough, over limit by {power_excess - available_power_to_reduce_with} W, discharging at max power")
            return battery_max_charge_discharge_power, State.DISCHARGE_BATTERY

    # Over export limit (exporting too much power to grid)
    elif grid_power < -grid_power_limit:
        if battery_soc >= max_battery_soc:
            log(f"Battery SoC is over max, we can't charge to reduce export")
            return 0, State.NO_ACTION

        power_excess = -grid_power_limit - grid_power  # How much we're over the export limit
        if available_power_to_increase_with >= power_excess:
            new_battery_power_setpoint = instantaneous_battery_power + power_excess
            log(f"Reducing export by charging battery: {new_battery_power_setpoint} W from {instantaneous_battery_power} W, increase by {power_excess} W")
            return new_battery_power_setpoint, State.CHARGE_BATTERY
        else:
            log(f"Can't charge enough, over export limit by {power_excess - available_power_to_increase_with} W, charging at max power")
            return -battery_max_charge_discharge_power, State.CHARGE_BATTERY

    # Within limits
    else:
        return 0, State.NO_ACTION
