A detailed table separating the data types for grid frequency (Hz) and power (W) for each inverter, including the starting Modbus register and the number of registers (or words) to read:

| Brand          | Measurement | Data Type | Scale | Function Code | Starting Modbus Register | Number of Registers |
| -------------- | ----------- | --------- | ----- | ------------- | ------------------------ | ------------------- |
| Huawei         | Frequency   | UInt16    |       | 03            | 32085                    | 1                   |
| Huawei         | Power       | Int32     |       | 03            | 32064                    | 2                   |
| SolarEdge      | Frequency   | UInt16    |       | 03            | 40085                    | 1                   |
| SolarEdge      | Power       | Int16     |       | 03            | 40100                    | 1                   |
| SunGrow        | Frequency   | UInt16    |       | 04            | 5035                     | 1                   |
| SunGrow        | Power       | Int32     |       | 04            | 5016                     | 2                   |
| SunGrow Hybrid | Frequency   | UInt16    |       | 04            | 5035                     | 1                   |
| SunGrow Hybrid | Power       | Int32     |       | 04            | 5016                     | 2                   |
| SMA            | Frequency   | UInt32    |       | 03/04         | 30803                    | 2                   |
| SMA            | Power       | Int32     |       | 03/04         | 30775                    | 2                   |
| Fronius        | Frequency   | Float32   |       | 03            | 40093                    | 2                   |
| Fronius        | Power       | Float32   |       | 03            | 40107                    | 2                   |
| Deye           | Frequency   |           | 1     | -             | 608                      | 1                   |
| Deye           | Power       |           |       | -             |                          | 1                   |
| Deye Hybrid    | Frequency   |           | 1     | -             | 608                      |                     |
| Deye Hybrid    | Power       |           |       | -             |                          |                     |
| Growatt        | Frequency   |           |       | -             | 36                       |                     |
| Growatt        | Power       |           | 0.1   | -             | 3000                     | 2                   |
| Goodwe         | Frequency   | INT16U    | 0.01  | -             | 0518                     | 1                   |
| Goodwe         | Power       | INT16S    | 1     | -             | 052B                     | 1                   |
