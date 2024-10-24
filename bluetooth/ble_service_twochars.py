import logging
import asyncio
import threading
import sys

import argparse
from typing import Any
import requests

import egwttp


import macAddr


# import wifiprov

from bless import (  # type: ignore
    BlessServer,
    BlessGATTCharacteristic,
    GATTCharacteristicProperties,
    GATTAttributePermissions,
)

from gpioButton import GpioButton

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(name=__name__)


if sys.platform == "linux":
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
    "0fda92b2-44a2-4af2-84f5-fa682baa2b8d"  # this is the uuid of the service
)
REQUEST_CHAR = "51ff12bb-3ed8-46e5-b4f9-d64e2fec021b"  # clients write to this
RESPONSE_CHAR = "51ff12bb-3ed8-46e5-b4f9-d64e2fec021c"  # client read from this
API_URL = "localhost:5000"
SERVICE_NAME = f"Sourceful Energy Gateway {macAddr.get().replace(':', '')[-6:]}"  # we cannot use special characters in the name as this will mess upp the bluez service name filepath
SERVER = None
REQUEST_TIMEOUT = 20


def read_request(characteristic: BlessGATTCharacteristic, **kwargs) -> bytearray:
    logger.debug("Reading %s", characteristic.value)
    return characteristic.value


def handle_response(path: str, method: str, reply: requests.Response, offset: int):
    egwttp_response = egwttp.construct_response(path, method, reply.text, offset)
    logger.debug("Reply: %s", egwttp_response)
    return egwttp_response


def request_get(path: str, offset: int) -> bytes:
    return handle_response(path, "GET", requests.get(API_URL + path, timeout=REQUEST_TIMEOUT), offset)


def request_post(path: str, content: str, offset: int) -> bytes:
    return handle_response(path, "POST", requests.post(API_URL + path, data=content, timeout=REQUEST_TIMEOUT), offset)


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


def write_request(characteristic: BlessGATTCharacteristic, value: Any, **kwargs):
    threading.Thread(target=handle_write_request, args=(characteristic, value)).start()


async def run(gpio_button_pin: int = -1):
    global SERVER
    trigger.clear()
    # Instantiate the server
    SERVER = BlessServer(name=SERVICE_NAME, name_overwrite=True)
    SERVER.read_request_func = read_request
    SERVER.write_request_func = write_request

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
        SERVICE_UUID,
        RESPONSE_CHAR,
        char_flags,
        bytearray(b"Hello ble World"),
        permissions,
    )

    logger.debug(SERVER.get_characteristic(REQUEST_CHAR))

    logger.debug(SERVER.get_characteristic(RESPONSE_CHAR))

    # bluez backend specific
    # if g_server.app:
    #  async def on_startNotify(characteristic: BlessGATTCharacteristic):
    #    logger.debug("StartNotify called - client subscribed")
    #    await g_server.app.stop_advertising(g_server.adapter)
    #    logger.debug("Advertising stopped")
    #    return True
    #
    #  async def on_stopNotify(characteristic: BlessGATTCharacteristic):
    #    logger.debug("StopNotify called - client unsubscribed")
    #    await g_server.app.start_advertising(g_server.adapter)
    #    logger.debug("Advertising started")
    #    return True
    #  g_server.app.StartNotify = on_startNotify
    #  g_server.app.StopNotify = on_stopNotify

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
