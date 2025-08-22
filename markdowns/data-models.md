# Data Models

The structure provides clean JSON output with direct numeric values and organized nested objects.

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
  "MPPT1": {
    "V": 400,
    "A": -3.75
  },
  "MPPT2": {
    "V": 380,
    "A": -3.68
  },
  "heatsink": {
    "C": 45
  },
  "total": {
    "export": {
      "Wh": 15000
    }
  }
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
| `MPPT1.V`         | V            | MPPT1 Voltage                          |
| `MPPT1.A`         | A            | MPPT1 Current                          |
| `MPPT2.V`         | V            | MPPT2 Voltage                          |
| `MPPT2.A`         | A            | MPPT2 Current                          |
| `heatsink.C`      | °C           | Inverter Temperature                   |
| `total.export.Wh` | Wh           | Total Energy Generated                 |

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
  "SoC": {
    "nom": {
      "fract": 0.75
    }
  },
  "temperature": {
    "C": 25
  },
  "total": {
    "import": {
      "Wh": 8000
    },
    "export": {
      "Wh": 7200
    }
  }
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
| `SoC.nom.fract`   | fraction     | State of Charge (0.0-1.0)            |
| `temperature.C`   | °C           | Battery Temperature                  |
| `total.import.Wh` | Wh           | Total Energy Charged                 |
| `total.export.Wh` | Wh           | Total Energy Discharged              |

## Meter Data Model

```json
{
  "timestamp": 1755701251122,
  "type": "Meter",
  "make": "Deye",
  "delta": 35,
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

| Field             | Unit         | Description                             |
| ----------------- | ------------ | --------------------------------------- |
| `timestamp`       | milliseconds | Timestamp of reading start              |
| `type`            | -            | Object type ("Meter")                   |
| `make`            | -            | Manufacturer/brand name                 |
| `delta`           | milliseconds | Time taken to complete the reading      |
| `W`               | W            | Total Active Power (+ import, - export) |
| `Hz`              | Hz           | Grid Frequency                          |
| `L1.V`            | V            | L1 Phase Voltage                        |
| `L1.A`            | A            | L1 Phase Current                        |
| `L1.W`            | W            | L1 Phase Power                          |
| `L2.V`            | V            | L2 Phase Voltage                        |
| `L2.A`            | A            | L2 Phase Current                        |
| `L2.W`            | W            | L2 Phase Power                          |
| `L3.V`            | V            | L3 Phase Voltage                        |
| `L3.A`            | A            | L3 Phase Current                        |
| `L3.W`            | W            | L3 Phase Power                          |
| `total.import.Wh` | Wh           | Total Energy Imported                   |
| `total.export.Wh` | Wh           | Total Energy Exported                   |

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
    "timestamp": 1755701251122,
    "type": "PV",
    "make": "Deye",
    "W": -5000.0,
    "rating": 6000.0,
    "heatsink": {
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
