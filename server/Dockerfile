FROM python:3.11-alpine
COPY . /server
ENV CRYPTOAUTHLIB_NOUSB=True
RUN apk add --no-cache make
RUN apk add --no-cache gcc musl-dev linux-headers cmake libffi-dev
RUN pip install --upgrade pip
RUN pip install -r server/requirements.txt
EXPOSE 5000

ENTRYPOINT ["python"]
CMD ["-m", "server", "-ih", "192.168.40.145", "-it", "unknown"]
# CMD ["-m", "server.app", "-ih", "10.130.1.235", "-it", "solaredge"]