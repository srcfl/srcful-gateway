#!/bin/bash

# Define the list of valid build names
valid_builds=("beta" "solaris")

# Check if the argument is valid
if [[ ! " ${valid_builds[@]} " =~ " $1 " ]]; then
  echo "Invalid argument. Must be one of: ${valid_builds[@]}"
  exit 1
fi

# Prompt the user to retype the build name for assurance
read -p "Please retype the build name '$1' to confirm: " confirmation

# Check if the confirmation matches the original build name
if [ "$confirmation" != "$1" ]; then
  echo "Confirmation does not match the original build name. Aborting."
  exit 1
fi

# Rename the docker-compose file based on the argument
mv "docker-compose-$1.yml" docker-compose.yml

# Run the balena deploy command
balena deploy "$1" --build --unsupported

# Rename the docker-compose file back to its original name
mv docker-compose.yml "docker-compose-$1.yml"

