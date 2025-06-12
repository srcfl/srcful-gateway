from server.control.fuse_protection import check_import_export_limits, State

########################################################################################
# Import tests
########################################################################################


def test_handle_import_when_max_charging():
    """Test when we are max charging and we are over current limit"""
    L1_A = 20  # Over limit
    L2_A = 18
    L3_A = 19
    L1_V = 230
    instantaneous_battery_power = 5000

    # Grid
    grid_current_limit = 16

    # Battery
    battery_soc = 6  # 0-100%
    battery_max_charge_discharge_power = 5000
    min_battery_soc = 5
    max_battery_soc = 100

    battery_power, state = check_import_export_limits(L1_A, L2_A, L3_A, L1_V,
                                                      grid_current_limit,
                                                      instantaneous_battery_power,
                                                      battery_soc,
                                                      battery_max_charge_discharge_power,
                                                      min_battery_soc,
                                                      max_battery_soc)
    print(f"Power: {battery_power}, State: {state}")
    assert battery_power == 4080  # discharge by power_excess (4A * 230V = 920W) from 5000W
    assert state == State.DISCHARGE_BATTERY


def test_handle_import_when_max_discharging():
    """Test when we are max discharging at max power but we are just at the limit"""
    L1_A = 16  # At limit
    L2_A = 14
    L3_A = 15
    L1_V = 230
    instantaneous_battery_power = -5000

    # Grid
    grid_current_limit = 16

    # Battery
    battery_soc = 6  # 0-100%
    battery_max_charge_discharge_power = 5000
    min_battery_soc = 5
    max_battery_soc = 100

    battery_power, state = check_import_export_limits(L1_A, L2_A, L3_A, L1_V, grid_current_limit, instantaneous_battery_power, battery_soc, battery_max_charge_discharge_power, min_battery_soc, max_battery_soc)
    print(f"Power: {battery_power}, State: {state}")
    assert battery_power == 0  # No need to do anything
    assert state == State.NO_ACTION


def test_handle_import_when_over_limit():
    """Test when we are over current limit by small amount"""
    L1_A = 18  # Over limit by 2A
    L2_A = 14
    L3_A = 15
    L1_V = 230
    instantaneous_battery_power = 0

    # Grid
    grid_current_limit = 16

    # Battery
    battery_soc = 6  # 0-100%
    battery_max_charge_discharge_power = 5000
    min_battery_soc = 5
    max_battery_soc = 100

    battery_power, state = check_import_export_limits(L1_A, L2_A, L3_A, L1_V, grid_current_limit, instantaneous_battery_power, battery_soc, battery_max_charge_discharge_power, min_battery_soc, max_battery_soc)
    print(f"Power: {battery_power}, State: {state}")
    assert battery_power == -460  # Reduce by power_excess (2A * 230V = 460W) from 0W
    assert state == State.DISCHARGE_BATTERY


def test_handle_import_when_under_limit():
    """Test when we are just under the limit"""
    L1_A = 15  # Under limit
    L2_A = 14
    L3_A = 15
    L1_V = 230
    instantaneous_battery_power = 0

    # Grid
    grid_current_limit = 16

    # Battery
    battery_soc = 6  # 0-100%
    battery_max_charge_discharge_power = 5000
    min_battery_soc = 5
    max_battery_soc = 100

    battery_power, state = check_import_export_limits(L1_A, L2_A, L3_A, L1_V, grid_current_limit, instantaneous_battery_power, battery_soc, battery_max_charge_discharge_power, min_battery_soc, max_battery_soc)
    print(f"Power: {battery_power}, State: {state}")
    assert battery_power == 0  # No need to do anything
    assert state == State.NO_ACTION


def test_handle_import_battery_soc_too_low():
    """Test when battery SOC is below minimum threshold"""
    L1_A = 20  # Over limit
    L2_A = 14
    L3_A = 15
    L1_V = 230
    instantaneous_battery_power = 0

    # Grid
    grid_current_limit = 16

    # Battery
    battery_soc = 4  # Below min_battery_soc
    battery_max_charge_discharge_power = 5000
    min_battery_soc = 5
    max_battery_soc = 100

    battery_power, state = check_import_export_limits(L1_A, L2_A, L3_A, L1_V, grid_current_limit, instantaneous_battery_power, battery_soc, battery_max_charge_discharge_power, min_battery_soc, max_battery_soc)
    print(f"Power: {battery_power}, State: {state}")
    assert battery_power == 0  # Can't do anything, SoC is too low
    assert state == State.NO_ACTION


