FROM python:3.11
RUN apt-get update
RUN apt-get install -y build-essential bluetooth libdbus-1-dev libgirepository1.0-dev libudev-dev libical-dev
ENV DBUS_SYSTEM_BUS_ADDRESS=unix:path=/host/run/dbus/system_bus_socket
WORKDIR /code
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN pip install dbus-python pycairo PyGObject
RUN pip install python-networkmanager
COPY . .
ENTRYPOINT sh docker_entrypoint.sh