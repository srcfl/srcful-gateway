# Data Models

## MQTT Topic Structure

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

Example topic:

sourceful/0xABCDEF1234567890/PV/ABC123/json/v1

The structure provides clean JSON output with direct numeric values and organized flattened fields using snake_case naming conventions while preserving proper unit casing.

## Core Structure

### Timestamp

All data objects include:

- **timestamp**: Timestamp in milliseconds
- **type**: Object type ("PV", "Battery", "Meter")
- **make**: Manufacturer/brand (e.g., "Deye", "Huawei", "Solis", "SunGrow")
- **delta**: Elapsed time to perform the reading (milliseconds)

### DERData

Root data structure containing up to three subsystems:

- **pv**: Photovoltaic system data
- **battery**: Battery storage system data
- **meter**: Meter data

## PV Data Model

```json
{
  "timestamp": 1755701251122,
  "type": "PV",
  "make": "Deye",
  "delta": 42,
  "W": -1500,
  "rating": 3000,
  "mppt1_V": 400,
  "mppt1_A": -3.75,
  "mppt2_V": 380,
  "mppt2_A": -3.68,
  "heatsink_C": 45,
  "total_export_Wh": 15000
}
```

| Field             | Unit         | Description                            |
| ----------------- | ------------ | -------------------------------------- |
| `timestamp`       | milliseconds | Timestamp of reading start             |
| `type`            | -            | Object type ("PV")                     |
| `make`            | -            | Manufacturer/brand name                |
| `delta`           | milliseconds | Time taken to complete the reading     |
| `W`               | W            | Active Power (negative for generation) |
| `rating`          | W            | Power rating                           |
| `mppt1_V`         | V            | MPPT1 Voltage                          |
| `mppt1_A`         | A            | MPPT1 Current                          |
| `mppt2_V`         | V            | MPPT2 Voltage                          |
| `mppt2_A`         | A            | MPPT2 Current                          |
| `heatsink_C`      | °C           | Inverter Temperature                   |
| `total_export_Wh` | Wh           | Total Energy Generated                 |

## Battery Data Model

```json
{
  "timestamp": 1755701251122,
  "type": "Battery",
  "make": "Deye",
  "delta": 38,
  "W": 500,
  "A": 10.5,
  "V": 48.2,
  "SoC_nom_fract": 0.75,
  "heatsink_C": 25,
  "total_import_Wh": 8000,
  "total_export_Wh": 7200
}
```

| Field             | Unit         | Description                          |
| ----------------- | ------------ | ------------------------------------ |
| `timestamp`       | milliseconds | Timestamp of reading start           |
| `type`            | -            | Object type ("Battery")              |
| `make`            | -            | Manufacturer/brand name              |
| `delta`           | milliseconds | Time taken to complete the reading   |
| `W`               | W            | Active Power (+ charge, - discharge) |
| `A`               | A            | Current (+ charge, - discharge)      |
| `V`               | V            | Voltage                              |
| `SoC_nom_fract`   | fraction     | State of Charge (0.0-1.0)            |
| `heatsink_C`      | °C           | Battery Temperature                  |
| `total_import_Wh` | Wh           | Total Energy Charged                 |
| `total_export_Wh` | Wh           | Total Energy Discharged              |

## Meter Data Model

