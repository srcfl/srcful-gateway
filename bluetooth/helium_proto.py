"""
Example for a BLE 4.0 Server
"""


import sys
import logging
import asyncio
import threading
from uuid import UUID
import helium


from typing import Any, Union

import protos.wifi_services_pb2 as wifi_services_pb2
import protos.add_gateway_pb2 as add_gateway_pb2
import protos.wifi_connect_pb2 as wifi_connect_pb2
import protos.diagnostics_pb2 as diagnostics_pb2


from bless import (  # type: ignore
    BlessServer,
    BlessGATTCharacteristic,
    GATTCharacteristicProperties,
    GATTAttributePermissions,
)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(name=__name__)

# NOTE: Some systems require different synchronization methods.
trigger: Union[asyncio.Event, threading.Event]
if sys.platform in ["darwin", "win32"]:
    trigger = threading.Event()
else:
    trigger = asyncio.Event()

SERVER: BlessServer = None

def read_request(characteristic: BlessGATTCharacteristic, **kwargs) -> bytearray:
    logger.debug(f"Reading {characteristic.value}")
    return characteristic.value


def write_request(characteristic: BlessGATTCharacteristic, value: Any, **kwargs):
    logger.debug(f"Writing!!")
    if characteristic.uuid == helium.add_gatway:
        threading.Thread(target=helium.add_gateway, args=(SERVER, characteristic, value,)).start()
    elif characteristic.uuid == helium.wifi_connect:
        
        threading.Thread(target=helium.connect_wifi, args=(SERVER, characteristic, value,)).start()

    else:
        characteristic.value = value
        logger.debug(f"Char value set to {characteristic.value}")
        if characteristic.value == b"\x0f":
            logger.debug("NICE")
            trigger.set()


from bless.backends.bluezdbus.service import BlessGATTServiceBlueZDBus
from bless.backends.bluezdbus.characteristic import BlessGATTCharacteristicBlueZDBus
from typing import List

class DeviceInfoService(BlessGATTServiceBlueZDBus):
    def __init__(self):
        super(DeviceInfoService, self).__init__('0000180a-0000-1000-8000-00805f9b34fb')  # here we use the full uuid for the device info service
        self._uuid: str = '180A'  # here we use the short uuid for the device info service

class DeviceInfoCharacteristic(BlessGATTCharacteristicBlueZDBus):
    def __init__(self, uuid: Union[str, UUID], short_uuid: str, properties: GATTCharacteristicProperties, permissions: GATTAttributePermissions, value: bytearray):
        super(DeviceInfoCharacteristic, self).__init__(uuid, properties, permissions, value)
        self._uuid: str = short_uuid


async def run(loop):
    trigger.clear()
    # Instantiate the server
    my_service_name = "Srcful Hotspot"
    global SERVER
    SERVER = BlessServer(name=my_service_name, loop=loop, name_overwrite=True)
    SERVER.read_request_func = read_request
    SERVER.write_request_func = write_request


    # device info service does not work on windows
    #await add_helium_device_info_service(SERVER)
    await helium.add_custom_service(SERVER)
    await helium.add_device_info_service(SERVER)

    

    # Add a Characteristic to the service
    my_char_uuid = "51FF12BB-3ED8-46E5-B4F9-D64E2FEC021B"
    char_flags = (
        GATTCharacteristicProperties.read
        | GATTCharacteristicProperties.write
        | GATTCharacteristicProperties.indicate
    )
    permissions = GATTAttributePermissions.readable | GATTAttributePermissions.writeable
    await SERVER.add_new_characteristic(
        helium.helium_service_uuid, my_char_uuid, char_flags, None, permissions
    )

    logger.debug(SERVER.get_characteristic(my_char_uuid))
    await SERVER.start()
    logger.debug("Advertising")
    logger.info(f"Write '0xF' to the advertised characteristic: {my_char_uuid}")
    try:
        if trigger.__module__ == "threading":
            trigger.wait()
        else:
            await trigger.wait()
    except KeyboardInterrupt:
        print("Server stopped by user")
        await SERVER.stop()
        trigger.set()

    if not trigger.is_set():
        await asyncio.sleep(2)
        logger.debug("Updating")
        SERVER.get_characteristic(my_char_uuid)
        SERVER.update_value(my_service_uuid, "51FF12BB-3ED8-46E5-B4F9-D64E2FEC021B")
        await asyncio.sleep(5)
        await SERVER.stop()


try:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(loop))
except KeyboardInterrupt:
    SERVER.stop()
    print("Server stopped by user")