import logging
import asyncio
import threading
import sys
import argparse
from typing import Any
import requests
import egwttp
import macAddr
from bless import (  # type: ignore
    BlessServer,
    BlessGATTCharacteristic,
    GATTCharacteristicProperties,
    GATTAttributePermissions,
)
try:
    from gpioButton import GpioButton
except ImportError:
    GpioButton = None
import constants
import request_handler
import protos.wifi_services_pb2 as wifi_services_pb2
import protos.diagnostics_pb2 as diagnostics_pb2

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(name=__name__)


if sys.platform == "linux" and GpioButton is not None:
    # if we are on a bluez backend then we add the start and stop advertising functions
    logger.info("Using bluez backend, adding start and stop advertising functions")

    async def start_advertising():
        logging.info("Starting advertising")
        # we depend on that we are now on a bluez backend
        await SERVER.app.start_advertising(SERVER.adapter)
        # we don't create a new task as the button loop should be blocked until we have stoped advertising
        await stop_advertising()

    async def stop_advertising():
        logging.info("Stopping advertising in 3 minutes")
        await asyncio.sleep(60 * 3)
        logging.info("Stopping advertising...")

        # we depend on that we are now on a bluez backend
        adv = SERVER.app.advertisements[0]
        await SERVER.app.stop_advertising(SERVER.adapter)

        # we also need to remove the exported advertisement endpoint
        # this is a hack to get bless start advertising to work
        SERVER.app.bus.unexport(adv.path, adv)
        logging.info("Stopped advertising")

else:
    logger.info(
        "Not using bluez backend, not adding start and stop advertising functions"
    )


# this trigger is never used atm but could be used to signal the main thread that a request has been received
trigger: asyncio.Event = asyncio.Event()

# some global configuration constants
SERVICE_UUID = (
    "a07498ca-ad5b-474e-940d-16f1fbe7e8cd"  # this is the uuid of the service
)
REQUEST_CHAR = "51ff12bb-3ed8-46e5-b4f9-d64e2fec021b"  # clients write to this
RESPONSE_CHAR = "51ff12bb-3ed8-46e5-b4f9-d64e2fec021c"  # client read from this
API_URL = "localhost:5000"
SERVICE_NAME = f"SrcFul Hotspot {macAddr.get().replace(':', '')[-6:]}"  # we cannot use special characters in the name as this will mess upp the bluez service name filepath
SERVER = None
REQUEST_TIMEOUT = 5

async def add_custom_service(server: BlessServer):  
    await server.add_new_service(constants.SERVICE_UUID)

    char_flags = GATTCharacteristicProperties.read
    permissions = GATTAttributePermissions.readable

    # To-Do: Read the onboarding and public key from the device and populate the characteristics    

    await server.add_new_characteristic(constants.SERVICE_UUID, constants.ONBOARDING_KEY_UUID, char_flags, bytes('112qfPXyyXmH7miY5UXa4HFuXwF4PdrfU17kftKpk2a2SpKpxtsh', 'utf-8'), permissions)
    await server.add_new_characteristic(constants.SERVICE_UUID, constants.PUBLIC_KEY_UUID, char_flags, bytes('112qfPXyyXmH7miY5UXa4HFuXwF4PdrfU17kftKpk2a2SpKpxtsh', 'utf-8'), permissions)
    await server.add_new_characteristic(constants.SERVICE_UUID, constants.WIFI_MAC_UUID, char_flags, b'wifi_mac', permissions)
    await server.add_new_characteristic(constants.SERVICE_UUID, constants.LIGHTS_UUID, char_flags, b'n/a', permissions)
    await server.add_new_characteristic(constants.SERVICE_UUID, constants.WIFI_SSID_UUID, char_flags, b'magic_ssid', permissions)
    await server.add_new_characteristic(constants.SERVICE_UUID, constants.ETHERNET_ONLINE, char_flags, b'false', permissions)

    services = wifi_services_pb2.wifi_services_v1()

    await server.add_new_characteristic(constants.SERVICE_UUID, constants.WIFI_SERVICES_UUID, char_flags, bytes(services.SerializeToString()), permissions)

    services = diagnostics_pb2.diagnostics_v1()
    services.diagnostics['Name:\n'] = 'AA'
    services.diagnostics['\nPublic Key:\n'] = 'AA'
    services.diagnostics['\nOnboarding key:\n'] = 'AA'

    await server.add_new_characteristic(constants.SERVICE_UUID, constants.DIAGNOSTICS_UUID, char_flags, bytes(services.SerializeToString()), permissions)


    char_flags = GATTCharacteristicProperties.write | GATTCharacteristicProperties.read | GATTCharacteristicProperties.indicate
    permissions = GATTAttributePermissions.writeable | GATTAttributePermissions.readable
    await server.add_new_characteristic(constants.SERVICE_UUID, constants.ADD_GATEWAY_UUID, char_flags, b'', permissions)

    await server.add_new_characteristic(constants.SERVICE_UUID, constants.WIFI_CONNECT_UUID, char_flags, b'', permissions)

    logger.debug(f"Helium Service added with uuid {constants.SERVICE_UUID}")

