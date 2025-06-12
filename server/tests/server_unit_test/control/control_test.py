from server.control.control import check_import_export_limits, State

########################################################################################
# Import tests
########################################################################################


def test_handle_import_when_max_charging():
    """Test when battery is max charging and grid power is 10kW over 10kW limit"""
    grid_power = 20000
    instantaneous_battery_power = 5000

    # Grid
    grid_power_limit = 10000

    # Battery
    battery_soc = 6  # 0-100%
    battery_max_charge_discharge_power = 5000
    min_battery_soc = 5
    max_battery_soc = 100

    battery_power, state = check_import_export_limits(grid_power,
                                                      grid_power_limit,
                                                      instantaneous_battery_power,
                                                      battery_soc,
                                                      battery_max_charge_discharge_power,
                                                      min_battery_soc,
                                                      max_battery_soc)
    print(f"Power: {battery_power}, State: {state}")
    assert battery_power == -5000  # discharge at max power
    assert state == State.DISCHARGE_BATTERY


def test_handle_import_when_max_discharging():
    """Test when battery is max discharging and grid power is exactly at 10kW limit"""
    grid_power = 10000
    instantaneous_battery_power = -5000

    # Grid
    grid_power_limit = 10000

    # Battery
    battery_soc = 6  # 0-100%
    battery_max_charge_discharge_power = 5000
    min_battery_soc = 5
    max_battery_soc = 100

    battery_power, state = check_import_export_limits(grid_power, grid_power_limit, instantaneous_battery_power, battery_soc, battery_max_charge_discharge_power, min_battery_soc, max_battery_soc)
    print(f"Power: {battery_power}, State: {state}")
    assert battery_power == 0  # No need to do anything
    assert state == State.NO_ACTION


def test_handle_import_when_over_limit():
    """Test when grid power is 5001W over 10kW limit with neutral battery"""
    grid_power = 15001
    instantaneous_battery_power = 0

    # Grid
    grid_power_limit = 10000

    # Battery
    battery_soc = 6  # 0-100%
    battery_max_charge_discharge_power = 5000
    min_battery_soc = 5
    max_battery_soc = 100

    battery_power, state = check_import_export_limits(grid_power, grid_power_limit, instantaneous_battery_power, battery_soc, battery_max_charge_discharge_power, min_battery_soc, max_battery_soc)
    print(f"Power: {battery_power}, State: {state}")
    assert battery_power == 5000
    assert state == State.DISCHARGE_BATTERY


def test_handle_import_when_at_limit():
    """Test when grid power is exactly at 10kW limit with neutral battery"""
    grid_power = 10000
    instantaneous_battery_power = 0

    # Grid
    grid_power_limit = 10000

    # Battery
    battery_soc = 6  # 0-100%
    battery_max_charge_discharge_power = 5000
    min_battery_soc = 5
    max_battery_soc = 100

    battery_power, state = check_import_export_limits(grid_power, grid_power_limit, instantaneous_battery_power, battery_soc, battery_max_charge_discharge_power, min_battery_soc, max_battery_soc)
    print(f"Power: {battery_power}, State: {state}")
    assert battery_power == 0
    assert state == State.NO_ACTION


def test_handle_import_battery_soc_too_low():
    """Test when grid power is over limit but battery SOC is below minimum threshold"""
    grid_power = 15000
    instantaneous_battery_power = 0

    # Grid
    grid_power_limit = 10000

    # Battery
    battery_soc = 4  # Below min_battery_soc
    battery_max_charge_discharge_power = 5000
    min_battery_soc = 5
    max_battery_soc = 100

    battery_power, state = check_import_export_limits(grid_power, grid_power_limit, instantaneous_battery_power, battery_soc, battery_max_charge_discharge_power, min_battery_soc, max_battery_soc)
    print(f"Power: {battery_power}, State: {state}")
    assert battery_power == 0
    assert state == State.NO_ACTION


def test_handle_import_partial_discharge_needed():
    """Test when grid power is 3kW over 10kW limit and battery is charging 1kW"""
    grid_power = 13000
    instantaneous_battery_power = 1000  # Currently charging at 1kW

    # Grid
    grid_power_limit = 10000

    # Battery
    battery_soc = 50  # Good SOC level
    battery_max_charge_discharge_power = 5000
    min_battery_soc = 5
    max_battery_soc = 100

    battery_power, state = check_import_export_limits(grid_power, grid_power_limit, instantaneous_battery_power, battery_soc, battery_max_charge_discharge_power, min_battery_soc, max_battery_soc)
    print(f"Power: {battery_power}, State: {state}")
    assert battery_power == -2000
    assert state == State.DISCHARGE_BATTERY


