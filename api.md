# Server 

## initilize 
POST `localhost:8090/api/initialize`
```json
{
  "wallet": "walletaddresswalletaddresswalletaddresswalletaddress"
}
```


## logger 

POST `localhost:8090/api/logger`

```json
{
  "logger": "server.inverters.InverterTCP",
  "level": "INFO"
}
```

## inverter

### invertertcp

POST `http://localhost:8080/api/invertertcp`

```json
{
  "ip": "192.168.50.162", 
  "port": 502, 
  "type": "solaredge", 
  "address": 1
}
```

### inverterrtu

POST `http://localhost:8080/api/inverterrtu`

```json
{
  "port": "/dev/serial0", 
  "baudrate": 9600, 
  "bytesize": 8, 
  "parity": "N", 
  "stopbits": 1, 
  "type": "lqt40s", 
  "address": 1
}
```

## modbus 

POST `http://localhost:8090/api/inverter/modbus`

```json
{
  "commands": [
    {
        "type": "write",
        "startingAddress": "10",
        "values": ["0", "1", "2"]
    },
    {
        "type": "pause",
        "duration": "2000",
    }
  ]
}
```

GET `http://localhost:8090/api/inverter/modbus/input/40000?type=float&size=4&endianess=big`


## wifi 

POST `http://localhost:8090/api/wifi`

```json
{
  "ssid": "kingfisher",
  "psk": "kingfisher"
}
```