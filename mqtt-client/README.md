# MQTT Client for Srcful Gateway

This container provides an MQTT client that connects to an MQTT broker using TLS and JWT authentication. It automatically retrieves the gateway's serialNumber from `/api/crypto` and creates JWT tokens via `/api/jwt/create` for secure authentication. It subscribes to modbus requests on the `iamcat/modbus/request` topic, publishes modbus responses to the `iamcat/modbus/response` topic, and publishes gateway state to the `iamcat/state` topic every 5 seconds.

## Features

- **TLS/SSL Connection**: Secure connection using the provided root CA certificate
- **JWT Authentication**: Automatic JWT token generation using gateway's crypto chip
- **Dynamic Credentials**: Uses serialNumber as username and JWT as password
- **Modbus Request Subscription**: Listens for modbus commands on `iamcat/modbus/request` topic
- **Modbus HTTP Bridge**: Converts MQTT modbus commands to HTTP requests to web container
- **Modbus Response Publishing**: Publishes modbus responses to `iamcat/modbus/response` topic
- **State Publishing**: Publishes gateway state to `iamcat/state` topic every 5 seconds
- **Health Check**: Built-in container health monitoring
- **Non-root User**: Runs with reduced privileges for security

## Configuration

The MQTT client is configured through the `mqtt.env` file located in the `mqtt-client` directory:

### Required Environment Variables

- `MQTT_BROKER_HOST`: The hostname/IP of your MQTT broker
- `MQTT_BROKER_PORT`: The port for secure MQTT connection (typically 8883)
- `WEB_CONTAINER_HOST`: The web container host for API calls (typically localhost)
- `WEB_CONTAINER_PORT`: The web container port for API calls (typically 5000)

### Optional Environment Variables

- `MQTT_ROOT_CA`: Custom root CA certificate for TLS verification (usually not needed for EMQX Cloud)

### Authentication

The client uses JWT authentication automatically:

1. Retrieves the gateway's `serialNumber` from `/api/crypto`
2. Creates a JWT token via `/api/jwt/create` with 5-minute expiration
3. Uses `serialNumber` as username and JWT as password for MQTT connection

### Setup Configuration

1. Copy the example configuration file:

   ```bash
   cd mqtt-client
   cp mqtt.env.example mqtt.env
   ```

2. Update the values in `mqtt-client/mqtt.env`:

   ```env
   MQTT_BROKER_HOST=my-broker.example.com
   MQTT_BROKER_PORT=8883
   WEB_CONTAINER_HOST=localhost
   WEB_CONTAINER_PORT=5000
   # Authentication handled automatically via JWT tokens
   # MQTT_ROOT_CA is optional for custom certificates
   ```

   **Important**: If you need to replace the certificate, format it as a single line with `\n` escape sequences:

   ```env
   MQTT_ROOT_CA="-----BEGIN CERTIFICATE-----\nYOUR_CERT_CONTENT_HERE\n-----END CERTIFICATE-----"
   ```

**Security Note**: The `mqtt.env` file contains sensitive information like passwords and certificates. Make sure to:

- Never commit this file to version control with real credentials
- Keep it secure and restrict access to authorized personnel only
- The `.gitignore` file is configured to exclude `*.env` files from git

## Topics

### Modbus Request Topic: `iamcat/modbus/request`

Send JSON commands for Modbus operations on inverter devices:

#### Modbus Read Operation (Function Code 3 or 4)

For reading from inverter devices via Modbus:

```json
{
  "function_code": 3,
  "device_id": "A2332407312",
  "address": 10056,
  "size": 1,
  "type": "U16",
  "endianess": "big",
  "scale_factor": 1
}
```

This will make an HTTP request to: `/api/inverter/modbus?device_id=A2332407312&function_code=3&address=10056&size=1&type=U16&endianess=big&scale_factor=1`

#### Modbus Write Operation (Function Code 16)

For writing to inverter devices via Modbus:

```json
{
  "function_code": 16,
  "device_id": "A2332407312",
  "address": 33207,
  "values": 170,
  "type": "U16"
}
```