def test_handle_import_partial_discharge_needed():
    """Test when we need partial discharge to stay within limits"""
    L1_A = 18  # Over limit by 2A
    L2_A = 14
    L3_A = 15
    L1_V = 230
    instantaneous_battery_power = 1000  # Currently charging at 1kW

    # Grid
    grid_current_limit = 16

    # Battery
    battery_soc = 50  # Good SOC level
    battery_max_charge_discharge_power = 5000
    min_battery_soc = 5
    max_battery_soc = 100

    battery_power, state = check_import_export_limits(L1_A, L2_A, L3_A, L1_V, grid_current_limit, instantaneous_battery_power, battery_soc, battery_max_charge_discharge_power, min_battery_soc, max_battery_soc)
    print(f"Power: {battery_power}, State: {state}")
    assert battery_power == 540  # Reduce by power_excess (2A * 230V = 460W) from 1000W
    assert state == State.DISCHARGE_BATTERY


def test_handle_import_exact_current_match():
    """Test when required current reduction exactly matches available power"""
    L1_A = 16  # At limit
    L2_A = 14
    L3_A = 15
    L1_V = 230
    instantaneous_battery_power = 0  # Neutral battery state

    # Grid
    grid_current_limit = 16

    # Battery
    battery_soc = 50
    battery_max_charge_discharge_power = 5000
    min_battery_soc = 5
    max_battery_soc = 100

    battery_power, state = check_import_export_limits(L1_A, L2_A, L3_A, L1_V, grid_current_limit, instantaneous_battery_power, battery_soc, battery_max_charge_discharge_power, min_battery_soc, max_battery_soc)
    print(f"Power: {battery_power}, State: {state}")
    assert battery_power == 0  # At limit, no action needed
    assert state == State.NO_ACTION


def test_handle_import_small_adjustment_needed():
    """Test when only a small adjustment is needed"""
    L1_A = 17  # Over limit by 1A
    L2_A = 14
    L3_A = 15
    L1_V = 230
    instantaneous_battery_power = 0

    # Grid
    grid_current_limit = 16

    # Battery
    battery_soc = 30
    battery_max_charge_discharge_power = 5000
    min_battery_soc = 5
    max_battery_soc = 100

    battery_power, state = check_import_export_limits(L1_A, L2_A, L3_A, L1_V, grid_current_limit, instantaneous_battery_power, battery_soc, battery_max_charge_discharge_power, min_battery_soc, max_battery_soc)
    print(f"Power: {battery_power}, State: {state}")
    assert battery_power == -230  # Reduce by power_excess (1A * 230V = 230W) from 0W
    assert state == State.DISCHARGE_BATTERY


def test_handle_import_when_already_optimal():
    """Test when current battery power setpoint would be the same"""
    L1_A = 16  # At limit
    L2_A = 14
    L3_A = 15
    L1_V = 230
    instantaneous_battery_power = -2000  # Already discharging

    # Grid
    grid_current_limit = 16

    # Battery
    battery_soc = 50
    battery_max_charge_discharge_power = 5000
    min_battery_soc = 5
    max_battery_soc = 100

    battery_power, state = check_import_export_limits(L1_A, L2_A, L3_A, L1_V, grid_current_limit, instantaneous_battery_power, battery_soc, battery_max_charge_discharge_power, min_battery_soc, max_battery_soc)
    print(f"Power: {battery_power}, State: {state}")
    assert battery_power == 0  # At limit, no change needed
    assert state == State.NO_ACTION


def test_handle_import_moderate_charging_state():
    """Test when battery is in moderate charging state"""
    L1_A = 20  # Over limit by 4A
    L2_A = 14
    L3_A = 15
    L1_V = 230
    instantaneous_battery_power = 2000  # Charging at 2kW

    # Grid
    grid_current_limit = 16

    # Battery
    battery_soc = 40
    battery_max_charge_discharge_power = 5000
    min_battery_soc = 5
    max_battery_soc = 100

    battery_power, state = check_import_export_limits(L1_A, L2_A, L3_A, L1_V, grid_current_limit, instantaneous_battery_power, battery_soc, battery_max_charge_discharge_power, min_battery_soc, max_battery_soc)
    print(f"Power: {battery_power}, State: {state}")
    assert battery_power == 1080  # Reduce by power_excess (4A * 230V = 920W) from 2000W
    assert state == State.DISCHARGE_BATTERY