async def add_device_info_service(server: BlessServer):
    service_uuid = '0000180a-0000-1000-8000-00805f9b34fb'
    await server.add_new_service(service_uuid)
    
    #await server.setup_task
    #service = DeviceInfoService()
    #await service.init(server)
    #server.services[service._uuid] = service

    char_uuid = "00002A29-0000-1000-8000-00805F9B34FB"
    char_flags = GATTCharacteristicProperties.read
    permissions = GATTAttributePermissions.readable

    #characteristic: BlessGATTCharacteristicBlueZDBus = (
    #        DeviceInfoCharacteristic(char_uuid, "2A29", char_flags, permissions, b'Helium')
    #    )
    #await characteristic.init(service)
    #service.add_characteristic(characteristic)

    #service.add_characteristic(char_uuid, char_flags, b'Helium', permissions)
    await server.add_new_characteristic(service_uuid, char_uuid, char_flags, b'Helium Systems, Inc.', permissions)

    char_uuid = "00002A25-0000-1000-8000-00805F9B34FB"
    await server.add_new_characteristic(service_uuid, char_uuid, char_flags, b'6081F989E7BF', permissions)

    char_uuid = "00002A26-0000-1000-8000-00805F9B34FB"
    await server.add_new_characteristic(service_uuid, char_uuid, char_flags, b'2020.02.18.1', permissions)


def read_request(characteristic: BlessGATTCharacteristic, **kwargs) -> bytearray:
    request_handler.read_request(SERVER, characteristic)

    return characteristic.value

def handle_response(path: str, method: str, reply: requests.Response, offset: int):
    egwttp_response = egwttp.construct_response(path, method, reply.text, offset)
    logger.debug("Reply: %s", egwttp_response)
    return egwttp_response

def request_get(path: str, offset: int) -> bytes:
    return handle_response(path, "GET", requests.get(API_URL + path, timeout=REQUEST_TIMEOUT), offset)

def request_post(path: str, content: str, offset: int) -> bytes:
    return handle_response(path, "POST", requests.post(API_URL + path, data=content, timeout=REQUEST_TIMEOUT), offset)

def write_request(characteristic: BlessGATTCharacteristic, value: Any, **kwargs):
    if request_handler.write_request(SERVER, characteristic, value) != True:
        threading.Thread(target=handle_write_request, args=(characteristic, value)).start()
    else: 
        pass

