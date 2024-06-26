# Use a Debian-based image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    cmake \
    build-essential \
    libpython3-dev \
    libdbus-1-dev \
    libglib2.0-dev \
    curl \
    tar \
    && rm -rf /var/lib/apt/lists/*

# Download the binary
RUN curl -L -o helium-gateway.tar.gz https://github.com/helium/gateway-rs/releases/download/v1.3.0/helium-gateway-1.3.0-armv7-unknown-linux-musleabihf.tar.gz && \
    tar -xzf helium-gateway.tar.gz && \
    rm helium-gateway.tar.gz

# Copy the settings.toml file into the container
COPY settings.toml /app/settings.toml

# Copy the requirements file into the container
COPY requirements.txt /app/requirements.txt

# Install the Python dependencies
RUN pip install -r /app/requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Specify the command to run the application with Waitress
CMD ["waitress-serve", "--port=3000", "--call", "server:create_app"]