#!/bin/bash

echo "Starting server container..."
echo "You can also visit https://app.srcful.io to configure the service."
echo ""

# Run your Python module here
python -m server -wp $REST_SERVICE_PORT_INTERNAL -hp $REST_SERVICE_PORT
