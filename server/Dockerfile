FROM python:3.11-alpine
COPY . /server
ENV CRYPTOAUTHLIB_NOUSB=True
ENV DBUS_SYSTEM_BUS_ADDRESS=unix:path=/host/run/dbus/system_bus_socket

RUN apk update
RUN apk add --no-cache make
RUN apk add --no-cache gcc musl-dev linux-headers cmake libffi-dev

# Install necessary packages
RUN apk add --no-cache dbus dbus-dev glib-dev dbus-glib

RUN pip install --upgrade pip
# Install Python D-Bus library
RUN pip install --no-cache-dir dbus-python

RUN pip install -r server/requirements.txt
EXPOSE 5000


ENTRYPOINT ["python"]
CMD ["-m", "server", "-ih", "192.168.40.145", "-it", "unknown"]
# CMD ["-m", "server.app", "-ih", "10.130.1.235", "-it", "solaredge"]