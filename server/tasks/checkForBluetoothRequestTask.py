import asyncio
import logging

#from threading import Thread

from .task import Task


from bless import ( BlessServer, BlessGATTCharacteristic,
                    GATTCharacteristicProperties,GATTAttributePermissions)


log = logging.getLogger(__name__)

# inspo from: https://github.com/gitdefllo/lighthouse-weather-station/blob/feature_classic_bluetooth/station/main_lighthouse.py
# pip install git+https://github.com/pybluez/pybluez.git#egg=pybluez - on windows at least

def construct_egwtp_response(data: str) -> bytes:
  # we construct a response similar to http
  # eg. EGWTP/1.1 200 OK
  #     Content-Type: text/json
  #     Content-Length: 123

  header = "EGWTP/1.1 200 OK\r\n"
  header += "Content-Type: text/json\r\n"
  header += "Content-Length: {}\r\n\r\n".format(len(data.encode('utf-8')))
  content = header + data

  return content.encode('utf-8')

def parse_egwtp_request(data: str) -> dict:
  # we parse a request similar to http
  # eg. GET /api/endpoint EGWTP/1.1
  #     Content-Type: text/json
  #     Content-Length: 123

  header, content = data.split("\r\n\r\n")
  header_lines = header.split("\r\n")

  header_line = header_lines[0]
  header_line_parts = header_line.split(" ")

  header_lines = header_lines[1:]
  header_lines = [line.split(": ") for line in header_lines]
  header_dict = {line[0]: line[1] for line in header_lines}
  header_dict['method'] = header_line_parts[0]
  header_dict['path'] = header_line_parts[1]
  header_dict['version'] = header_line_parts[2]

  return header_dict, content


import asyncio
from bleak import BleakClient, BleakScanner
from typing import Any, List


def read_request(characteristic: BlessGATTCharacteristic, **kwargs) -> bytearray:
  log.debug(f"Reading {characteristic.value}")
  return characteristic.value

def write_request(characteristic: BlessGATTCharacteristic, value: Any, **kwargs):
  characteristic.value = "Hello World: ".encode() + value
  log.debug(f"Char value set to {characteristic.value}")

class CheckForBLERequest(Task):

  async def _create_ble_service(self):
    log.debug("Creating Bless server")
    my_service_name = "SrcFul EGW"
    server = BlessServer(name=my_service_name)
    server.read_request_func = read_request
    server.write_request_func = write_request

    # Add Service
    log.debug("Adding service")
    my_service_uuid = "A07498CA-AD5B-474E-940D-16F1FBE7E8CD"
    await server.add_new_service(my_service_uuid)

    # Add a Characteristic to the service
    my_char_uuid = "51FF12BB-3ED8-46E5-B4F9-D64E2FEC021B"
    char_flags = (GATTCharacteristicProperties.read |
                  GATTCharacteristicProperties.write |
                  GATTCharacteristicProperties.indicate)
    permissions = ( GATTAttributePermissions.readable |
                    GATTAttributePermissions.writeable)
    
    log.debug("Adding characteristic")
    await server.add_new_characteristic(
            my_service_uuid,
            my_char_uuid,
            char_flags,
            None,
            permissions)

    log.debug(server.get_characteristic(my_char_uuid))
    await server.start()
    log.debug("Advertising")
    log.info(f"Write '0xF' to the advertised characteristic: {my_char_uuid}")
    return server


  def __init__(self, eventTime: int, stats: dict):
    super().__init__(eventTime, stats)
    if not 'btRequests' in self.stats:
      self.stats['btRequests'] = 0

    # check if there is a nother event loop
    # if so, use that one
    # if not, create a new one
    try:
      loop = asyncio.get_running_loop()
      log.info("Event loop found, using it")
      self.server = loop.run_until_complete(self._create_ble_service())
    except RuntimeError:
      log.info("No event loop found, creating a new one")
      self.server = asyncio.run(self._create_ble_service())

    log.info("BLE Service created Waiting for BLE connection")
  
  def __del__(self):
    asyncio.run(self.server.stop())
    log.info("BLE Service destroyed")


  def execute(self, eventTime: int) -> None | Task | List[Task]:
      
      # we likely need to collect some(?) of the requests and prepare responses
      # as these need to be synchronous and not interfere with harvesting etc.
      # there could also be other tasks that should be created and then returned

      self.time += eventTime
      return self
  


