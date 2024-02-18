import asyncio
import time
import logging
from gpio4 import SysfsGPIO

logger = logging.getLogger(name=__name__)

# How often to check for button presses
MONITOR_CHECK_INTERVAL_SECONDS = 0.05


class GpioButton:
    def __init__(self, pin_number, hold_seconds, when_held:function):
        logger.info("Initializing GPIO button on pin %s" % pin_number)
        self.gpio = SysfsGPIO(pin_number)
        self.gpio.export = True
        self.gpio.direction = 'in'
        self.hold_seconds = hold_seconds
        self.when_held = when_held
        self.last_pressed_at = None
        self.is_press_already_registered = False
        self.reset_pressed_state()

    async def run(self):
        while True:
            if not self.is_pressed():
                self.reset_pressed_state()
            else:
                await self.process_press()

            await asyncio.sleep(MONITOR_CHECK_INTERVAL_SECONDS)


    async def process_press(self):
        if self.last_pressed_at is None:
            logger.debug("Button pressed for first time")
            self.last_pressed_at = time.time()
        else:
            await self.trigger_when_held_after_hold_seconds()


    async def trigger_when_held_after_hold_seconds(self):
        if self.when_held and not self.is_press_already_registered:
            if self.have_hold_seconds_elapsed():
                logger.debug("Button pressed down for `hold_seconds` (%s secs)", self.hold_seconds)
                self.is_press_already_registered = True
                await self.when_held()


    def have_hold_seconds_elapsed(self):
        elapsed_seconds = time.time() - self.last_pressed_at
        return elapsed_seconds >= self.hold_seconds


    def reset_pressed_state(self):
        self.last_pressed_at = None
        self.is_press_already_registered = False


    def is_pressed(self):
        return self.gpio.value == 0


    def close(self):
        self.gpio.export = False