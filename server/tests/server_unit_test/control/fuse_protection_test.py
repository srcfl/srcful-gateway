from server.control.fuse_protection import handle_fuse_limit, State

########################################################################################
# Import tests
########################################################################################


def test_handle_import_when_max_charging():
    """Test when battery is max charging and L1 current is 4A over 16A limit"""
    L1_A = 20  # 4A over 16A limit
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

    battery_power, state = handle_fuse_limit(L1_A, L2_A, L3_A, L1_V,
                                             grid_current_limit,
                                             instantaneous_battery_power,
                                             battery_soc,
                                             battery_max_charge_discharge_power,
                                             min_battery_soc,
                                             max_battery_soc)
    print(f"Power: {battery_power}, State: {state}")
    assert battery_power == 2240
    assert state == State.DISCHARGE_BATTERY


def test_handle_import_when_max_discharging():
    """Test when battery is max discharging and L1 current is exactly at 16A limit"""
    L1_A = 16  # Exactly at 16A limit
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

    battery_power, state = handle_fuse_limit(L1_A, L2_A, L3_A, L1_V, grid_current_limit, instantaneous_battery_power, battery_soc, battery_max_charge_discharge_power, min_battery_soc, max_battery_soc)
    print(f"Power: {battery_power}, State: {state}")
    assert battery_power == 0  # No need to do anything
    assert state == State.NO_ACTION


def test_handle_import_when_over_limit():
    """Test when L1 current is 2A over 16A limit with neutral battery"""
    L1_A = 18  # 2A over 16A limit
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

    battery_power, state = handle_fuse_limit(L1_A, L2_A, L3_A, L1_V, grid_current_limit, instantaneous_battery_power, battery_soc, battery_max_charge_discharge_power, min_battery_soc, max_battery_soc)
    print(f"Power: {battery_power}, State: {state}")
    assert battery_power == -1380
    assert state == State.DISCHARGE_BATTERY


def test_handle_import_when_under_limit():
    """Test when all phase currents are under 16A limit"""
    L1_A = 15  # 1A under 16A limit
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

    battery_power, state = handle_fuse_limit(L1_A, L2_A, L3_A, L1_V, grid_current_limit, instantaneous_battery_power, battery_soc, battery_max_charge_discharge_power, min_battery_soc, max_battery_soc)
    print(f"Power: {battery_power}, State: {state}")
    assert battery_power == 0  # No need to do anything
    assert state == State.NO_ACTION


def test_handle_import_battery_soc_too_low():
    """Test when L1 current is over limit but battery SOC is below minimum threshold"""
    L1_A = 20  # 4A over 16A limit
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

    battery_power, state = handle_fuse_limit(L1_A, L2_A, L3_A, L1_V, grid_current_limit, instantaneous_battery_power, battery_soc, battery_max_charge_discharge_power, min_battery_soc, max_battery_soc)
    print(f"Power: {battery_power}, State: {state}")
    assert battery_power == 0  # Can't do anything, SoC is too low
    assert state == State.NO_ACTION


def test_handle_import_partial_discharge_needed():
    """Test when L1 current is 2A over limit and battery is charging 1kW"""
    L1_A = 18  # 2A over 16A limit
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

    battery_power, state = handle_fuse_limit(L1_A, L2_A, L3_A, L1_V, grid_current_limit, instantaneous_battery_power, battery_soc, battery_max_charge_discharge_power, min_battery_soc, max_battery_soc)
    print(f"Power: {battery_power}, State: {state}")
    assert battery_power == -380
    assert state == State.DISCHARGE_BATTERY


def test_handle_import_exact_current_match():
    """Test when L1 current is exactly at 16A limit with neutral battery"""
    L1_A = 16  # Exactly at 16A limit
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

    battery_power, state = handle_fuse_limit(L1_A, L2_A, L3_A, L1_V, grid_current_limit, instantaneous_battery_power, battery_soc, battery_max_charge_discharge_power, min_battery_soc, max_battery_soc)
    print(f"Power: {battery_power}, State: {state}")
    assert battery_power == 0  # At limit, no action needed
    assert state == State.NO_ACTION


def test_handle_import_small_adjustment_needed():
    """Test when L1 current is 1A over 16A limit with neutral battery"""
    L1_A = 17  # 1A over 16A limit
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

    battery_power, state = handle_fuse_limit(L1_A, L2_A, L3_A, L1_V, grid_current_limit, instantaneous_battery_power, battery_soc, battery_max_charge_discharge_power, min_battery_soc, max_battery_soc)
    print(f"Power: {battery_power}, State: {state}")
    assert battery_power == -690
    assert state == State.DISCHARGE_BATTERY


