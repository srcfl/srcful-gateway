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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(name=__name__)

SERVICE_NAME = f"SrcFul Energy Gateway {macAddr.get().replace(':', '')[-6:]}"  # we cannot use special characters in the name as this will mess upp the bluez service name filepath

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
gateway = None

async def run(gpio_button_pin: int = -1):
    global SERVER
    global gateway
    trigger.clear()
    
    # Instantiate the server
    SERVER = BlessServer(name=SERVICE_NAME, name_overwrite=True)
    gateway = Gateway(SERVER)
    await gateway.init_gateway()

    SERVER.read_request_func = gateway.handle_read_request
    SERVER.write_request_func = gateway.handle_write_request

    logger.info("Starting server...")
    try:
        started = await SERVER.start()
        if not started:
            logger.error("Failed to start server")
            raise RuntimeError("Failed to start server")
    except Exception as e:
        logger.error(f"Error starting server: {e}")
        raise  # Re-raise the exception to stop execution

    logger.info("Server started successfully!")

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

    try:
        # Run indefinitely or until interrupted
        while True:
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        logger.info("Server operation cancelled")
    finally:
        logger.info("Stopping server...")
        await SERVER.stop()


if __name__ == "__main__":
    logger.info("Starting ble service... ")

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
    logger.info("BLE service called with arguments: %s", args)
    
    API_URL = "http://" + args.api_url
    SERVICE_NAME = args.service_name
    if args.log_level not in logging.getLevelNamesMapping().keys():
        logger.error(
            "Invalid log level %s continuing with default log level.", args.log_level
        )
    else:
        logger.setLevel(logging.getLevelName(args.log_level))
    
    # Add this line to ensure you're seeing all INFO messages
    logging.getLogger().setLevel(logging.INFO)

    asyncio.run(run(args.gpio_button_pin))