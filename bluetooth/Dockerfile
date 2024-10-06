FROM python:3.11-slim-bullseye as build

RUN apt-get update && apt-get install -y \
    build-essential \
    libdbus-1-dev \
    libgirepository1.0-dev \
    libudev-dev \
    libical-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /code
COPY requirements.txt requirements.txt

ENV VIRTUAL_ENV=/code/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir dbus-python==1.3.2

# The run stage container
FROM python:3.11-slim-bullseye

ENV DBUS_SYSTEM_BUS_ADDRESS=unix:path=/host/run/dbus/system_bus_socket

RUN apt-get update && apt-get install -y \
    bluetooth \
    && rm -rf /var/lib/apt/lists/*

COPY --from=build /code/venv /code/venv

ENV VIRTUAL_ENV=/code/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY bluetooth.conf /etc/bluetooth/main.conf

WORKDIR /code
COPY . .
ENTRYPOINT ["sh", "docker_entrypoint.sh"]