def test_handle_import_with_different_phase_currents():
    """Test scenario with different phase currents where L2 is highest"""
    L1_A = 14
    L2_A = 18  # Highest phase, over limit by 2A
    L3_A = 12
    L1_V = 230
    instantaneous_battery_power = 1000

    # Grid
    grid_current_limit = 16

    # Battery
    battery_soc = 60
    battery_max_charge_discharge_power = 5000
    min_battery_soc = 5
    max_battery_soc = 100

    battery_power, state = check_import_export_limits(L1_A, L2_A, L3_A, L1_V, grid_current_limit, instantaneous_battery_power, battery_soc, battery_max_charge_discharge_power, min_battery_soc, max_battery_soc)
    print(f"Power: {battery_power}, State: {state}")
    assert battery_power == 540  # Reduce by power_excess (2A * 230V = 460W) from 1000W
    assert state == State.DISCHARGE_BATTERY


########################################################################################
# Export tests
########################################################################################


def test_handle_export_at_limit():
    """Test scenario at export limit"""
    L1_A = -16  # At export limit
    L2_A = -14
    L3_A = -15
    L1_V = 230
    instantaneous_battery_power = 0

    # Grid
    grid_current_limit = 16

    # Battery
    battery_soc = 60
    battery_max_charge_discharge_power = 5000
    min_battery_soc = 5
    max_battery_soc = 100

    battery_power, state = check_import_export_limits(L1_A, L2_A, L3_A, L1_V, grid_current_limit, instantaneous_battery_power, battery_soc, battery_max_charge_discharge_power, min_battery_soc, max_battery_soc)
    print(f"Power: {battery_power}, State: {state}")
    assert battery_power == 0  # At limit, no action needed
    assert state == State.NO_ACTION


def test_handle_export_over_limit():
    """Test scenario over export limit"""
    L1_A = -17  # Over export limit by 1A
    L2_A = -14
    L3_A = -15
    L1_V = 230
    instantaneous_battery_power = 0

    # Grid
    grid_current_limit = 16

    # Battery
    battery_soc = 60
    battery_max_charge_discharge_power = 5000
    min_battery_soc = 5
    max_battery_soc = 100

    battery_power, state = check_import_export_limits(L1_A, L2_A, L3_A, L1_V, grid_current_limit, instantaneous_battery_power, battery_soc, battery_max_charge_discharge_power, min_battery_soc, max_battery_soc)
    print(f"Power: {battery_power}, State: {state}")
    assert battery_power == 230  # Charge by 1A * 230V to reduce export
    assert state == State.CHARGE_BATTERY


def test_handle_export_under_limit():
    """Test scenario under export limit"""
    L1_A = -8  # Under export limit
    L2_A = -6
    L3_A = -7
    L1_V = 230
    instantaneous_battery_power = 0

    # Grid
    grid_current_limit = 16

    # Battery
    battery_soc = 60
    battery_max_charge_discharge_power = 5000
    min_battery_soc = 5
    max_battery_soc = 100

    battery_power, state = check_import_export_limits(L1_A, L2_A, L3_A, L1_V, grid_current_limit, instantaneous_battery_power, battery_soc, battery_max_charge_discharge_power, min_battery_soc, max_battery_soc)
    print(f"Power: {battery_power}, State: {state}")
    assert battery_power == 0  # Within limits, no action needed
    assert state == State.NO_ACTION


def test_handle_export_battery_soc_too_high():
    """Test when battery SOC is above maximum threshold"""
    L1_A = -20  # Over export limit
    L2_A = -18
    L3_A = -19
    L1_V = 230
    instantaneous_battery_power = 0

    # Grid
    grid_current_limit = 16

    # Battery
    battery_soc = 100  # At max SOC
    battery_max_charge_discharge_power = 5000
    min_battery_soc = 5
    max_battery_soc = 100

    battery_power, state = check_import_export_limits(L1_A, L2_A, L3_A, L1_V, grid_current_limit, instantaneous_battery_power, battery_soc, battery_max_charge_discharge_power, min_battery_soc, max_battery_soc)
    print(f"Power: {battery_power}, State: {state}")
    assert battery_power == 0  # Can't charge, SOC is too high
    assert state == State.NO_ACTION


