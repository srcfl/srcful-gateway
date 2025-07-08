FROM python:3.11-alpine@sha256:558d14432cef380aec99155f348ac1c5cb35072abf32209aecd5a8a422ff519a AS builder

# Install only the build dependencies needed for zeroconf
RUN apk update && apk add --no-cache make gcc musl-dev linux-headers cmake libffi-dev

# Build zeroconf wheel
RUN pip install --upgrade pip
RUN pip install six
RUN pip wheel --wheel-dir=/wheels zeroconf==0.135.0

# Main stage
FROM python:3.11-alpine@sha256:558d14432cef380aec99155f348ac1c5cb35072abf32209aecd5a8a422ff519a

# Copy pre-built wheel
COPY --from=builder /wheels /wheels

# Copy application files
COPY . /server
COPY docker_entrypoint.sh .
COPY balena_get_host_ip.sh .

# Set environment variables
ENV CRYPTOAUTHLIB_NOUSB=True
ENV DBUS_SYSTEM_BUS_ADDRESS=unix:path=/host/run/dbus/system_bus_socket

# Install all system dependencies in one layer
RUN apk update && \
    apk add --no-cache make gcc musl-dev linux-headers cmake libffi-dev curl jq dbus dbus-dev glib-dev dbus-glib networkmanager networkmanager-cli

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir six && \
    pip install --no-cache-dir --no-index --find-links=/wheels zeroconf==0.135.0 && \
    pip install --no-cache-dir dbus-python==1.3.2 && \
    pip install -r server/requirements.txt

EXPOSE 5000

# Make scripts executable
RUN chmod +x /docker_entrypoint.sh
RUN chmod +x /balena_get_host_ip.sh

ENTRYPOINT sh /docker_entrypoint.sh