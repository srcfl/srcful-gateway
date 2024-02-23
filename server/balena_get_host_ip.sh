#!/bin/bash

# Check if the necessary environment variables are set
if [[ -z "${BALENA_SUPERVISOR_ADDRESS}" ]] || [[ -z "${BALENA_SUPERVISOR_API_KEY}" ]]; then
    echo "Environment variables BALENA_SUPERVISOR_ADDRESS or BALENA_SUPERVISOR_API_KEY are not set."
    echo "Use label io.balena.features.supervisor-api in docker compose file to enable the Supervisor API."
    exit 1
fi

# Send a GET request to the Balena Supervisor API and get the device information
response=$(curl -s -X GET --header "Content-Type:application/json" "${BALENA_SUPERVISOR_ADDRESS}/v1/device?apikey=${BALENA_SUPERVISOR_API_KEY}")

# Get the IP addresses from the response
ip_addresses=$(echo "${response}" | jq -r '.ip_address')

# Get the first IP address
host_ip=$(echo "${ip_addresses}" | cut -d ' ' -f 1)

# Export the HOST_IP environment variable
export HOST_IP="${host_ip}"

echo "Using Balena Supervisor API to set HOST_IP to ${HOST_IP}"
