import logging
import asyncio
import threading
import sys

import argparse

import requests

import egwttp
from typing import Any

import macAddr




# import wifiprov

from bless import (  # type: ignore
    BlessServer,
    BlessGATTCharacteristic,
    GATTCharacteristicProperties,
    GATTAttributePermissions,
)

from gpioButton import GpioButton

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(name=__name__)


if sys.platform == "linux":
    # if we are on a bluez backend then we add the start and stop advertising functions
    logger.info("Using bluez backend, adding start and stop advertising functions")
    async def start_advertising():
        logging.info("Starting advertising")
        # we depend on that we are now on a bluez backend
        await g_server.app.start_advertising(g_server.adapter)
        # add the stop advertising task to the event loop
        asyncio.create_task(stop_advertising())


    async def stop_advertising():
        logging.info("Stopping advertising in 3 minutes")
        asyncio.sleep(60 * 3)
        logging.info("Stopping advertising")
        # we depend on that we are now on a bluez backend
        await g_server.app.stop_advertising(g_server.adapter)
else:
    logger.info("Not using bluez backend, not adding start and stop advertising functions")


# this trigger is never used atm but could be used to signal the main thread that a request has been received
trigger: asyncio.Event = asyncio.Event()

# some global configuration constants
g_service_uuid = (
    "a07498ca-ad5b-474e-940d-16f1fbe7e8cd"  # this is the uuid of the service
)
g_request_char_uuid = "51ff12bb-3ed8-46e5-b4f9-d64e2fec021b"  # for accepting requests ie. clients write to this
g_response_char_uuid = "51ff12bb-3ed8-46e5-b4f9-d64e2fec021c"  # for sending responses ie client read from this
g_api_url = "localhost:5000"
g_service_name = f"SrcFul Energy Gateway {macAddr.get().replace(':', '')[-6:]}"  # we cannot use special characters in the name as this will mess upp the bluez service name filepath
g_server = None


def read_request(characteristic: BlessGATTCharacteristic, **kwargs) -> bytearray:
    logger.debug("Reading %", characteristic.value)
    return characteristic.value


def handle_response(path: str, method: str, reply: requests.Response):
    egwttp_response = egwttp.construct_response(path, method, reply.text)
    logger.debug("Reply: %s", egwttp_response)
    return egwttp_response


def request_get(path: str) -> bytearray:
    return bytearray(handle_response(path, "GET", requests.get(g_api_url + path)))


def request_post(path: str, content: str) -> bytearray:
    return bytearray(
        handle_response(path, "POST", requests.post(g_api_url + path, data=content))
    )


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
                request_get(header["path"])
                if header["method"] == "GET"
                else request_post(header["path"], content)
            )
            response_char = g_server.get_characteristic(g_response_char_uuid)
            response_char.value = response
            logger.debug("Char value set to %s", response_char.value)
            if g_server.update_value(g_service_uuid, g_response_char_uuid):
                logger.debug("Value updated sent notifications to %s", str(len(g_server.app.subscribed_characteristics)))
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




async def run():
    global g_server, g_service_uuid, g_char_uuid, g_api_url, g_service_name
    trigger.clear()
    # Instantiate the server
    g_server = BlessServer(name=g_service_name, name_overwrite=True)
    g_server.read_request_func = read_request
    g_server.write_request_func = write_request

    # Add Service
    await g_server.add_new_service(g_service_uuid)
    logger.debug("Service added with uuid %s and name %s.", g_service_uuid, g_service_name)

    # Add a Characteristic to the service
    char_flags = (
        GATTCharacteristicProperties.write_without_response
        | GATTCharacteristicProperties.write
    )
    permissions = GATTAttributePermissions.writeable
    await g_server.add_new_characteristic(
        g_service_uuid, g_request_char_uuid, char_flags, None, permissions
    )

    char_flags = (
        GATTCharacteristicProperties.read
        | GATTCharacteristicProperties.notify
        | GATTCharacteristicProperties.indicate
    )
    permissions = GATTAttributePermissions.readable
    await g_server.add_new_characteristic(
        g_service_uuid,
        g_response_char_uuid,
        char_flags,
        bytearray(b"Hello ble World"),
        permissions,
    )

    logger.debug(g_server.get_characteristic(g_request_char_uuid))

    logger.debug(g_server.get_characteristic(g_response_char_uuid))

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

    await g_server.start()

    # if we are using the bluez backend and gpio buttin is set then we stop advertising after 3 minutes and also set up the button
    if sys.platform == "linux":
        logging.info("Using bluez backend, adding gpio button")
        await stop_advertising()
        button = GpioButton(7, 3, start_advertising)
        asyncio.create_task(button.run())
    else:
        logging.info("Not using bluez backend, not adding gpio button")

    await trigger.wait()

    await g_server.stop()


if __name__ == "__main__":
    logger.info("Starting ble service... ")

    args = argparse.ArgumentParser()
    args.add_argument(
        "-api_url",
        help=f"The url of the API endpoint, default: {g_api_url}",
        default=g_api_url,
    )
    args.add_argument(
        "-service_uuid",
        help=f"The UUID of the service, default: {g_service_uuid}",
        default=g_service_uuid,
    )
    args.add_argument(
        "-char_uuid",
        help=f"The UUID of the characteristic, default: {g_request_char_uuid}",
        default=g_request_char_uuid,
    )
    args.add_argument(
        "-log_level",
        help=f"The log level ({logging.getLevelNamesMapping().keys()}), default: {logging.getLevelName(logger.getEffectiveLevel())}",
        default=logging.getLevelName(logger.level),
    )
    args.add_argument(
        "-service_name",
        help=f"The name of the service, default: {g_service_name}",
        default=g_service_name,
    )

    args = args.parse_args()
    print("BLE service called with arguments: ", args)
    g_service_uuid = args.service_uuid.lower()
    g_char_uuid = args.char_uuid.lower()
    g_api_url = "http://" + args.api_url
    g_service_name = args.service_name
    if args.log_level not in logging.getLevelNamesMapping().keys():
        logger.error("Invalid log level %s continuing with default log level.", args.log_level)
    else:
        logger.setLevel(logging.getLevelName(args.log_level))

    asyncio.run(run())