def test_handle_import_when_already_optimal():
    """Test when L1 current is at 16A limit and battery is already discharging"""
    L1_A = 16  # Exactly at 16A limit
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

    battery_power, state = handle_fuse_limit(L1_A, L2_A, L3_A, L1_V, grid_current_limit, instantaneous_battery_power, battery_soc, battery_max_charge_discharge_power, min_battery_soc, max_battery_soc)
    print(f"Power: {battery_power}, State: {state}")
    assert battery_power == 0  # At limit, no change needed
    assert state == State.NO_ACTION


def test_handle_import_moderate_charging_state():
    """Test when L1 current is 4A over 16A limit and battery is charging 2kW"""
    L1_A = 20  # 4A over 16A limit
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

    battery_power, state = handle_fuse_limit(L1_A, L2_A, L3_A, L1_V, grid_current_limit, instantaneous_battery_power, battery_soc, battery_max_charge_discharge_power, min_battery_soc, max_battery_soc)
    print(f"Power: {battery_power}, State: {state}")
    assert battery_power == -760
    assert state == State.DISCHARGE_BATTERY


def test_handle_import_with_different_phase_currents():
    """Test when L2 current is highest at 2A over 16A limit"""
    L1_A = 14
    L2_A = 18  # 2A over 16A limit (highest phase)
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

    battery_power, state = handle_fuse_limit(L1_A, L2_A, L3_A, L1_V, grid_current_limit, instantaneous_battery_power, battery_soc, battery_max_charge_discharge_power, min_battery_soc, max_battery_soc)
    print(f"Power: {battery_power}, State: {state}")
    assert battery_power == -380
    assert state == State.DISCHARGE_BATTERY


########################################################################################
# Export tests
########################################################################################


def test_handle_export_at_limit():
    """Test when L1 current is exactly at -16A export limit"""
    L1_A = -16  # Exactly at -16A export limit
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

    battery_power, state = handle_fuse_limit(L1_A, L2_A, L3_A, L1_V, grid_current_limit, instantaneous_battery_power, battery_soc, battery_max_charge_discharge_power, min_battery_soc, max_battery_soc)
    print(f"Power: {battery_power}, State: {state}")
    assert battery_power == 0  # At limit, no action needed
    assert state == State.NO_ACTION


def test_handle_export_over_limit():
    """Test when L1 current is 1A over -16A export limit"""
    L1_A = -17  # 1A over -16A export limit
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

    battery_power, state = handle_fuse_limit(L1_A, L2_A, L3_A, L1_V, grid_current_limit, instantaneous_battery_power, battery_soc, battery_max_charge_discharge_power, min_battery_soc, max_battery_soc)
    print(f"Power: {battery_power}, State: {state}")
    assert battery_power == 690
    assert state == State.CHARGE_BATTERY


def test_handle_export_under_limit():
    """Test when all phase currents are under -16A export limit"""
    L1_A = -8  # Well under -16A export limit
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

    battery_power, state = handle_fuse_limit(L1_A, L2_A, L3_A, L1_V, grid_current_limit, instantaneous_battery_power, battery_soc, battery_max_charge_discharge_power, min_battery_soc, max_battery_soc)
    print(f"Power: {battery_power}, State: {state}")
    assert battery_power == 0  # Within limits, no action needed
    assert state == State.NO_ACTION


def test_handle_export_battery_soc_too_high():
    """Test when currents are over export limit but battery SOC is at maximum"""
    L1_A = -20  # 4A over -16A export limit
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

    battery_power, state = handle_fuse_limit(L1_A, L2_A, L3_A, L1_V, grid_current_limit, instantaneous_battery_power, battery_soc, battery_max_charge_discharge_power, min_battery_soc, max_battery_soc)
    print(f"Power: {battery_power}, State: {state}")
    assert battery_power == 0  # Can't charge, SOC is too high
    assert state == State.NO_ACTION


def test_handle_export_max_charge_needed():
    """Test when L1 current is 8A over -16A export limit requiring max charge"""
    L1_A = -24  # 8A over -16A export limit
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

    battery_power, state = handle_fuse_limit(L1_A, L2_A, L3_A, L1_V, grid_current_limit, instantaneous_battery_power, battery_soc, battery_max_charge_discharge_power, min_battery_soc, max_battery_soc)
    print(f"Power: {battery_power}, State: {state}")
    assert battery_power == 5000
    assert state == State.CHARGE_BATTERY


def test_handle_export_partial_charge_needed():
    """Test when L3 current is 2A over -16A export limit and battery is discharging"""
    L1_A = -14
    L2_A = -12
    L3_A = -18  # 2A over -16A export limit (most negative)
    L1_V = 230
    instantaneous_battery_power = -1000  # Currently discharging at 1kW

    # Grid
    grid_current_limit = 16

    # Battery
    battery_soc = 50
    battery_max_charge_discharge_power = 5000
    min_battery_soc = 5
    max_battery_soc = 100

    battery_power, state = handle_fuse_limit(L1_A, L2_A, L3_A, L1_V, grid_current_limit, instantaneous_battery_power, battery_soc, battery_max_charge_discharge_power, min_battery_soc, max_battery_soc)
    print(f"Power: {battery_power}, State: {state}")
    assert battery_power == 380
    assert state == State.CHARGE_BATTERY


