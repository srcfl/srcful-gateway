from server.control.control import check_import_export_limits, State

########################################################################################
# Import tests
########################################################################################


def test_handle_import_when_max_charging():
    """Test when we are max charging and we are over limit"""
    grid_power = 20000
    instantaneous_battery_power = 5000

    # Grid
    grid_power_limit = 10000

    # Battery
    battery_soc = 6  # 0-100%
    battery_max_charge_discharge_power = 5000
    min_battery_soc = 5
    max_battery_soc = 100

    battery_power, state = check_import_export_limits(grid_power, grid_power_limit, instantaneous_battery_power, battery_soc, battery_max_charge_discharge_power, min_battery_soc, max_battery_soc)
    print(f"Power: {battery_power}, State: {state}")
    assert battery_power == -5000  # discharge at max power
    assert state == State.DISCHARGE_BATTERY


def test_handle_import_when_max_discharging():
    """Test when we are max discharging at max power but we are just at the limit"""
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
    """Test when we are over limit by 1W"""
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
    assert battery_power == 5000  # Discharge at max power
    assert state == State.DISCHARGE_BATTERY


def test_handle_export_when_under_limit():
    """Test when we just at the limit"""
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
    assert battery_power == 0  # No need to do anything
    assert state == State.NO_ACTION


def test_handle_import_battery_soc_too_low():
    """Test when battery SOC is below minimum threshold"""
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
    assert battery_power == 0  # Can't do anything, SoC is too low
    assert state == State.NO_ACTION


def test_handle_import_partial_discharge_needed():
    """Test when we need partial discharge to stay within limits"""
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
    assert battery_power == -2000  # Need to reduce by 3000W from +1000 to -2000
    assert state == State.DISCHARGE_BATTERY


def test_handle_import_exact_power_match():
    """Test when required power reduction exactly matches available power"""
    grid_power = 10000
    instantaneous_battery_power = 0  # Neutral battery state

    # Grid
    grid_power_limit = 10000

    # Battery
    battery_soc = 50
    battery_max_charge_discharge_power = 5000  # Can discharge exactly 5000W
    min_battery_soc = 5
    max_battery_soc = 100

    battery_power, state = check_import_export_limits(grid_power, grid_power_limit, instantaneous_battery_power, battery_soc, battery_max_charge_discharge_power, min_battery_soc, max_battery_soc)
    print(f"Power: {battery_power}, State: {state}")
    assert battery_power == 0  # At limit, no action needed
    assert state == State.NO_ACTION


def test_handle_import_small_adjustment_needed():
    """Test when only a small adjustment is needed"""
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
    assert battery_power == -500  # Small discharge to handle 500W excess
    assert state == State.DISCHARGE_BATTERY


def test_handle_import_when_already_optimal():
    """Test when current battery power setpoint would be the same"""
    grid_power = 10000
    instantaneous_battery_power = -2000  # Already discharging the right amount

    # Grid
    grid_power_limit = 10000

    # Battery
    battery_soc = 50
    battery_max_charge_discharge_power = 5000
    min_battery_soc = 5
    max_battery_soc = 100

    battery_power, state = check_import_export_limits(grid_power, grid_power_limit, instantaneous_battery_power, battery_soc, battery_max_charge_discharge_power, min_battery_soc, max_battery_soc)
    print(f"Power: {battery_power}, State: {state}")
    assert battery_power == 0  # At limit, no change needed
    assert state == State.NO_ACTION


def test_handle_import_moderate_charging_state():
    """Test when battery is in moderate charging state"""
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
    assert battery_power == -3000  # Change from +2000 to -3000 (5000W reduction)
    assert state == State.DISCHARGE_BATTERY


def test_handle_import_with_pv_generation():
    """Test scenario with PV generation reducing net power"""
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
    """Test scenario at export limit"""
    grid_power = -10000  # At export limit
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
    assert battery_power == 0  # At limit, no action needed
    assert state == State.NO_ACTION


########################################################################################
# Export tests
########################################################################################


def test_handle_export_over_limit():
    """Test scenario over export limit"""
    grid_power = -10001  # Over export limit by 1W
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
    assert battery_power == 1  # Charge by 1W to reduce export
    assert state == State.CHARGE_BATTERY


def test_handle_export_under_limit():
    """Test scenario under export limit"""
    grid_power = -5000  # Under export limit
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
    assert battery_power == 0  # Within limits, no action needed
    assert state == State.NO_ACTION


def test_handle_export_battery_soc_too_high():
    """Test when battery SOC is above maximum threshold"""
    grid_power = -15000  # Over export limit
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
    assert battery_power == 0  # Can't charge, SOC is too high
    assert state == State.NO_ACTION


def test_handle_export_max_charge_needed():
    """Test when maximum charge is needed to reduce export"""
    grid_power = -16000  # Way over export limit
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
    assert battery_power == -5000  # Charge at max power (negative for charging)
    assert state == State.CHARGE_BATTERY


def test_handle_export_partial_charge_needed():
    """Test when partial charge is needed to stay within export limits"""
    grid_power = -12000  # Over export limit by 2000W
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
    assert battery_power == 1000  # Change from -1000 to +1000 (2000W increase)
    assert state == State.CHARGE_BATTERY
