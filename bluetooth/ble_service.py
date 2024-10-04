import logging
import asyncio
import sys
import argparse
from bless import (  # type: ignore
    BlessServer
)
try:
    from gpioButton import GpioButton
except ImportError:
    GpioButton = None
from gateway import Gateway
import constants
import macAddr

# change root logger level to debug
# Configure the root logger
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    stream=sys.stdout)
logger = logging.getLogger(__name__)


SERVICE_NAME = f"SrcFul Energy Gateway {macAddr.get().replace(':', '')[-6:]}"  # we cannot use special characters in the name as this will mess upp the bluez service name filepath

SERVER = None
gateway = None

if sys.platform == "linux":
    # if we are on a bluez backend then we add the start and stop advertising functions
    logger.warning("Using bluez backend, adding start and stop advertising functions")

    async def start_advertising():
        logger.warning("Starting advertising")
        # we depend on that we are now on a bluez backend
        await SERVER.app.start_advertising(SERVER.adapter)
        # we don't create a new task as the button loop should be blocked until we have stoped advertising
        await stop_advertising()

    async def stop_advertising():
        logger.warning("Stopping advertising in 3 minutes")
        await asyncio.sleep(60 * 3)
        logger.warning("Stopping advertising...")

        # we depend on that we are now on a bluez backend
        adv = SERVER.app.advertisements[0]
        await SERVER.app.stop_advertising(SERVER.adapter)

        # we also need to remove the exported advertisement endpoint
        # this is a hack to get bless start advertising to work
        SERVER.app.bus.unexport(adv.path, adv)
        logger.warning("Stopped advertising")

else:
    logger.warning(
        "Not using bluez backend, not adding start and stop advertising functions"
    )

# this trigger is never used atm but could be used to signal the main thread that a request has been received
trigger: asyncio.Event = asyncio.Event()
gateway = None

async def run(gpio_button_pin: int = -1):
    global SERVER
    global gateway
    trigger.clear()
    
    logger.warning("Initializing server...")
    # Instantiate the server
    SERVER = BlessServer(name=SERVICE_NAME, name_overwrite=True)
    logger.warning("Server instantiated")
    
    logger.warning("Adding new service...")
    await SERVER.add_new_service(constants.SERVICE_UUID)
    logger.debug(f"Added service {constants.SERVICE_UUID}")

    logger.warning("Initializing Gateway...")
    gateway = Gateway(SERVER)
    logger.warning("Gateway initialized")
    
    logger.warning("Initializing gateway...")
    await gateway.init_gateway()
    logger.warning("Gateway initialized")

    SERVER.read_request_func = gateway.handle_read_request
    SERVER.write_request_func = gateway.handle_write_request
    logger.warning("Request handlers set")
    
    logger.warning("Starting server...")
    try:
        logger.warning("Calling SERVER.start()...")
        started = await SERVER.start()
        logger.warning(f"SERVER.start() returned: {started}")
        if not started:
            logger.error("Failed to start server")
            raise RuntimeError("Failed to start server")
    except Exception as e:
        logger.error(f"Error starting server: {e}")
        raise  # Re-raise the exception to stop execution

    logger.warning("Server started successfully!")

    # if we are using the bluez backend and gpio buttin is set then we stop advertising after 3 minutes and also set up the button
    if sys.platform == "linux" and gpio_button_pin >= 0:
        logger.warning("Using bluez backend, adding button on pin %s", gpio_button_pin)
        await stop_advertising()
        button = GpioButton(gpio_button_pin, start_advertising)
        asyncio.create_task(button.run())
    else:
        logger.warning(
            "Not using bluez backend or pin < 0 (pin is: %s), advertising indefinitely",
            gpio_button_pin,
        )

    try:
        # Run indefinitely or until interrupted
        while True:
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        logger.warning("Server operation cancelled")
    finally:
        logger.warning("Stopping server...")
        await SERVER.stop()


if __name__ == "__main__":
    logger.warning("Starting ble service... ")

    args = argparse.ArgumentParser()
    args.add_argument(
        "-api_url",
        help=f"The url of the API endpoint, default: {constants.SRCFUL_GW_API_ENDPOINT}",
        default=constants.SRCFUL_GW_API_ENDPOINT,
    )

    args.add_argument(
        "-gpio_button_pin",
        help="Pin for a gpio button to start advertising on double click, default: -1 (eternal advertising)",
        default=-1,
        type=int,
    )

    args.add_argument(
        "-service_name",
        help=f"The name of the service, default: {SERVICE_NAME}",
        default=SERVICE_NAME,
    )

    args = args.parse_args()
    logger.warning("BLE service called with arguments: %s", args)
    
    API_URL = "http://" + args.api_url
    SERVICE_NAME = args.service_name


    asyncio.run(run(args.gpio_button_pin))