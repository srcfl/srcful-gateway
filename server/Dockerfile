FROM python:3.11-alpine
COPY . /app
WORKDIR /app
ENV CRYPTOAUTHLIB_NOUSB=True
RUN apk add --no-cache make
RUN apk add --no-cache gcc musl-dev linux-headers cmake libffi-dev
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
EXPOSE 5000

ENTRYPOINT ["python"]
CMD ["app.py", "-ih", "10.130.1.235", "-it", "solaredge"]