FROM python:3.8
RUN apt-get update
RUN apt-get install -y build-essential bluetooth libdbus-1-dev libgirepository1.0-dev libudev-dev libical-dev
WORKDIR /code
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN pip install dbus-python pycairo PyGObject
COPY . .
ENTRYPOINT sh docker_entrypoint.sh