def test_handle_export_max_charge_needed():
    """Test when maximum charge is needed to reduce export"""
    L1_A = -24  # Way over export limit by 8A
    L2_A = -22
    L3_A = -23
    L1_V = 230
    instantaneous_battery_power = 0

    # Grid
    grid_current_limit = 16

    # Battery
    battery_soc = 50
    battery_max_charge_discharge_power = 5000
    min_battery_soc = 5
    max_battery_soc = 100

    battery_power, state = check_import_export_limits(L1_A, L2_A, L3_A, L1_V, grid_current_limit, instantaneous_battery_power, battery_soc, battery_max_charge_discharge_power, min_battery_soc, max_battery_soc)
    print(f"Power: {battery_power}, State: {state}")
    assert battery_power == 1840  # Increase by excess_current * L1_V (8A * 230V) from 0W
    assert state == State.CHARGE_BATTERY


def test_handle_export_partial_charge_needed():
    """Test when partial charge is needed to stay within export limits"""
    L1_A = -14
    L2_A = -12
    L3_A = -18  # Over export limit by 2A (min current)
    L1_V = 230
    instantaneous_battery_power = -1000  # Currently discharging at 1kW

    # Grid
    grid_current_limit = 16

    # Battery
    battery_soc = 50
    battery_max_charge_discharge_power = 5000
    min_battery_soc = 5
    max_battery_soc = 100

    battery_power, state = check_import_export_limits(L1_A, L2_A, L3_A, L1_V, grid_current_limit, instantaneous_battery_power, battery_soc, battery_max_charge_discharge_power, min_battery_soc, max_battery_soc)
    print(f"Power: {battery_power}, State: {state}")
    assert battery_power == -540  # Change from -1000 to -540 (2A * 230V = 460W increase)
    assert state == State.CHARGE_BATTERY


def test_handle_export_with_l3_as_minimum():
    """Test export scenario where L3 has the most negative current"""
    L1_A = -12
    L2_A = -14
    L3_A = -17  # Most negative, over export limit by 1A
    L1_V = 230
    instantaneous_battery_power = -500

    # Grid
    grid_current_limit = 16

    # Battery
    battery_soc = 50
    battery_max_charge_discharge_power = 5000
    min_battery_soc = 5
    max_battery_soc = 100

    battery_power, state = check_import_export_limits(L1_A, L2_A, L3_A, L1_V, grid_current_limit, instantaneous_battery_power, battery_soc, battery_max_charge_discharge_power, min_battery_soc, max_battery_soc)
    print(f"Power: {battery_power}, State: {state}")
    assert battery_power == -270  # Increase by 1A * 230V = 230W from -500W
    assert state == State.CHARGE_BATTERY


def test_handle_export_already_charging():
    """Test export scenario when battery is already charging"""
    L1_A = -12
    L2_A = -14
    L3_A = -17  # Over export limit by 1A
    L1_V = 230
    instantaneous_battery_power = 2000  # Already charging

    # Grid
    grid_current_limit = 16

    # Battery
    battery_soc = 50
    battery_max_charge_discharge_power = 5000
    min_battery_soc = 5
    max_battery_soc = 100

    battery_power, state = check_import_export_limits(L1_A, L2_A, L3_A, L1_V, grid_current_limit, instantaneous_battery_power, battery_soc, battery_max_charge_discharge_power, min_battery_soc, max_battery_soc)
    print(f"Power: {battery_power}, State: {state}")
    assert battery_power == 2230  # Increase by 1A * 230V = 230W from 2000W
    assert state == State.CHARGE_BATTERY


def test_handle_mixed_phase_currents():
    """Test scenario with mixed positive and negative phase currents"""
    L1_A = 8   # Importing
    L2_A = -18  # Exporting (most negative, over export limit by 2A)
    L3_A = 4   # Importing
    L1_V = 230
    instantaneous_battery_power = 0

    # Grid
    grid_current_limit = 16

    # Battery
    battery_soc = 50
    battery_max_charge_discharge_power = 5000
    min_battery_soc = 5
    max_battery_soc = 100

    battery_power, state = check_import_export_limits(L1_A, L2_A, L3_A, L1_V, grid_current_limit, instantaneous_battery_power, battery_soc, battery_max_charge_discharge_power, min_battery_soc, max_battery_soc)
    print(f"Power: {battery_power}, State: {state}")
    assert battery_power == 460  # Charge by 2A * 230V to reduce export
    assert state == State.CHARGE_BATTERY
