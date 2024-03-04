#!/bin/bash

# Check if the necessary environment variables are set
if [[ -z "${BALENA_SUPERVISOR_ADDRESS}" ]] || [[ -z "${BALENA_SUPERVISOR_API_KEY}" ]]; then
    echo "Environment variables BALENA_SUPERVISOR_ADDRESS or BALENA_SUPERVISOR_API_KEY are not set."
    echo "Use label io.balena.features.supervisor-api in docker compose file to enable the Supervisor API."
    return 1
fi

# Attempt to get the IP address for up to 5 times
i=1
while [ $i -le 15 ]
do
    # Send a GET request to the Balena Supervisor API and get the device information
    response=$(curl -s -X GET --header "Content-Type:application/json" "${BALENA_SUPERVISOR_ADDRESS}/v1/device?apikey=${BALENA_SUPERVISOR_API_KEY}")

    echo "Attempt ${i}: ${response}"

    # Get the IP addresses from the response
    ip_addresses=$(echo "${response}" | jq -r '.ip_address')

    # Get the first IP address
    host_ip=$(echo "${ip_addresses}" | cut -d ' ' -f 1)

    # Check if the IP address is not empty
    if [[ -n "${host_ip}" ]]; then
        # Export the HOST_IP environment variable
        export HOST_IP="${host_ip}"
        
        echo "Using Balena Supervisor API to set HOST_IP to ${HOST_IP}"
        return 0
    fi

    i=$(( $i + 1 ))
    # Sleep for 7 seconds before the next attempt
    sleep 7
done

echo "Failed to get the IP address after 15 attempts."
return 1
