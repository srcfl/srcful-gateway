# Use Python 3.11 Alpine as the base image
FROM python:3.11-alpine

# Set working directory
WORKDIR /root

# Install necessary dependencies
# Alpine uses apk for package management
RUN apk update && apk add --no-cache \
    git \
    build-base \
    linux-headers \
    # Add any additional dependencies required for the packet forwarder
    && rm -rf /var/cache/apk/*

# Clone the SX1302 Packet Forwarder repository
RUN git clone https://github.com/helium/sx1302_hal.git

# Build the SX1302 Packet Forwarder
WORKDIR /root/sx1302_hal
RUN make

# Set up links in the packet_forwarder directory
WORKDIR /root/sx1302_hal/packet_forwarder
RUN ln -s ../tools/reset_lgw.sh reset_lgw.sh \
    && ln -s global_conf.json.sx1250.EU868_A global_conf.json

# Set the start command for the container
CMD ["./lora_pkt_fwd"]
