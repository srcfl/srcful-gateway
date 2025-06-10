from server.control.control import handle_import, State


def test_handle_import_when_max_charging():
    """Test when we are max charging and we are over limit"""
    # PV & Load stuff
    pv_power = 0
    total_household_load = 15000

    # Grid stuff
    grid_import_power_limit = 10000

    # Battery stuff
    battery_soc = 6  # 0-100%
    instantaneous_battery_power = 5000
    battery_max_charge_discharge_power = 5000
    min_battery_soc = 5

    net_power = total_household_load + instantaneous_battery_power - pv_power
    power, state = handle_import(net_power, grid_import_power_limit, instantaneous_battery_power, battery_soc, battery_max_charge_discharge_power, min_battery_soc)
    print(f"Power: {power}, State: {state}")
    assert power == -5000  # discharge
    assert state == State.DISCHARGE_BATTERY


def test_handle_import_when_max_discharging():
    """Test when we are max discharging at max power but we are just at the limit"""
    # PV & Load stuff
    pv_power = 0
    total_household_load = 15000

    # Grid stuff
    grid_import_power_limit = 10000

    # Battery stuff
    battery_soc = 6  # 0-100%
    instantaneous_battery_power = -5000
    battery_max_charge_discharge_power = 5000
    min_battery_soc = 5

    net_power = total_household_load + instantaneous_battery_power - pv_power
    power, state = handle_import(net_power, grid_import_power_limit, instantaneous_battery_power, battery_soc, battery_max_charge_discharge_power, min_battery_soc)
    print(f"Power: {power}, State: {state}")
    assert power == 0  # No need to do anything
    assert state == State.NO_ACTION


def test_handle_import_when_over_limit():
    """Test when we are over limit by 1W"""
    # PV & Load stuff
    pv_power = 0
    total_household_load = 15001

    # Grid stuff
    grid_import_power_limit = 10000

    # Battery stuff
    battery_soc = 6  # 0-100%
    instantaneous_battery_power = 0
    battery_max_charge_discharge_power = 5000
    min_battery_soc = 5

    net_power = total_household_load + instantaneous_battery_power - pv_power
    power, state = handle_import(net_power, grid_import_power_limit, instantaneous_battery_power, battery_soc, battery_max_charge_discharge_power, min_battery_soc)
    print(f"Power: {power}, State: {state}")
    assert power == 5000  # Charge at max power
    assert state == State.OVER_LIMIT


def test_handle_export_when_under_limit():
    """Test when we just at the limit"""
    # PV & Load stuff
    pv_power = 0
    total_household_load = 10000

    # Grid stuff
    grid_import_power_limit = 10000

    # Battery stuff
    battery_soc = 6  # 0-100%
    instantaneous_battery_power = 0
    battery_max_charge_discharge_power = 5000
    min_battery_soc = 5

    net_power = total_household_load + instantaneous_battery_power - pv_power
    power, state = handle_import(net_power, grid_import_power_limit, instantaneous_battery_power, battery_soc, battery_max_charge_discharge_power, min_battery_soc)
    print(f"Power: {power}, State: {state}")
    assert power == 0  # No need to do anything
    assert state == State.NO_ACTION


def test_handle_import_battery_soc_too_low():
    """Test when battery SOC is below minimum threshold"""
    # PV & Load stuff
    pv_power = 0
    total_household_load = 15000

    # Grid stuff
    grid_import_power_limit = 10000

    # Battery stuff
    battery_soc = 4  # Below min_battery_soc
    instantaneous_battery_power = 0
    battery_max_charge_discharge_power = 5000
    min_battery_soc = 5

    net_power = total_household_load + instantaneous_battery_power - pv_power
    power, state = handle_import(net_power, grid_import_power_limit, instantaneous_battery_power, battery_soc, battery_max_charge_discharge_power, min_battery_soc)
    print(f"Power: {power}, State: {state}")
    assert power == 0  # Can't do anything
    assert state == State.NO_ACTION


def test_handle_import_partial_discharge_needed():
    """Test when we need partial discharge to stay within limits"""
    # PV & Load stuff
    pv_power = 0
    total_household_load = 12000  # 2000W over limit

    # Grid stuff
    grid_import_power_limit = 10000

    # Battery stuff
    battery_soc = 50  # Good SOC level
    instantaneous_battery_power = 1000  # Currently charging at 1kW
    battery_max_charge_discharge_power = 5000
    min_battery_soc = 5

    net_power = total_household_load + instantaneous_battery_power - pv_power  # 13000W
    power, state = handle_import(net_power, grid_import_power_limit, instantaneous_battery_power, battery_soc, battery_max_charge_discharge_power, min_battery_soc)
    print(f"Power: {power}, State: {state}")
    assert power == -2000  # Should discharge to -2000W (from +1000W to -2000W = 3000W reduction)
    assert state == State.DISCHARGE_BATTERY