def test_handle_import_exact_power_match():
    """Test when grid power is exactly at 10kW limit with neutral battery"""
    grid_power = 10000
    instantaneous_battery_power = 0  # Neutral battery state

    # Grid
    grid_power_limit = 10000

    # Battery
    battery_soc = 50
    battery_max_charge_discharge_power = 5000
    min_battery_soc = 5
    max_battery_soc = 100

    battery_power, state = check_import_export_limits(grid_power, grid_power_limit, instantaneous_battery_power, battery_soc, battery_max_charge_discharge_power, min_battery_soc, max_battery_soc)
    print(f"Power: {battery_power}, State: {state}")
    assert battery_power == 0
    assert state == State.NO_ACTION


def test_handle_import_small_adjustment_needed():
    """Test when grid power is 500W over 10kW limit with neutral battery"""
    grid_power = 10500
    instantaneous_battery_power = 0

    # Grid
    grid_power_limit = 10000

    # Battery
    battery_soc = 30
    battery_max_charge_discharge_power = 5000
    min_battery_soc = 5
    max_battery_soc = 100

    battery_power, state = check_import_export_limits(grid_power, grid_power_limit, instantaneous_battery_power, battery_soc, battery_max_charge_discharge_power, min_battery_soc, max_battery_soc)
    print(f"Power: {battery_power}, State: {state}")
    assert battery_power == -500
    assert state == State.DISCHARGE_BATTERY


def test_handle_import_when_already_optimal():
    """Test when grid power is at 10kW limit and battery is already discharging"""
    grid_power = 10000
    instantaneous_battery_power = -2000  # Already discharging

    # Grid
    grid_power_limit = 10000

    # Battery
    battery_soc = 50
    battery_max_charge_discharge_power = 5000
    min_battery_soc = 5
    max_battery_soc = 100

    battery_power, state = check_import_export_limits(grid_power, grid_power_limit, instantaneous_battery_power, battery_soc, battery_max_charge_discharge_power, min_battery_soc, max_battery_soc)
    print(f"Power: {battery_power}, State: {state}")
    assert battery_power == 0
    assert state == State.NO_ACTION


def test_handle_import_moderate_charging_state():
    """Test when grid power is 5kW over 10kW limit and battery is charging 2kW"""
    grid_power = 15000
    instantaneous_battery_power = 2000  # Charging at 2kW

    # Grid
    grid_power_limit = 10000

    # Battery
    battery_soc = 40
    battery_max_charge_discharge_power = 5000
    min_battery_soc = 5
    max_battery_soc = 100

    battery_power, state = check_import_export_limits(grid_power, grid_power_limit, instantaneous_battery_power, battery_soc, battery_max_charge_discharge_power, min_battery_soc, max_battery_soc)
    print(f"Power: {battery_power}, State: {state}")
    assert battery_power == -3000
    assert state == State.DISCHARGE_BATTERY


def test_handle_import_with_pv_generation():
    """Test when grid power is 3kW over 10kW limit with battery charging 1kW"""
    grid_power = 13000
    instantaneous_battery_power = 1000

    # Grid
    grid_power_limit = 10000

    # Battery
    battery_soc = 60
    battery_max_charge_discharge_power = 5000
    min_battery_soc = 5
    max_battery_soc = 100

    battery_power, state = check_import_export_limits(grid_power, grid_power_limit, instantaneous_battery_power, battery_soc, battery_max_charge_discharge_power, min_battery_soc, max_battery_soc)
    print(f"Power: {battery_power}, State: {state}")
    assert state == State.DISCHARGE_BATTERY


def test_handle_export_at_limit():
    """Test when grid power is exactly at -10kW export limit"""
    grid_power = -10000  # At -10kW export limit
    instantaneous_battery_power = 0

    # Grid
    grid_power_limit = 10000

    # Battery
    battery_soc = 60
    battery_max_charge_discharge_power = 5000
    min_battery_soc = 5
    max_battery_soc = 100

    battery_power, state = check_import_export_limits(grid_power, grid_power_limit, instantaneous_battery_power, battery_soc, battery_max_charge_discharge_power, min_battery_soc, max_battery_soc)
    print(f"Power: {battery_power}, State: {state}")
    assert battery_power == 0
    assert state == State.NO_ACTION


########################################################################################
# Export tests
########################################################################################


