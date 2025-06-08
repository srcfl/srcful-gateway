import asyncio
import time
import logging
from enum import Enum
from typing import Callable, Optional
from gpio4 import SysfsGPIO

logger = logging.getLogger(name=__name__)

# How often to check for button presses
MONITOR_CHECK_INTERVAL_SECONDS = 0.05
# Duration for long press in seconds
LONG_PRESS_DURATION_SECONDS = 3.0
# Timeframe for double click in seconds
DOUBLE_CLICK_TIMEFRAME_SECONDS = 1.5


class ButtonState(Enum):
    IDLE = "idle"
    PRESSED = "pressed"
    WAITING_FOR_SECOND_CLICK = "waiting_for_second_click"


class GpioButton:
    def __init__(self, pin_number, when_interaction: Optional[Callable[[str], None]] = None):
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

        self.when_interaction = when_interaction

        self.state = ButtonState.IDLE
        self.state_start_time = None

    async def run(self):
        while True:
            current_pressed = self.is_pressed()
            current_time = time.time()

            if self.state == ButtonState.IDLE:
                if current_pressed:
                    logger.info("Button pressed")
                    self.state = ButtonState.PRESSED
                    self.state_start_time = current_time

            elif self.state == ButtonState.PRESSED:
                if not current_pressed:
                    # Button released - was it a short press?
                    if self.when_interaction:
                        self.state = ButtonState.WAITING_FOR_SECOND_CLICK
                        self.state_start_time = current_time
                    else:
                        self.state = ButtonState.IDLE
                elif current_time - self.state_start_time >= LONG_PRESS_DURATION_SECONDS:
                    # Long press detected
                    logger.info("Long press detected")
                    if self.when_interaction:
                        await self.when_interaction()
                    self.state = ButtonState.IDLE

            elif self.state == ButtonState.WAITING_FOR_SECOND_CLICK:
                if current_pressed:
                    # Second press - double click detected
                    logger.info("Double click detected")
                    if self.when_interaction:
                        await self.when_interaction()
                    self.state = ButtonState.IDLE
                elif current_time - self.state_start_time >= DOUBLE_CLICK_TIMEFRAME_SECONDS:
                    # Timeout - no second click
                    self.state = ButtonState.IDLE

            await asyncio.sleep(MONITOR_CHECK_INTERVAL_SECONDS)

    def is_pressed(self):
        return self.gpio.value == 0

    def close(self):
        self.gpio.export = False
