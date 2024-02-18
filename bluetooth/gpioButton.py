import asyncio
import time
import logging
from typing import Callable
from gpio4 import SysfsGPIO

logger = logging.getLogger(name=__name__)

# How often to check for button presses
MONITOR_CHECK_INTERVAL_SECONDS = 0.05
# Timeframe for double click in seconds
DOUBLE_CLICK_TIMEFRAME_SECONDS = 0.5


class GpioButton:
    def __init__(self, pin_number, when_double_clicked: Callable[[], None]):
        logger.info("Initializing GPIO button on pin %s",pin_number)
        self.gpio = SysfsGPIO(pin_number)
        self.gpio.export = True
        self.gpio.direction = 'in'
        self.when_double_clicked = when_double_clicked
        self.last_clicked_at = None
        self.click_count = 0

    async def run(self):
        while True:
            if not self.is_pressed():
                if self.click_count == 2 and self.when_double_clicked:
                    await self.when_double_clicked()
                self.click_count = 0
            else:
                await self.process_click()

            await asyncio.sleep(MONITOR_CHECK_INTERVAL_SECONDS)

    async def process_click(self):
        if self.last_clicked_at and time.time() - self.last_clicked_at <= DOUBLE_CLICK_TIMEFRAME_SECONDS:
            self.click_count += 1
            self.last_clicked_at = time.time()
        else:
            self.click_count = 1
            self.last_clicked_at = time.time()

    def is_pressed(self):
        return self.gpio.value == 0

    def close(self):
        self.gpio.export = False