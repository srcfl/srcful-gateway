# Data Models

The Srcful Gateway uses nested data models to represent energy system measurements from distributed energy resources (DER). The structure provides clean JSON output with direct numeric values and organized nested objects.

## Core Structure

### Timestamp
All data objects include:
- **ts**: Timestamp in milliseconds
- **type**: Object type ("PV", "Battery", "Meter")

### DERData
Root data structure containing up to three subsystems:
- **pv**: Photovoltaic system data
- **battery**: Battery storage system data  
- **meter**: Grid meter data

## PV Data Model

```json
{
  "ts": 1755701251122,
  "type": "PV",
  "W": -1500,
  "active_power": 3000,
  "MPPT1": {
    "V": 400,
    "A": -3.75
  },
  "MPPT2": {
    "V": 380,
    "A": -3.68
  },
  "heatsink_tmp": {
    "C": 45
  },
  "total": {
    "export": {
      "Wh": 15000
    }
  }
}
```

| Field | Unit | Description |
|-------|------|-------------|
| `W` | W | Active Power (negative for generation) |
| `active_power` | W | Maximum Power Rating |
| `MPPT1/2.V` | V | DC Voltage per MPPT |
| `MPPT1/2.A` | A | DC Current per MPPT (negative) |
| `heatsink_tmp.C` | °C | Inverter Temperature |
| `total.export.Wh` | Wh | Total Energy Generated |

## Battery Data Model

```json
{
  "ts": 1755701251122,
  "type": "Battery",
  "W": 500,
  "A": 10.5,
  "V": 48.2,
  "SoC": {
    "nom": {
      "fract": 0.75
    }
  },
  "Tmp": {
    "C": 25
  },
  "total": {
    "import": {
      "Wh": 8000
    },
    "export": {
      "Wh": 7200
    },
    "uptime": {
      "s": 123456
    }
  }
}
```

| Field | Unit | Description |
|-------|------|-------------|
| `W` | W | Active Power (+ charge, - discharge) |
| `A` | A | Current (+ charge, - discharge) |
| `V` | V | Voltage |
| `SoC.nom.fract` | fraction | State of Charge (0.0-1.0) |
| `Tmp.C` | °C | Battery Temperature |
| `total.import.Wh` | Wh | Total Energy Charged |
| `total.export.Wh` | Wh | Total Energy Discharged |
| `total.uptime.s` | seconds | System Uptime |

## Meter Data Model

```json
{
  "ts": 1755701251122,
  "type": "Meter",
  "W": 1200,
  "Hz": 50.0,
  "L1": {
    "V": 230,
    "A": 5.2,
    "W": 400
  },
  "L2": {
    "V": 229,
    "A": 5.1,
    "W": 380
  },
  "L3": {
    "V": 231,
    "A": 5.3,
    "W": 420
  },
  "total": {
    "import": {
      "Wh": 25000
    },
    "export": {
      "Wh": 18000
    }
  }
}
```

| Field | Unit | Description |
|-------|------|-------------|
| `W` | W | Total Active Power (+ import, - export) |
| `Hz` | Hz | Grid Frequency |
| `L1/L2/L3.V` | V | Phase Voltage |
| `L1/L2/L3.A` | A | Phase Current |
| `L1/L2/L3.W` | W | Phase Power |
| `total.import.Wh` | Wh | Total Energy Imported |
| `total.export.Wh` | Wh | Total Energy Exported |

## Sign Conventions

- **Generation**: Negative power (PV: `W < 0`)
- **Charging**: Positive power/current (Battery: `W > 0`, `A > 0`)
- **Discharging**: Negative power/current (Battery: `W < 0`, `A < 0`)
- **Import**: Positive power (Meter: `W > 0`)
- **Export**: Negative power (Meter: `W < 0`)
- **Energy Totals**: Always positive values in `total.import.Wh` and `total.export.Wh`

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

Example serialized PV data:
```json
{
  "pv": {
    "ts": 1755701251122,
    "type": "PV",
    "W": -5000.0,
    "active_power": 6000.0,
    "heatsink_tmp": {
      "C": 45.0
    },
    "MPPT1": {
      "V": 380.0,
      "A": -12.5
    },
    "total": {
      "export": {
        "Wh": 25000
      }
    }
  }
}
```

This standardized approach ensures consistent data interpretation across the Srcful ecosystem while maintaining compatibility with SunSpec specifications.
