#!/bin/bash

echo "Welcome to the srcful eGW Docker Compose application!"
echo ""
echo "This application requires Docker and Docker Compose to be installed on your system."
echo "It also requires network access to fetch Docker images and communicate with external services."
echo "Please ensure that your system meets these requirements before proceeding."
echo ""
echo "In this step, the system will automatically detect your host IP and you will be asked to select a Docker Compose file to start the services."
echo "Next docker compose up will be executed with the selected file and the services will be started."
echo ""

# Get the IP address of the default network interface
export HOST_IP=$(ip -4 addr show scope global dev $(ip route|awk '/default/ { print $5 }') | grep inet | awk '{print $2}' | cut -d / -f 1)

# Find all Docker Compose files in the current directory
compose_files=($(ls | grep 'compose.*\.yml$'))

# Prompt the user to select a file
echo "Select a Docker Compose file:"
select file in "${compose_files[@]}"; do
  if [[ -n "${file}" ]]; then
    # Run docker-compose up with the selected file
    docker-compose -f "${file}" up
    break
  else
    echo "Invalid selection. Please try again."
  fi
done
