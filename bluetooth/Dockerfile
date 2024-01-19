FROM python:3.11@sha256:f51f754249d41efc64c10b44b60e510201f0cbbf96bef9f0e27fc1c2a7a83728
RUN apt-get update
RUN apt-get install -y build-essential bluetooth libdbus-1-dev libgirepository1.0-dev libudev-dev libical-dev
ENV DBUS_SYSTEM_BUS_ADDRESS=unix:path=/host/run/dbus/system_bus_socket
WORKDIR /code
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN pip install dbus-python==1.3.2
COPY . .
ENTRYPOINT sh docker_entrypoint.sh