This will make an HTTP request to: `/api/inverter/modbus?device_id=A2332407312&address=33207&function_code=16&values=170&type=U16`

### Modbus Response Topic: `iamcat/modbus/response`

The client publishes modbus operation responses:

#### Modbus Response

When a modbus operation (read or write) is performed, the response is published to the modbus response topic:

```json
{
  "timestamp": "2024-08-03T15:05:30.123456Z",
  "type": "modbus_response",
  "request": {
    "function_code": 3,
    "device_id": "A2332407312",
    "address": 10056,
    "size": 1,
    "type": "U16",
    "endianess": "big",
    "scale_factor": 1
  },
  "response": {
    "success": true,
    "data": [42],
    "device_id": "A2332407312"
  }
}
```

### State Topic: `iamcat/state`

The client publishes gateway state information every 5 seconds by fetching from the web container's `/api/state` endpoint:

#### Gateway State

The gateway state is fetched from the web container's REST API:

```json
{
  "timestamp": "2024-08-03T15:05:30.123456Z",
  "type": "gateway_state",
  "status": "online",
  "uptime": 1234567890.123,
  "version": "1.0.0",
  "connected_devices": 3,
  "network_status": "connected",
  "memory_usage": 45.2,
  "cpu_usage": 12.5
}
```

#### Fallback State

If the web container API is unavailable, a fallback state is published:

```json
{
  "timestamp": "2024-08-03T15:05:30.123456Z",
  "type": "gateway_state",
  "status": "api_unavailable",
  "uptime": 1234567890.123,
  "version": "1.0.0",
  "error": "Failed to fetch state from web container"
}
```

#### Modbus Response

When a modbus operation (read or write) is performed, the response is published to the modbus response topic:

```json
{
  "timestamp": "2024-08-03T15:05:30.123456Z",
  "type": "modbus_response",
  "request": {
    "function_code": 3,
    "device_id": "A2332407312",
    "address": 10056,
    "size": 1,
    "type": "U16",
    "endianess": "big",
    "scale_factor": 1
  },
  "response": {
    "success": true,
    "data": [42],
    "device_id": "A2332407312"
  }
}
```

## Usage

### Build and Run

The container is automatically built and started when you run:

```bash
docker-compose up mqtt-client
```

### Logs

View the container logs:

```bash
docker-compose logs -f mqtt-client
```

### Health Check

Check if the container is healthy:

```bash
docker-compose ps mqtt-client
```

## Development

### Local Testing

To test the MQTT client locally:

1. Install dependencies:

   ```bash
   cd mqtt-client
   pip install -r requirements.txt
   ```

2. Set environment variables:

   ```bash
   export MQTT_BROKER_HOST=your-broker.com
   export MQTT_BROKER_PORT=8883
   export MQTT_USERNAME=your-username
   export MQTT_PASSWORD=your-password
   export MQTT_ROOT_CA="-----BEGIN CERTIFICATE-----..."
   ```

3. Run the client:
   ```bash
   python mqtt_client.py
   ```

### Customization

To customize the harvest data or add new control commands:

1. Edit `mqtt_client.py`
2. Modify the `handle_control_message()` method for new commands
3. Update the `generate_sample_harvest_data()` method for different data
4. Rebuild the container: `docker-compose build mqtt-client`

## Security Notes

- The container runs as a non-root user (`mqttuser`)
- TLS certificate verification is enabled
- Credentials are passed via environment variables (not stored in the image)
- The root CA certificate is the DigiCert Global Root CA

## Troubleshooting

### Connection Issues

1. Check broker hostname and port
2. Verify username/password
3. Ensure TLS certificate is valid
4. Check network connectivity

### Certificate Issues

If you encounter TLS certificate errors:

1. Verify the `MQTT_ROOT_CA` environment variable contains the correct certificate
2. Check if your broker requires a specific certificate format
3. Consider setting `context.check_hostname = True` if hostname verification is required

### Logs

Check the container logs for detailed error messages:

```bash
docker-compose logs mqtt-client
```
