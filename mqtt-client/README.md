# MQTT Service

A simple Flask-based MQTT service that provides an HTTP API for publishing MQTT messages. This service self-initializes by getting device authentication from the web container and establishing its own MQTT broker connection.

## Architecture

- **Self-Initializing**: Automatically gets crypto info and JWT from web container
- **Simple Flask API**: Two endpoints for health check and message publishing
- **Direct Communication**: Server container makes direct HTTP POST requests to this service
- **Clean Dependencies**: Unidirectional dependency flow (Server → MQTT)

## API Endpoints

### GET /health
Returns the service status and MQTT connection state.

### POST /publish
Publishes a message to the MQTT broker.

**Request Body:**
```json
{
    "topic": "sourceful/device/DEVICE_ID/harvest/example",
    "payload": {
        "type": "harvest",
        "device_sn": "DEVICE_12345",
        "harvest_data": {...}
    }
}
```

**Features:**
- Automatically replaces `DEVICE_ID` placeholder in topic with actual device ID
- Returns success/failure status
- Handles MQTT broker connection errors gracefully

## Usage

### From Server Container (Harvest Task)
```python
import requests

# Direct HTTP request to MQTT service
response = requests.post(
    "http://localhost:8080/publish",
    json={
        "topic": "sourceful/device/DEVICE_ID/harvest/example",
        "payload": harvest_data
    }
)
```

## Testing

Run the test script to verify API functionality:

```bash
python test_api.py
```

## Environment Variables

- `WEB_CONTAINER_HOST`: Host for web container (default: localhost)
- `WEB_CONTAINER_PORT`: Port for web container (default: 8000)

## Files

- `mqtt_service.py`: Main Flask MQTT service
- `test_api.py`: API testing script
- `Dockerfile`: Container configuration
- `requirements.txt`: Python dependencies