def test_handle_import_exact_power_match():
    """Test when required power reduction exactly matches available power"""
    # PV & Load stuff
    pv_power = 0
    total_household_load = 15000  # 5000W over limit

    # Grid stuff
    grid_import_power_limit = 10000

    # Battery stuff
    battery_soc = 50
    instantaneous_battery_power = 0  # Neutral battery state
    battery_max_charge_discharge_power = 5000  # Can discharge exactly 5000W
    min_battery_soc = 5

    net_power = total_household_load + instantaneous_battery_power - pv_power  # 15000W
    power, state = handle_import(net_power, grid_import_power_limit, instantaneous_battery_power, battery_soc, battery_max_charge_discharge_power, min_battery_soc)
    print(f"Power: {power}, State: {state}")
    assert power == -5000  # Should discharge at max power
    assert state == State.DISCHARGE_BATTERY


def test_handle_import_small_adjustment_needed():
    """Test when only a small adjustment is needed"""
    # PV & Load stuff
    pv_power = 0
    total_household_load = 10500  # Just 500W over limit

    # Grid stuff
    grid_import_power_limit = 10000

    # Battery stuff
    battery_soc = 30
    instantaneous_battery_power = 0
    battery_max_charge_discharge_power = 5000
    min_battery_soc = 5

    net_power = total_household_load + instantaneous_battery_power - pv_power
    power, state = handle_import(net_power, grid_import_power_limit, instantaneous_battery_power, battery_soc, battery_max_charge_discharge_power, min_battery_soc)
    print(f"Power: {power}, State: {state}")
    assert power == -500  # Small discharge to handle 500W excess
    assert state == State.DISCHARGE_BATTERY


def test_handle_import_when_already_optimal():
    """Test when current battery power setpoint would be the same"""
    # PV & Load stuff
    pv_power = 0
    total_household_load = 12000

    # Grid stuff
    grid_import_power_limit = 10000

    # Battery stuff
    battery_soc = 50
    instantaneous_battery_power = -2000  # Already discharging the right amount
    battery_max_charge_discharge_power = 5000
    min_battery_soc = 5

    net_power = total_household_load + instantaneous_battery_power - pv_power  # 10000W (at limit)
    power, state = handle_import(net_power, grid_import_power_limit, instantaneous_battery_power, battery_soc, battery_max_charge_discharge_power, min_battery_soc)
    print(f"Power: {power}, State: {state}")
    assert power == 0  # No change needed
    assert state == State.NO_ACTION


def test_handle_import_moderate_charging_state():
    """Test when battery is in moderate charging state"""
    # PV & Load stuff
    pv_power = 0
    total_household_load = 13000

    # Grid stuff
    grid_import_power_limit = 10000

    # Battery stuff
    battery_soc = 40
    instantaneous_battery_power = 2000  # Charging at 2kW
    battery_max_charge_discharge_power = 5000
    min_battery_soc = 5

    net_power = total_household_load + instantaneous_battery_power - pv_power  # 15000W
    power, state = handle_import(net_power, grid_import_power_limit, instantaneous_battery_power, battery_soc, battery_max_charge_discharge_power, min_battery_soc)
    print(f"Power: {power}, State: {state}")
    assert power == -3000  # Change from +2000 to -3000 (5000W reduction)
    assert state == State.DISCHARGE_BATTERY


def test_handle_import_with_pv_generation():
    """Test scenario with PV generation reducing net power"""
    # PV & Load stuff
    pv_power = 3000  # 3kW PV generation
    total_household_load = 15000

    # Grid stuff
    grid_import_power_limit = 10000

    # Battery stuff
    battery_soc = 60
    instantaneous_battery_power = 1000
    battery_max_charge_discharge_power = 5000
    min_battery_soc = 5

    net_power = total_household_load + instantaneous_battery_power - pv_power  # 13000W
    power, state = handle_import(net_power, grid_import_power_limit, instantaneous_battery_power, battery_soc, battery_max_charge_discharge_power, min_battery_soc)
    print(f"Power: {power}, State: {state}")
    assert power == -2000  # Reduce from +1000 to -2000 (3000W reduction)
    assert state == State.DISCHARGE_BATTERY
