# Data Models

## Table of Contents

- [Overview](#overview)
  - [DERData Structure](#derdata-structure)
  - [Inheritance Model](#inheritance-model)
- [Units and Conventions](#units-and-conventions)
  - [Units](#units)
  - [Sign Conventions](#sign-conventions)
  - [Field Naming Convention](#field-naming-convention)
- [Data Models](#data-models)
  - [BaseDeviceData](#basedevicedata)
  - [PV Data Model](#pv-data-model)
  - [Battery Data Model](#battery-data-model)
  - [Meter Data Model](#meter-data-model)
- [MQTT Integration](#mqtt-integration)
  - [Topic Structure](#topic-structure)

## Overview

### DERData Structure

The root data structure containing up to three subsystems:

- **pv**: Photovoltaic system data
- **battery**: Battery storage system data
- **meter**: Meter data

### Inheritance Model

- **BaseDeviceData**: Abstract base class containing common fields shared by all device types
- **PVData**: Inherits from `BaseDeviceData`, adds PV-specific fields
- **BatteryData**: Inherits from `BaseDeviceData`, adds battery-specific fields
- **MeterData**: Inherits from `BaseDeviceData`, adds meter-specific fields

## Units and Conventions

### Units

All measurements use base SI units:

- Power: W (watts)
- Energy: Wh (watt-hours)
- Voltage: V (volts)
- Current: A (amperes)
- Frequency: Hz (hertz)
- Temperature: °C (Celsius)
- State of Charge: fraction (0.0 = empty, 1.0 = full)
- Time: s (seconds), ms (milliseconds for timestamps)

### Sign Conventions

- **Generation**: Negative power (PV: `W < 0`)
- **Charging**: Positive power/current (Battery: `W > 0`, `A > 0`)
- **Discharging**: Negative power/current (Battery: `W < 0`, `A < 0`)
- **Import**: Positive power (Meter: `W > 0`)
- **Export**: Negative power (Meter: `W < 0`)
- **Energy Totals**: Always positive values in `total_import_Wh`, `total_export_Wh`, `total_charge_Wh`, `total_discharge_Wh`, and `total_generation_Wh`

### Field Naming Convention

The flattened structure uses snake_case naming while preserving proper unit casing:

- **Units preserved**: `W`, `V`, `A`, `Hz`, `C`, `Wh`, `s`
- **Hierarchical paths flattened**: `MPPT1.V` → `mppt1_V`, `L1.A` → `L1_A`
- **Compound fields**: `SoC.nom.fract` → `SoC_nom_fract`
- **Energy paths**: `total.export.Wh` → `total_export_Wh`

## Data Models

### BaseDeviceData

Base class structure with common fields:

```json
{
  "type": "Device",
  "make": "Deye",
  "timestamp": 1755701251122,
  "read_time_ms": 42
}
```

| Field          | Unit         | Data Type | Description                                   |
| -------------- | ------------ | --------- | --------------------------------------------- |
| `type`         | -            | string    | Object type ("PV", "Battery", "Meter")        |
| `make`         | -            | string    | Manufacturer/brand name (optional)            |
| `timestamp`    | milliseconds | integer   | Timestamp of reading start (optional)         |
| `read_time_ms` | milliseconds | integer   | Time taken to complete the reading (optional) |

### PV Data Model

Inherits from `BaseDeviceData` and adds PV-specific fields:

```json
{
  "W": -1500,
  "rated_power_W": 3000,
  "mppt1_V": 400,
  "mppt1_A": -3.75,
  "mppt2_V": 380,
  "mppt2_A": -3.68,
  "heatsink_C": 45,
  "total_generation_Wh": 15000
}
```

| Field                 | Unit | Data Type | Description                            |
| --------------------- | ---- | --------- | -------------------------------------- |
| `W`                   | W    | float     | Active Power (negative for generation) |
| `rated_power_W`       | W    | float     | System Rated Power                     |
| `mppt1_V`             | V    | float     | MPPT1 Voltage                          |
| `mppt1_A`             | A    | float     | MPPT1 Current                          |
| `mppt2_V`             | V    | float     | MPPT2 Voltage                          |
| `mppt2_A`             | A    | float     | MPPT2 Current                          |
| `heatsink_C`          | °C   | float     | Inverter Temperature                   |
| `total_generation_Wh` | Wh   | integer   | Total Energy Generated                 |

### Battery Data Model

Inherits from `BaseDeviceData` and adds battery-specific fields:

```json
{
  "W": 500,
  "A": 10.5,
  "V": 48.2,
  "SoC_nom_fract": 0.75,
  "heatsink_C": 25,
  "total_charge_Wh": 8000,
  "total_discharge_Wh": 7200
}
```

| Field                | Unit     | Data Type | Description                          |
| -------------------- | -------- | --------- | ------------------------------------ |
| `W`                  | W        | float     | Active Power (+ charge, - discharge) |
| `A`                  | A        | float     | Current (+ charge, - discharge)      |
| `V`                  | V        | float     | Voltage                              |
| `SoC_nom_fract`      | fraction | float     | State of Charge (0.0-1.0)            |
| `heatsink_C`         | °C       | float     | Battery Temperature                  |
| `total_charge_Wh`    | Wh       | integer   | Total Energy Charged                 |
| `total_discharge_Wh` | Wh       | integer   | Total Energy Discharged              |

### Meter Data Model

Inherits from `BaseDeviceData` and adds meter-specific fields:

```json
{
  "W": 1200,
  "Hz": 50.0,
  "L1_V": 230,
  "L1_A": 5.2,
  "L1_W": 400,
  "L2_V": 229,
  "L2_A": 5.1,
  "L2_W": 380,
  "L3_V": 231,
  "L3_A": 5.3,
  "L3_W": 420,
  "total_import_Wh": 25000,
  "total_export_Wh": 18000
}
```

| Field             | Unit | Data Type | Description                             |
| ----------------- | ---- | --------- | --------------------------------------- |
| `W`               | W    | float     | Total Active Power (+ import, - export) |
| `Hz`              | Hz   | float     | Grid Frequency                          |
| `L1_V`            | V    | float     | L1 Phase Voltage                        |
| `L1_A`            | A    | float     | L1 Phase Current                        |
| `L1_W`            | W    | float     | L1 Phase Power                          |
| `L2_V`            | V    | float     | L2 Phase Voltage                        |
| `L2_A`            | A    | float     | L2 Phase Current                        |
| `L2_W`            | W    | float     | L2 Phase Power                          |
| `L3_V`            | V    | float     | L3 Phase Voltage                        |
| `L3_A`            | A    | float     | L3 Phase Current                        |
| `L3_W`            | W    | float     | L3 Phase Power                          |
| `total_import_Wh` | Wh   | integer   | Total Energy Imported                   |
| `total_export_Wh` | Wh   | integer   | Total Energy Exported                   |

## MQTT Integration

### Topic Structure

Harvested data is published to MQTT topics using the following structure:

```
sourceful/<wallet>/<type>/<device_sn>/<format>/<version>
```

Where:

- `sourceful/<wallet>`: Root topic, with `<wallet>` set by the MQTT client
- `<type>`: Data type (e.g., PV, Battery, Meter)
- `<device_sn>`: Device serial number
- `<format>`: Data format (e.g., json, protobuf, binary)
- `<version>`: Data model version (e.g., v1)

Example topic: `sourceful/0xABCDEF1234567890/PV/ABC123/json/v1`