def handle_write_request(characteristic: BlessGATTCharacteristic, value: Any, **kwargs):
    characteristic.value = value
    # if request_response and request_response.value:
    val = value.decode("utf-8")

    logger.debug("Chars value set to %s", val)

    if egwttp.is_request(val):
        logger.debug("Request received...")
        header, content = egwttp.parse_request(val)
        logger.debug("Header: %s", header)
        logger.debug("Content: %s", content)

        if header["method"] == "GET" or header["method"] == "POST":
            response = (
                request_get(header["path"], header["Offset"])
                if header["method"] == "GET"
                else request_post(header["path"], content, header["Offset"])
            )
            response_char = SERVER.get_characteristic(RESPONSE_CHAR)
            response_char.value = response
            logger.debug("Char value set to %s", response_char.value)
            if SERVER.update_value(SERVICE_UUID, RESPONSE_CHAR):
                logger.debug(
                    "Value updated sent notifications to %s",
                    str(len(SERVER.app.subscribed_characteristics)),
                )
            else:
                logger.debug("Value not updated")
        else:
            logger.debug("Not a GET or POST request, doing nothing")

        # await post_request(header['path'], content)

        # transfer the request to a http request to the server
        # when the response is received, transfer it to a egwttp response
    else:
        logger.debug("Not a EGWTTP request, doing nothing")

async def run(gpio_button_pin: int = -1):
    global SERVER
    trigger.clear()
    # Instantiate the server
    SERVER = BlessServer(name=SERVICE_NAME, name_overwrite=True)
    SERVER.read_request_func = read_request
    SERVER.write_request_func = write_request

    await add_custom_service(SERVER)
    await add_device_info_service(SERVER)


    # Add Service
    await SERVER.add_new_service(SERVICE_UUID)
    logger.debug(
       "Service added with uuid %s and name %s.", SERVICE_UUID, SERVICE_NAME
    )

    # Add a Characteristic to the service
    char_flags = (
        GATTCharacteristicProperties.write_without_response
        | GATTCharacteristicProperties.write
    )
    permissions = GATTAttributePermissions.writeable
    await SERVER.add_new_characteristic(
        SERVICE_UUID, REQUEST_CHAR, char_flags, None, permissions
    )

    char_flags = (
        GATTCharacteristicProperties.read
        | GATTCharacteristicProperties.notify
        | GATTCharacteristicProperties.indicate
    )
    permissions = GATTAttributePermissions.readable
    await SERVER.add_new_characteristic(
        SERVICE_UUID, RESPONSE_CHAR, char_flags, bytearray(b"Hello ble World"),permissions,
    )

    logger.debug(SERVER.get_characteristic(REQUEST_CHAR))
    logger.debug(SERVER.get_characteristic(RESPONSE_CHAR))


    await SERVER.start()

    # if we are using the bluez backend and gpio buttin is set then we stop advertising after 3 minutes and also set up the button
    if sys.platform == "linux" and gpio_button_pin >= 0:
        logging.info("Using bluez backend, adding button on pin %s", gpio_button_pin)
        await stop_advertising()
        button = GpioButton(gpio_button_pin, start_advertising)
        asyncio.create_task(button.run())
    else:
        logging.info(
            "Not using bluez backend or pin < 0 (pin is: %s), advertising indefinitely",
            gpio_button_pin,
        )

    await trigger.wait()

    await SERVER.stop()


if __name__ == "__main__":
    logger.info("Starting ble service... ")

    args = argparse.ArgumentParser()
    args.add_argument(
        "-api_url",
        help=f"The url of the API endpoint, default: {API_URL}",
        default=API_URL,
    )

    args.add_argument(
        "-gpio_button_pin",
        help="Pin for a gpio button to start advertising on double click, default: -1 (eternal advertising)",
        default=-1,
        type=int,
    )

    args.add_argument(
        "-log_level",
        help=f"The log level ({logging.getLevelNamesMapping().keys()}), default: {logging.getLevelName(logger.getEffectiveLevel())}",
        default=logging.getLevelName(logger.level),
    )
    args.add_argument(
        "-service_name",
        help=f"The name of the service, default: {SERVICE_NAME}",
        default=SERVICE_NAME,
    )

    args = args.parse_args()
    print("BLE service called with arguments: ", args)
    API_URL = "http://" + args.api_url
    SERVICE_NAME = args.service_name
    if args.log_level not in logging.getLevelNamesMapping().keys():
        logger.error(
            "Invalid log level %s continuing with default log level.", args.log_level
        )
    else:
        logger.setLevel(logging.getLevelName(args.log_level))

    asyncio.run(run(args.gpio_button_pin))