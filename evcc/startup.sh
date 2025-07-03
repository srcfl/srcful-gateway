#!/bin/sh
set -e

# Ensure config directory exists
mkdir -p /etc/evcc

# Always create/clear the config file to remove any dummy content
echo "Creating empty evcc configuration file..."
> /etc/evcc/evcc.yaml

# Start evcc
exec evcc -c /etc/evcc/evcc.yaml 