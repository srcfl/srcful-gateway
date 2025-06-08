import asyncio
import time
from unittest.mock import Mock, patch, AsyncMock, MagicMock


def test_double_click():
    """Test double click detection"""
    mock_gpio4 = MagicMock()
    mock_gpio_instance = MagicMock()
    mock_gpio_instance.value = 1  # Not pressed initially
    mock_gpio4.SysfsGPIO.return_value = mock_gpio_instance

    async def run_test():
        with patch.dict('sys.modules', {'gpio4': mock_gpio4}):
            from bluetooth.gpioButton import GpioButton, ButtonState

            interaction_callback = AsyncMock()
            button = GpioButton(18, when_interaction=interaction_callback)
            button.gpio = mock_gpio_instance

            task = asyncio.create_task(button.run())

            try:
                print("Testing double click...")

                # First press
                mock_gpio_instance.value = 0
                await asyncio.sleep(0.1)
                print(f"  First press: {button.state}")

                # First release
                mock_gpio_instance.value = 1
                await asyncio.sleep(0.1)
                print(f"  First release: {button.state}")

                # Second press
                mock_gpio_instance.value = 0
                await asyncio.sleep(0.1)
                print(f"  Second press: {button.state}")

                if interaction_callback.called:
                    # Check that it was called with "double_click"
                    interaction_callback.assert_called_once()
                    print("  ✓ Double click detected!")
                else:
                    print("  ✗ Double click NOT detected")

            finally:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

    return asyncio.run(run_test())


def test_long_press():
    """Test long press detection"""
    mock_gpio4 = MagicMock()
    mock_gpio_instance = MagicMock()
    mock_gpio_instance.value = 1  # Not pressed initially
    mock_gpio4.SysfsGPIO.return_value = mock_gpio_instance

    async def run_test():
        with patch.dict('sys.modules', {'gpio4': mock_gpio4}):
            from bluetooth.gpioButton import GpioButton, ButtonState, LONG_PRESS_DURATION_SECONDS

            interaction_callback = AsyncMock()
            button = GpioButton(18, when_interaction=interaction_callback)
            button.gpio = mock_gpio_instance

            task = asyncio.create_task(button.run())

            try:
                print("Testing long press...")

                # Press and hold
                mock_gpio_instance.value = 0
                await asyncio.sleep(0.1)
                print(f"  Button pressed: {button.state}")

                # Simulate time passing for long press
                original_time = time.time()
                with patch('time.time', return_value=original_time + LONG_PRESS_DURATION_SECONDS + 0.1):
                    await asyncio.sleep(0.1)

                if interaction_callback.called:
                    # Check that it was called with "long_press"
                    interaction_callback.assert_called_once()
                    print("  ✓ Long press detected!")
                else:
                    print("  ✗ Long press NOT detected")

            finally:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

    return asyncio.run(run_test())


if __name__ == "__main__":
    print("Testing GPIO Button...")
    print("=" * 30)

    test_double_click()
    print()
    test_long_press()

    print("=" * 30)
    print("Tests completed!")
