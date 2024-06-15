FROM python:3.11-alpine@sha256:558d14432cef380aec99155f348ac1c5cb35072abf32209aecd5a8a422ff519a
COPY . /server
# put the entrypoint script in the container in the parent directory
# we do this so the script can run the server as a module
COPY docker_entrypoint.sh .
COPY balena_get_host_ip.sh .
ENV CRYPTOAUTHLIB_NOUSB=True
ENV DBUS_SYSTEM_BUS_ADDRESS=unix:path=/host/run/dbus/system_bus_socket

RUN apk update
RUN apk add --no-cache make
RUN apk add --no-cache gcc musl-dev linux-headers cmake libffi-dev
RUN apk add curl jq
    
# Install necessary packages
RUN apk add --no-cache dbus dbus-dev glib-dev dbus-glib

RUN pip install --upgrade pip
# Install Python D-Bus library
RUN pip install --no-cache-dir dbus-python==1.3.2

RUN pip install -r server/requirements.txt
EXPOSE 5000

# Make scripts executable
RUN chmod +x /docker_entrypoint.sh
RUN chmod +x /balena_get_host_ip.sh

ENTRYPOINT sh /docker_entrypoint.sh