def test_handle_export_over_limit():
    """Test when grid power is 1W over -10kW export limit"""
    grid_power = -10001  # 1W over -10kW export limit
    instantaneous_battery_power = 0

    # Grid
    grid_power_limit = 10000

    # Battery
    battery_soc = 60
    battery_max_charge_discharge_power = 5000
    min_battery_soc = 5
    max_battery_soc = 100

    battery_power, state = check_import_export_limits(grid_power, grid_power_limit, instantaneous_battery_power, battery_soc, battery_max_charge_discharge_power, min_battery_soc, max_battery_soc)
    print(f"Power: {battery_power}, State: {state}")
    assert battery_power == 1
    assert state == State.CHARGE_BATTERY


def test_handle_export_under_limit():
    """Test when grid power is under -10kW export limit"""
    grid_power = -5000  # Under -10kW export limit
    instantaneous_battery_power = 0

    # Grid
    grid_power_limit = 10000

    # Battery
    battery_soc = 60
    battery_max_charge_discharge_power = 5000
    min_battery_soc = 5
    max_battery_soc = 100

    battery_power, state = check_import_export_limits(grid_power, grid_power_limit, instantaneous_battery_power, battery_soc, battery_max_charge_discharge_power, min_battery_soc, max_battery_soc)
    print(f"Power: {battery_power}, State: {state}")
    assert battery_power == 0
    assert state == State.NO_ACTION


def test_handle_export_battery_soc_too_high():
    """Test when grid power is over export limit but battery SOC is at maximum"""
    grid_power = -15000  # 5kW over -10kW export limit
    instantaneous_battery_power = 0

    # Grid
    grid_power_limit = 10000

    # Battery
    battery_soc = 100  # At max SOC
    battery_max_charge_discharge_power = 5000
    min_battery_soc = 5
    max_battery_soc = 100

    battery_power, state = check_import_export_limits(grid_power, grid_power_limit, instantaneous_battery_power, battery_soc, battery_max_charge_discharge_power, min_battery_soc, max_battery_soc)
    print(f"Power: {battery_power}, State: {state}")
    assert battery_power == 0
    assert state == State.NO_ACTION


def test_handle_export_max_charge_needed():
    """Test when grid power is 6kW over -10kW export limit requiring max charge"""
    grid_power = -16000  # 6kW over -10kW export limit
    instantaneous_battery_power = 0

    # Grid
    grid_power_limit = 10000

    # Battery
    battery_soc = 50
    battery_max_charge_discharge_power = 5000
    min_battery_soc = 5
    max_battery_soc = 100

    battery_power, state = check_import_export_limits(grid_power, grid_power_limit, instantaneous_battery_power, battery_soc, battery_max_charge_discharge_power, min_battery_soc, max_battery_soc)
    print(f"Power: {battery_power}, State: {state}")
    assert battery_power == -5000
    assert state == State.CHARGE_BATTERY


def test_handle_export_partial_charge_needed():
    """Test when grid power is 2kW over -10kW export limit and battery is discharging"""
    grid_power = -12000  # 2kW over -10kW export limit
    instantaneous_battery_power = -1000  # Currently discharging at 1kW

    # Grid
    grid_power_limit = 10000

    # Battery
    battery_soc = 50
    battery_max_charge_discharge_power = 5000
    min_battery_soc = 5
    max_battery_soc = 100

    battery_power, state = check_import_export_limits(grid_power, grid_power_limit, instantaneous_battery_power, battery_soc, battery_max_charge_discharge_power, min_battery_soc, max_battery_soc)
    print(f"Power: {battery_power}, State: {state}")
    assert battery_power == 1000
    assert state == State.CHARGE_BATTERY


def test_handle_export_over_limit_by_1149W():
    """Test when grid power is 1149W over -3kW export limit and battery is discharging"""
    grid_power = -4149  # 1149W over -3kW export limit
    instantaneous_battery_power = -2999  # Currently discharging 2999W

    # Grid
    grid_power_limit = 3000

    # Battery
    battery_soc = 50
    battery_max_charge_discharge_power = 5000
    min_battery_soc = 5
    max_battery_soc = 100

    battery_power, state = check_import_export_limits(grid_power, grid_power_limit, instantaneous_battery_power, battery_soc, battery_max_charge_discharge_power, min_battery_soc, max_battery_soc)
    print(f"Power: {battery_power}, State: {state}")
    assert battery_power == -1850
    assert state == State.CHARGE_BATTERY
