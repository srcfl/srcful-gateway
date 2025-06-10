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


def handle_import(net_power, grid_import_power_limit, instantaneous_battery_power, battery_soc, battery_max_charge_discharge_power, min_battery_soc) -> tuple[int, State]:
    if battery_soc < min_battery_soc:
        log("Battery is too low, we can't do anything")
        return 0, State.NO_ACTION

    log(f"Net power: {net_power} W, Grid import power limit: {grid_import_power_limit} W, Instantaneous battery power: {instantaneous_battery_power} W, Battery SOC: {battery_soc}%")

    # We are over importing power from the grid, so let's check if we can discharge the battery
    available_power_to_reduce_with, _ = _get_distances(instantaneous_battery_power, -battery_max_charge_discharge_power, battery_max_charge_discharge_power)  # This is how much we can decrease the power with, best case with max_charge_discharge_power * 2 if we are charging at max
    log(f"We can reduce the total load by: {available_power_to_reduce_with} W")

    if available_power_to_reduce_with >= (net_power - grid_import_power_limit):
        new_battery_power_setpoint = instantaneous_battery_power - (net_power - grid_import_power_limit)

        if new_battery_power_setpoint == instantaneous_battery_power:
            return 0, State.NO_ACTION
        else:
            log(f"We can save the fuze by setting new battery power to {new_battery_power_setpoint} W from {instantaneous_battery_power} W, decrease battery power by {net_power - grid_import_power_limit} W")
            return new_battery_power_setpoint, State.DISCHARGE_BATTERY
    else:
        log(f"We can't discharge the battery, we are over limit by {net_power - grid_import_power_limit - available_power_to_reduce_with} W, but we will discharge at max power anyway")
        return battery_max_charge_discharge_power, State.OVER_LIMIT


def handle_limits(net_power, grid_import_power_limit, grid_export_power_limit, instantaneous_battery_power, battery_soc, battery_max_charge_discharge_power, min_battery_soc, max_battery_soc) -> tuple[int, State]:
    if net_power > grid_import_power_limit:
        return handle_import(net_power, grid_import_power_limit, instantaneous_battery_power, battery_soc, battery_max_charge_discharge_power, min_battery_soc)
    else:
        return 0, State.NO_ACTION
