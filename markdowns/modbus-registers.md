## Register Reference Tables by Make

The following tables have 4 fields in common:

- **type** - This is the type of the data model (e.g., "PV", "Battery", "Meter").
- **make** - This is the manufacturer/brand of the device.
- **ts** - This is the timestamp of the start of the reading (milliseconds).
- **reading_duration_ms** - Time taken to complete the reading (milliseconds).

### PV Register Table

| Field                    | Unit | Description                   | Huawei | Sungrow | Deye    |
| ------------------------ | ---- | ----------------------------- | ------ | ------- | ------- |
| PV - type                | str  | Object type ("PV")            | -      | -       | -       |
| PV - make                | str  | Manufacturer/brand            | -      | -       | -       |
| PV - ts                  | int  | Timestamp (ms)                | -      | -       | -       |
| PV - reading_duration_ms | int  | Elapsed time for reading (ms) | -      | -       | -       |
| PV - rated_power         | W    | Rated Power                   | 30073  | 5000    | 20      |
| PV - W                   | W    | PV Active Power               | 32064  | 5016    | 672-675 |
| PV - MPPT1.V             | V    | MPPT1 Voltage                 | 32016  | 5010    | 676     |
| PV - MPPT1.A             | A    | MPPT1 Current                 | 32017  | 5011    | 677     |
| PV - MPPT2.V             | V    | MPPT2 Voltage                 | 32018  | 5012    | 678     |
| PV - MPPT2.A             | A    | MPPT2 Current                 | 32019  | 5013    | 679     |
| PV - heatsink_tmp.C      | °C   | Heatsink Temperature          | 32087  | 5007    | 541     |
| PV - total.export.Wh     | Wh   | Total Energy Generated        | 32106  | 13002   | 534     |

### Battery Register Table

| Field                         | Unit     | Description                   | Huawei | Sungrow | Deye |
| ----------------------------- | -------- | ----------------------------- | ------ | ------- | ---- |
| Battery - type                | str      | Object type ("Battery")       | -      | -       | -    |
| Battery - make                | str      | Manufacturer/brand            | -      | -       | -    |
| Battery - ts                  | int      | Timestamp (ms)                | -      | -       | -    |
| Battery - reading_duration_ms | int      | Elapsed time for reading (ms) | -      | -       | -    |
| Battery - W                   | W        | Battery Power                 | 37001  | 13021   | 590  |
| Battery - A                   | A        | Battery Current               | 37021  | 13020   | 591  |
| Battery - V                   | V        | Battery Voltage               | 37003  | 13019   | 587  |
| Battery - SoC.nom.fract       | fraction | State of Charge               | 37004  | 13022   | 588  |
| Battery - Tmp.C               | °C       | Battery Temperature           | 37022  | 13024   | 217  |
| Battery - total.import.Wh     | Wh       | Total Energy Charged          | 37066  | 13026   | 516  |
| Battery - total.export.Wh     | Wh       | Total Energy Discharged       | 37068  | 13040   | 518  |

### Meter Register Table

| Field                       | Unit | Description                   | Huawei | Sungrow | Deye |
| --------------------------- | ---- | ----------------------------- | ------ | ------- | ---- |
| Meter - type                | str  | Object type ("Meter")         | -      | -       | -    |
| Meter - make                | str  | Manufacturer/brand            | -      | -       | -    |
| Meter - ts                  | int  | Timestamp (ms)                | -      | -       | -    |
| Meter - reading_duration_ms | int  | Elapsed time for reading (ms) | -      | -       | -    |
| Meter - W                   | W    | Meter Active Power            | 37113  | 5035    | 619  |
| Meter - Hz                  | Hz   | Grid Frequency                | 37118  | 5035    | 609  |
| Meter - L1.V                | V    | L1 Phase Voltage              | 37101  | 5018    | 598  |
| Meter - L1.A                | A    | L1 Phase Current              | 37107  | 13030   | 610  |
| Meter - L1.W                | W    | L1 Phase Power                | 37132  | 5602    | 616  |
| Meter - L2.V                | V    | L2 Phase Voltage              | 37103  | 5019    | 599  |
| Meter - L2.A                | A    | L2 Phase Current              | 37109  | 13031   | 611  |
| Meter - L2.W                | W    | L2 Phase Power                | 37134  | 5604    | 617  |
| Meter - L3.V                | V    | L3 Phase Voltage              | 37105  | 5020    | 600  |
| Meter - L3.A                | A    | L3 Phase Current              | 37111  | 13032   | 612  |
| Meter - L3.W                | W    | L3 Phase Power                | 37136  | 5606    | 618  |
| Meter - total.import.Wh     | Wh   | Total Energy Imported         | 37121  | 13033   | 522  |
| Meter - total.export.Wh     | Wh   | Total Energy Exported         | 37119  | 13033   | 524  |
