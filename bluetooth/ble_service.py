import logging
import asyncio
import threading

import aiohttp
import requests

import egwttp

from typing import Tuple
from typing import Any

import wifiprov

from bless import (  # type: ignore
    BlessServer,
    BlessGATTCharacteristic,
    GATTCharacteristicProperties,
    GATTAttributePermissions
)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(name=__name__)
trigger: asyncio.Event = asyncio.Event()

service_uuid = "A07498CA-AD5B-474E-940D-16F1FBE7E8CD"
char_uuid = "51FF12BB-3ED8-46E5-B4F9-D64E2FEC021B"
server = None


def read_request(characteristic: BlessGATTCharacteristic, **kwargs) -> bytearray:
  logger.debug(f"Reading {characteristic.value}")
  return characteristic.value

def request_get(path: str) -> str:
  reply = requests.get('http://localhost:5000' + path)
  egwttp_response = egwttp.construct_response(path, reply.text)
  logger.debug(f"Reply: {egwttp_response}")
  return egwttp_response

def request_post(path: str, content: str) -> str:
  reply = requests.post('http://localhost:5000' + path, data=content)
  egwttp_response = egwttp.construct_response(path, reply.text)
  logger.debug(f"Reply: {egwttp_response}")
  return egwttp_response

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
        server.update_value(service_uuid, char_uuid)   
      else:
        logger.debug("Not a GET or POST request, doing nothing")

      #await post_request(header['path'], content)

      # transfer the request to a http request to the server
      # when the response is received, transfer it to a egwttp response
    else:
        logger.debug("Not a EGWTTP request, doing nothing")
    
    


async def run(loop):
  global server
  trigger.clear()
  # Instantiate the server
  my_service_name = "SrcFul Energy Gateway"
  server = BlessServer(name=my_service_name, loop=loop)
  server.read_request_func = read_request
  server.write_request_func = write_request

  # Add Service
  await server.add_new_service(service_uuid)

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
  await server.add_new_characteristic(
      service_uuid,
      char_uuid,
      char_flags,
      None,
      permissions)

  logger.debug(
      server.get_characteristic(
          char_uuid
      )
  )
  await server.start()
  logger.debug("Advertising")
  logger.info(f"Write '0xF' to the advertised characteristic: {char_uuid}")
  await trigger.wait()
  await asyncio.sleep(2)
  logger.debug("Updating")
  server.get_characteristic(char_uuid)
  server.update_value(service_uuid, char_uuid)
  await asyncio.sleep(5)
  await server.stop()

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
asyncio.run(run(loop))