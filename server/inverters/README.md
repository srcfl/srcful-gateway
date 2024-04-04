A detailed table separating the data types for grid frequency (Hz) and power (W) for each inverter, including the starting Modbus register and the number of registers (or words) to read:

| Brand          | Measurement | Data Type | Starting Modbus Register | Number of Registers |
| -------------- | ----------- | --------- | ------------------------ | ------------------- |
| Huawei         | Frequency   | UInt16    | 32085                    | 1                   |
| Huawei         | Power       | Int32     | 32064                    | 2                   |
| SolarEdge      | Frequency   | UInt16    | 40085                    | 2                   |
| SolarEdge      | Power       | Int16     | 40100                    | 2                   |
| SunGrow        | Frequency   | UInt16    | 5035                     | 1                   |
| SunGrow        | Power       | Int32     | 5016                     | 2                   |
| SunGrow Hybrid | Frequency   | UInt16    | 5035                     | 1                   |
| SunGrow Hybrid | Power       | Int32     | 5016                     | 2                   |
| SMA            | Frequency   | UInt32    | 30803                    | 2                   |
| SMA            | Power       | Int32     | 30775                    | 2                   |
| Fronius        | Frequency   | Float32   | 40093                    | 2                   |
| Fronius        | Power       | Float32   | 40107                    | 2                   |