```json
{
  "timestamp": 1755701251122,
  "type": "Meter",
  "make": "Deye",
  "delta": 35,
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

| Field             | Unit         | Description                             |
| ----------------- | ------------ | --------------------------------------- |
| `timestamp`       | milliseconds | Timestamp of reading start              |
| `type`            | -            | Object type ("Meter")                   |
| `make`            | -            | Manufacturer/brand name                 |
| `delta`           | milliseconds | Time taken to complete the reading      |
| `W`               | W            | Total Active Power (+ import, - export) |
| `Hz`              | Hz           | Grid Frequency                          |
| `L1_V`            | V            | L1 Phase Voltage                        |
| `L1_A`            | A            | L1 Phase Current                        |
| `L1_W`            | W            | L1 Phase Power                          |
| `L2_V`            | V            | L2 Phase Voltage                        |
| `L2_A`            | A            | L2 Phase Current                        |
| `L2_W`            | W            | L2 Phase Power                          |
| `L3_V`            | V            | L3 Phase Voltage                        |
| `L3_A`            | A            | L3 Phase Current                        |
| `L3_W`            | W            | L3 Phase Power                          |
| `total_import_Wh` | Wh           | Total Energy Imported                   |
| `total_export_Wh` | Wh           | Total Energy Exported                   |

## Sign Conventions

- **Generation**: Negative power (PV: `W < 0`)
- **Charging**: Positive power/current (Battery: `W > 0`, `A > 0`)
- **Discharging**: Negative power/current (Battery: `W < 0`, `A < 0`)
- **Import**: Positive power (Meter: `W > 0`)
- **Export**: Negative power (Meter: `W < 0`)
- **Energy Totals**: Always positive values in `total_import_Wh` and `total_export_Wh`

## Units

All measurements use base SI units:

- Power: W (watts)
- Energy: Wh (watt-hours)
- Voltage: V (volts)
- Current: A (amperes)
- Frequency: Hz (hertz)
- Temperature: °C (Celsius)
- State of Charge: fraction (0.0 = empty, 1.0 = full)
- Time: s (seconds), ms (milliseconds for timestamps)

## Field Naming Convention

The flattened structure uses snake_case naming while preserving proper unit casing:

- **Units preserved**: `W`, `V`, `A`, `Hz`, `C`, `Wh`, `s`
- **Hierarchical paths flattened**: `MPPT1.V` → `mppt1_V`, `L1.A` → `L1_A`
- **Compound fields**: `SoC.nom.fract` → `SoC_nom_fract`
- **Energy paths**: `total.export.Wh` → `total_export_Wh`

Example serialized PV data:

```json
{
  "pv": {
    "timestamp": 1755701251122,
    "type": "PV",
    "make": "Deye",
    "W": -5000.0,
    "rating": 6000.0,
    "heatsink_C": 45.0,
    "mppt1_V": 380.0,
    "mppt1_A": -12.5,
    "total_export_Wh": 25000
  }
}
```

## Battery Data Model

```json
{
  "timestamp": 1755701251122,
  "type": "Battery",
  "make": "Deye",
  "delta": 38,
  "w": 500,
  "a": 10.5,
  "v": 48.2,
  "soc_nom_fract": 0.75,
  "heatsink_c": 25,
  "total_import_wh": 8000,
  "total_export_wh": 7200
}
```

| Field             | Unit         | Description                          |
| ----------------- | ------------ | ------------------------------------ |
| `timestamp`       | milliseconds | Timestamp of reading start           |
| `type`            | -            | Object type ("Battery")              |
| `make`            | -            | Manufacturer/brand name              |
| `delta`           | milliseconds | Time taken to complete the reading   |
| `w`               | W            | Active Power (+ charge, - discharge) |
| `a`               | A            | Current (+ charge, - discharge)      |
| `v`               | V            | Voltage                              |
| `soc_nom_fract`   | fraction     | State of Charge (0.0-1.0)            |
| `heatsink_c`      | °C           | Battery Temperature                  |
| `total_import_wh` | Wh           | Total Energy Charged                 |
| `total_export_wh` | Wh           | Total Energy Discharged              |

## Meter Data Model

```json
{
  "timestamp": 1755701251122,
  "type": "Meter",
  "make": "Deye",
  "delta": 35,
  "w": 1200,
  "hz": 50.0,
  "l1_v": 230,
  "l1_a": 5.2,
  "l1_w": 400,
  "l2_v": 229,
  "l2_a": 5.1,
  "l2_w": 380,
  "l3_v": 231,
  "l3_a": 5.3,
  "l3_w": 420,
  "total_import_wh": 25000,
  "total_export_wh": 18000
}
```

| Field             | Unit         | Description                             |
| ----------------- | ------------ | --------------------------------------- |
| `timestamp`       | milliseconds | Timestamp of reading start              |
| `type`            | -            | Object type ("Meter")                   |
| `make`            | -            | Manufacturer/brand name                 |
| `delta`           | milliseconds | Time taken to complete the reading      |
| `w`               | W            | Total Active Power (+ import, - export) |
| `hz`              | Hz           | Grid Frequency                          |
| `l1_v`            | V            | L1 Phase Voltage                        |
| `l1_a`            | A            | L1 Phase Current                        |
| `l1_w`            | W            | L1 Phase Power                          |
| `l2_v`            | V            | L2 Phase Voltage                        |
| `l2_a`            | A            | L2 Phase Current                        |
| `l2_w`            | W            | L2 Phase Power                          |
| `l3_v`            | V            | L3 Phase Voltage                        |
| `l3_a`            | A            | L3 Phase Current                        |
| `l3_w`            | W            | L3 Phase Power                          |
| `total_import_wh` | Wh           | Total Energy Imported                   |
| `total_export_wh` | Wh           | Total Energy Exported                   |

## Sign Conventions

- **Generation**: Negative power (PV: `w < 0`)
- **Charging**: Positive power/current (Battery: `w > 0`, `a > 0`)
- **Discharging**: Negative power/current (Battery: `w < 0`, `a < 0`)
- **Import**: Positive power (Meter: `w > 0`)
- **Export**: Negative power (Meter: `w < 0`)
- **Energy Totals**: Always positive values in `total_import_wh` and `total_export_wh`

## Units

All measurements use base SI units:

- Power: W (watts)
- Energy: Wh (watt-hours)
- Voltage: V (volts)
- Current: A (amperes)
- Frequency: Hz (hertz)
- Temperature: °C (Celsius)
- State of Charge: fraction (0.0 = empty, 1.0 = full)
- Time: s (seconds), ms (milliseconds for timestamps)

## Field Naming Convention

All field names use snake_case format, replacing the previous hierarchical structure:

- **MPPT data**: `MPPT1.V` → `mppt1_v`, `MPPT2.A` → `mppt2_a`
- **Phase data**: `L1.V` → `l1_v`, `L2.W` → `l2_w`, `L3.A` → `l3_a`
- **Temperature**: `heatsink.C` → `heatsink_c`
- **State of Charge**: `SoC.nom.fract` → `soc_nom_fract`
- **Energy totals**: `total.export.Wh` → `total_export_wh`, `total.import.Wh` → `total_import_wh`
- **Power/Current/Voltage**: `W` → `w`, `A` → `a`, `V` → `v`, `Hz` → `hz`

Example serialized PV data:

```json
{
  "pv": {
    "timestamp": 1755701251122,
    "type": "PV",
    "make": "Deye",
    "w": -5000.0,
    "rating": 6000.0,
    "heatsink_c": 45.0,
    "mppt1_v": 380.0,
    "mppt1_a": -12.5,
    "total_export_wh": 25000
  }
}
```
