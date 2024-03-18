#!/bin/bash

# Check if the HOST_IP environment variable is set
if [[ -z "${HOST_IP}" ]]; then
    # Source the previous script to set HOST_IP
    source ./balena_get_host_ip.sh
fi

# Check if the HOST_IP environment variable is set now
if [[ -z "${HOST_IP}" ]]; then
    # Issue a warning and set HOST_IP to 127.0.0.1
    echo "Warning: HOST_IP is not set. Defaulting to 127.0.0.1"
    export HOST_IP="127.0.0.1"
fi

echo "HOST_IP is set to ${HOST_IP}"

# Check if the REST_SERVICE_PORT_INTERNAL environment variable is set
if [[ -z "${REST_SERVICE_PORT_INTERNAL}" ]]; then
    # Issue a warning and set REST_SERVICE_PORT_INTERNAL to 5000
    echo "Warning: REST_SERVICE_PORT_INTERNAL is not set. Defaulting to 5000"
    export REST_SERVICE_PORT_INTERNAL=5000
fi

echo "REST_SERVICE_PORT_INTERNAL is set to ${REST_SERVICE_PORT_INTERNAL}"

# Check if the REST_SERVICE_PORT environment variable is set
if [[ -z "${REST_SERVICE_PORT}" ]]; then
    # Issue a warning and set REST_SERVICE_PORT to 80
    echo "Warning: REST_SERVICE_PORT is not set. Defaulting to 80"
    export REST_SERVICE_PORT=80
fi

echo "REST_SERVICE_PORT is set to ${REST_SERVICE_PORT}"

echo ""
echo "Starting server container... visit http://${HOST_IP}:${REST_SERVICE_PORT} to access the service once it has started."
echo "You can also visit https://configurator.srcful.io to configure the service."
echo ""

# Run your Python module here
python -m server -b /data/srcful/bootstrap.txt -wp $REST_SERVICE_PORT_INTERNAL -hip $HOST_IP -hp $REST_SERVICE_PORT
