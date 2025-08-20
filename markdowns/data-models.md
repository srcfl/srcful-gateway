# Data Models

The Srcful Gateway uses standardized data models to represent energy system measurements from distributed energy resources (DER). These models ensure consistent data structure across different device types and manufacturers.

## Core Components

### Value
A measurement value containing three components:
- **value**: Numeric measurement
- **unit**: Standardized unit (W, kW, V, A, Hz, °C, %, kWh)
- **name**: Descriptive field name

### DERData
Root data structure containing up to three subsystems:
- **pv**: Photovoltaic system data
- **battery**: Battery storage system data  
- **meter**: Grid meter data

## PV Data Model

Represents photovoltaic solar generation systems.

| Field | Unit | Description | Sign Convention |
|-------|------|-------------|-----------------|
| `power` | W/kW | Current power output | Always negative (generation) |
| `rated_power` | W/kW | Maximum rated capacity | Positive |
| `mppt1_voltage` | V | MPPT1 DC voltage | Positive |
| `mppt1_current` | A | MPPT1 DC current | Always negative (generation) |
| `mppt2_voltage` | V | MPPT2 DC voltage | Positive |
| `mppt2_current` | A | MPPT2 DC current | Always negative (generation) |
| `inverter_temperature` | °C | Inverter temperature | Positive |
| `total_pv_generation` | kWh | Cumulative energy generated | Always positive |

## Battery Data Model

Represents energy storage systems.

| Field | Unit | Description | Sign Convention |
|-------|------|-------------|-----------------|
| `power` | W/kW | Charging/discharging power | Positive (charging), Negative (discharging) |
| `current` | A | Battery current | Positive (charging), Negative (discharging) |
| `voltage` | V | Battery voltage | Positive |
| `soc` | % | State of charge | 0-100% |
| `battery_temperature` | °C | Battery temperature | Positive |
| `total_charge_energy` | kWh | Cumulative energy charged | Always positive |
| `total_discharge_energy` | kWh | Cumulative energy discharged | Always positive |

## Meter Data Model

Represents grid connection meters with three-phase support.

| Field | Unit | Description | Sign Convention |
|-------|------|-------------|-----------------|
| `active_power` | W/kW | Total active power | Positive (import), Negative (export) |
| `frequency` | Hz | Grid frequency | Positive |
| `l1_current` | A | Phase 1 current | Positive (import), Negative (export) |
| `l2_current` | A | Phase 2 current | Positive (import), Negative (export) |
| `l3_current` | A | Phase 3 current | Positive (import), Negative (export) |
| `l1_voltage` | V | Phase 1 voltage | Positive |
| `l2_voltage` | V | Phase 2 voltage | Positive |
| `l3_voltage` | V | Phase 3 voltage | Positive |
| `l1_active_power` | W/kW | Phase 1 active power | Positive (import), Negative (export) |
| `l2_active_power` | W/kW | Phase 2 active power | Positive (import), Negative (export) |
| `l3_active_power` | W/kW | Phase 3 active power | Positive (import), Negative (export) |
| `total_import_energy` | kWh | Cumulative energy imported | Always positive |
| `total_export_energy` | kWh | Cumulative energy exported | Always positive |

## Sign Conventions

The data models follow consistent sign conventions:

- **Generation**: Negative values (PV power, PV current)
- **Consumption/Import**: Positive values (meter import, battery charging)
- **Export/Discharge**: Negative values (meter export, battery discharge)
- **Cumulative Energy**: Always positive (total generation, charge, discharge, import, export)

## Data Serialization

All data models support dictionary serialization with two modes:
- **Verbose**: Includes value, unit, and name for each measurement
- **Compact**: Returns only numeric values

This standardized approach ensures consistent data interpretation across the Srcful ecosystem.
