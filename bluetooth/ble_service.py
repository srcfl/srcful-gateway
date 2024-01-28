import logging
import asyncio

import argparse

import requests

import egwttp
from typing import Any

# import wifiprov

from ble_flush import remove_all_paired_devices

from bless import (  # type: ignore
    BlessServer,
    BlessGATTCharacteristic,
    GATTCharacteristicProperties,
    GATTAttributePermissions
)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(name=__name__)
# this trigger is never used atm but could be used to signal the main thread that a request has been received
trigger: asyncio.Event = asyncio.Event()

# some global configuration constants
g_service_uuid = "A07498CA-AD5B-474E-940D-16F1FBE7E8CD"
g_char_uuid = "51FF12BB-3ED8-46E5-B4F9-D64E2FEC021B"
g_api_url = "localhost:5000"
g_service_name = "SrcFul Energy Gateway"
g_server = None


def read_request(characteristic: BlessGATTCharacteristic, **kwargs) -> bytearray:
  logger.debug(f"Reading {characteristic.value}")
  return characteristic.value

def handle_response(path:str, reply: requests.Response):
  egwttp_response = egwttp.construct_response(path, reply.text)
  logger.debug(f"Reply: {egwttp_response}")
  return egwttp_response

def request_get(path: str) -> bytearray:
  return bytearray(handle_response(path, requests.get(g_api_url + path)))

def request_post(path: str, content: str) -> bytearray:
  return bytearray(handle_response(path, requests.post(g_api_url + path, data=content)))

def write_request(characteristic: BlessGATTCharacteristic, value: Any, **kwargs):

    # if request_response and request_response.value:
    val = value.decode('utf-8')

    logger.debug(f"Chars value set to {val}")

    if egwttp.is_request(val):
      logger.debug(f"Request received...")
      header, content = egwttp.parse_request(val)
      logger.debug(f"Header: {header}")
      logger.debug(f"Content: {content}")

      if header['method'] == 'GET' or header['method'] == 'POST':
        response = request_get(header['path']) if header['method'] == 'GET' else request_post(header['path'], content)
        characteristic.value = response
        logger.debug(f"Char value set to {characteristic.value}")
        g_server.update_value(g_service_uuid, g_char_uuid)   
      else:
        logger.debug("Not a GET or POST request, doing nothing")

      #await post_request(header['path'], content)

      # transfer the request to a http request to the server
      # when the response is received, transfer it to a egwttp response
    else:
        if val == "remove_all_paired_devices":
          logger.debug("Removing all paired devices...")
          g_server.update_value(g_service_uuid, g_response_char_uuid)
          response_char = g_server.get_characteristic(g_response_char_uuid)
          response_char.value = bytearray(b"Removing all paired devices")
          remove_all_paired_devices()
        elif val == "hello":
          logger.debug("Hello received")
          response_char = g_server.get_characteristic(g_response_char_uuid)
          response_char.value = bytearray(b"Hello from the ble service")
          g_server.update_value(g_service_uuid, g_response_char_uuid)
        else:
          logger.debug("Not a EGWTTP nor a ble request, doing nothing")
    
    


async def run():
  global g_server, g_service_uuid, g_char_uuid, g_api_url, g_service_name
  trigger.clear()
  # Instantiate the server
  g_server = BlessServer(name=g_service_name, name_overwrite=True)
  g_server.read_request_func = read_request
  g_server.write_request_func = write_request

  # Add Service
  await g_server.add_new_service(g_service_uuid)
  logger.debug("Service added")

  # Add a Characteristic to the service
  char_flags = (
      GATTCharacteristicProperties.read |
      GATTCharacteristicProperties.write |
      GATTCharacteristicProperties.indicate
  )
  permissions = (
      GATTAttributePermissions.readable |
      GATTAttributePermissions.writeable
  )
  await g_server.add_new_characteristic(
      g_service_uuid,
      g_char_uuid,
      char_flags,
      None,
      permissions)

  logger.debug(
      g_server.get_characteristic(
          g_char_uuid
      )
  )

  await g_server.start()
  await trigger.wait()

  await g_server.stop()

if __name__ == "__main__":

  args = argparse.ArgumentParser()
  args.add_argument("-api_url", help=f"The url of the API endpoint, default: {g_api_url}", default=g_api_url)
  args.add_argument("-service_uuid", help=f"The UUID of the service, default: {g_service_uuid}", default=g_service_uuid)
  args.add_argument("-char_uuid", help=f"The UUID of the characteristic, default: {g_char_uuid}", default=g_char_uuid)
  args.add_argument("-log_level", help=f"The log level ({logging.getLevelNamesMapping().keys()}), default: {logging.getLevelName(logger.getEffectiveLevel())}", default=logging.getLevelName(logger.level))
  args.add_argument("-service_name", help=f"The name of the service, default: {g_service_name}", default=g_service_name)


  args = args.parse_args()
  g_service_uuid = args.service_uuid
  g_char_uuid = args.char_uuid
  g_api_url = "http://" + args.api_url
  g_service_name = args.service_name
  if args.log_level not in logging.getLevelNamesMapping().keys():
    logger.error(f"Invalid log level {args.log_level} continuing with default log level.")
  else:
    logger.setLevel(logging.getLevelName(args.log_level))
  
  asyncio.run(run())