def test_handle_export_with_l3_as_minimum():
    """Test when L3 current is most negative at 1A over -16A export limit"""
    L1_A = -12
    L2_A = -14
    L3_A = -17  # 1A over -16A export limit (most negative)
    L1_V = 230
    instantaneous_battery_power = -500

    # Grid
    grid_current_limit = 16

    # Battery
    battery_soc = 50
    battery_max_charge_discharge_power = 5000
    min_battery_soc = 5
    max_battery_soc = 100

    battery_power, state = handle_fuse_limit(L1_A, L2_A, L3_A, L1_V, grid_current_limit, instantaneous_battery_power, battery_soc, battery_max_charge_discharge_power, min_battery_soc, max_battery_soc)
    print(f"Power: {battery_power}, State: {state}")
    assert battery_power == 190
    assert state == State.CHARGE_BATTERY


def test_handle_export_already_charging():
    """Test when L3 current is 1A over -16A export limit and battery is already charging"""
    L1_A = -12
    L2_A = -14
    L3_A = -17  # 1A over -16A export limit
    L1_V = 230
    instantaneous_battery_power = 2000  # Already charging

    # Grid
    grid_current_limit = 16

    # Battery
    battery_soc = 50
    battery_max_charge_discharge_power = 5000
    min_battery_soc = 5
    max_battery_soc = 100

    battery_power, state = handle_fuse_limit(L1_A, L2_A, L3_A, L1_V, grid_current_limit, instantaneous_battery_power, battery_soc, battery_max_charge_discharge_power, min_battery_soc, max_battery_soc)
    print(f"Power: {battery_power}, State: {state}")
    assert battery_power == 2690
    assert state == State.CHARGE_BATTERY


def test_handle_mixed_phase_currents():
    """Test with mixed phase currents where L2 is 2A over -16A export limit"""
    L1_A = 8   # Positive (importing)
    L2_A = -18  # 2A over -16A export limit (most negative)
    L3_A = 4   # Positive (importing)
    L1_V = 230
    instantaneous_battery_power = 0

    # Grid
    grid_current_limit = 16

    # Battery
    battery_soc = 50
    battery_max_charge_discharge_power = 5000
    min_battery_soc = 5
    max_battery_soc = 100

    battery_power, state = handle_fuse_limit(L1_A, L2_A, L3_A, L1_V, grid_current_limit, instantaneous_battery_power, battery_soc, battery_max_charge_discharge_power, min_battery_soc, max_battery_soc)
    print(f"Power: {battery_power}, State: {state}")
    assert battery_power == 1380
    assert state == State.CHARGE_BATTERY


def test_handle_import_three_phase_factor_forces_max_power():
    """Test when L1 current is 3A over 16A limit with battery charging at 3kW"""
    L1_A = 19  # 3A over 16A limit
    L2_A = 14
    L3_A = 15
    L1_V = 230
    instantaneous_battery_power = 3000  # High current power state

    # Grid
    grid_current_limit = 16

    # Battery
    battery_soc = 50
    battery_max_charge_discharge_power = 5000
    min_battery_soc = 5
    max_battery_soc = 100

    battery_power, state = handle_fuse_limit(L1_A, L2_A, L3_A, L1_V, grid_current_limit, instantaneous_battery_power, battery_soc, battery_max_charge_discharge_power, min_battery_soc, max_battery_soc)
    print(f"Power: {battery_power}, State: {state}")
    assert battery_power == 930
    assert state == State.DISCHARGE_BATTERY


def test_handle_import_three_phase_factor_insufficient_power():
    """Test when L1 current is 4A over 16A limit with limited battery capacity"""
    L1_A = 20  # 4A over 16A limit
    L2_A = 14
    L3_A = 15
    L1_V = 230
    instantaneous_battery_power = 2500  # Limited available power

    # Grid
    grid_current_limit = 16

    # Battery
    battery_soc = 50
    battery_max_charge_discharge_power = 2800  # Smaller battery capacity
    min_battery_soc = 5
    max_battery_soc = 100

    battery_power, state = handle_fuse_limit(L1_A, L2_A, L3_A, L1_V, grid_current_limit, instantaneous_battery_power, battery_soc, battery_max_charge_discharge_power, min_battery_soc, max_battery_soc)
    print(f"Power: {battery_power}, State: {state}")
    assert battery_power == -260
    assert state == State.DISCHARGE_BATTERY
