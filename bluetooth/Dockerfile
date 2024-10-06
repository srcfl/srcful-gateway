FROM python:3.11@sha256:f51f754249d41efc64c10b44b60e510201f0cbbf96bef9f0e27fc1c2a7a83728 as build
RUN apt-get update
RUN apt-get install -y build-essential libdbus-1-dev libgirepository1.0-dev libudev-dev libical-dev



WORKDIR /code
COPY requirements.txt requirements.txt

# set up python virtual env running activate is cumbersome and applies only to that RUN line
# we do it manually so it is used all over the container

ENV VIRTUAL_ENV=/code/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN pip install -r requirements.txt
RUN pip install dbus-python==1.3.2


# the run stage container
FROM python:3.11@sha256:f51f754249d41efc64c10b44b60e510201f0cbbf96bef9f0e27fc1c2a7a83728

ENV DBUS_SYSTEM_BUS_ADDRESS=unix:path=/host/run/dbus/system_bus_socket

RUN apt-get update
RUN apt-get install -y bluetooth

COPY --from=build /code/venv /code/venv

# Make sure we use the virtualenv:
ENV VIRTUAL_ENV=/code/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# copy bluetooth main configuration
COPY bluetooth.conf /etc/bluetooth/main.conf

WORKDIR /code
COPY . .
ENTRYPOINT sh docker_entrypoint.sh