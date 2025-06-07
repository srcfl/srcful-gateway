import asyncio
import time
import logging
from typing import Callable
from gpio4 import SysfsGPIO

logger = logging.getLogger(name=__name__)

# How often to check for button presses
MONITOR_CHECK_INTERVAL_SECONDS = 0.05
# Duration for long press in seconds
LONG_PRESS_DURATION_SECONDS = 3.0


class GpioButton:
    def __init__(self, pin_number, when_long_pressed: Callable[[], None]):
        logger.info("Initializing GPIO button on pin %s", pin_number)
        try:
            self.gpio = SysfsGPIO(pin_number)
            # Try to unexport first in case it's already exported
            try:
                self.gpio.export = False
            except:
                pass
            # Now try to export
            self.gpio.export = True
            self.gpio.direction = 'in'
        except OSError as e:
            logger.error(f"Failed to initialize GPIO on pin {pin_number}: {e}")
            raise RuntimeError(f"GPIO initialization failed: {e}")

        self.when_long_pressed = when_long_pressed
        self.press_start_time = None
        self.long_press_triggered = False

    async def run(self):
        while True:
            if self.is_pressed():
                if self.press_start_time is None:
                    # Button just pressed, start timing
                    self.press_start_time = time.time()
                    self.long_press_triggered = False
                elif not self.long_press_triggered:
                    # Check if long press duration has been reached
                    press_duration = time.time() - self.press_start_time
                    if press_duration >= LONG_PRESS_DURATION_SECONDS:
                        logger.info("Long press detected")
                        self.long_press_triggered = True
                        if self.when_long_pressed:
                            await self.when_long_pressed()
            else:
                # Button released, reset timing
                self.press_start_time = None
                self.long_press_triggered = False

            await asyncio.sleep(MONITOR_CHECK_INTERVAL_SECONDS)

    def is_pressed(self):
        return self.gpio.value == 0

    def close(self):
        self.gpio.export = False
