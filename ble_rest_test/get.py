import pytest
import asyncio
import logging

from bleak import BleakClient, BleakScanner, BLEDevice, AdvertisementData
from bleak.backends.characteristic import BleakGATTCharacteristic

logger = logging.getLogger(__name__)

request_char_uuid = '51ff12bb-3ed8-46e5-b4f9-d64e2fec021b'


@pytest.fixture(scope="module")
async def client():

    def notification_handler_factory(response: [], trigger: asyncio.Event):
        def notification_handler(characteristic: BleakGATTCharacteristic, data: bytearray):
            """Simple notification handler which prints the data received."""
            logger.info("%s: %r", characteristic.description, data)
            response.append(data)
            trigger.set()
        return notification_handler

    service = "a07498ca-ad5b-474e-940d-16f1fbe7e8cd"

    def blefilter(d: BLEDevice, adv: AdvertisementData):
        print('Name:', adv.local_name, type(adv.local_name))
        print('Services:', adv.service_uuids)
        
        return adv.local_name and adv.local_name.startswith("SrcFul Energy Gateway") and service in adv.service_uuids

    device = await BleakScanner.find_device_by_filter(blefilter, timeout=60)
    
    response_char_uuid = '51ff12bb-3ed8-46e5-b4f9-d64e2fec021c'
    bclient = BleakClient(device, timeout=60, disconnected_callback=lambda client: logger.info("Disconnected"))

    response = []
    trigger = asyncio.Event()
    
    try:
        await bclient.connect()
        await bclient.start_notify(response_char_uuid, notification_handler_factory(response, trigger))
        yield (response, trigger, bclient)
    finally:
        await bclient.disconnect()

@pytest.mark.asyncio
async def test_hello(client):
    async for response, trigger, bclient in client:
        req = construct_request("/api/hello", "GET", "")
        trigger.clear()
        response.clear()
        await bclient.write_gatt_char(request_char_uuid, req, False)
        await trigger.wait()
        response = response[0].decode()
        print("Response:", response)
        assert response == 'EGWTP/1.1 200 OK\r\nLocation: /api/hello\r\nMethod: GET\r\nContent-Type: text/json\r\nContent-Length: 39\r\n\r\n{"message": "hello world from srcful!"}'


@pytest.mark.asyncio
async def test_hello_again(client):
    async for response, trigger, bclient in client:
        req = construct_request("/api/hello", "GET", "")
        trigger.clear()
        response.clear()
        await bclient.write_gatt_char(request_char_uuid, req, False)
        await trigger.wait()
        response = response[0].decode()
        print("Response:", response)
        assert response == 'EGWTP/1.1 200 OK\r\nLocation: /api/hello\r\nMethod: GET\r\nContent-Type: text/json\r\nContent-Length: 39\r\n\r\n{"message": "hello world from srcful!"}'


def construct_request(endpoint, method, data):
    message_type = "EGWTTP/1.1"
    content_type = "text/json"
    content_length = len(data.encode())

    data_to_send = f'{method} {endpoint} {message_type}\r\nContent-Type: {content_type}\r\nContent-Length: {content_length}\r\n\r\n{data}'

    return data_to_send.encode()

