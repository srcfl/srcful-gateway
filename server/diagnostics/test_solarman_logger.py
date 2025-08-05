#!/usr/bin/env python3
"""
Test script for solarman diagnostic logger.
This can be used to verify the logging system works correctly.
"""

import os
import tempfile
import time
from datetime import datetime
from server.diagnostics.solarman_logger import SolarmanDiagnosticLogger, SolarmanLogEntry


class MockSolarmanDevice:
    """Mock solarman device for testing"""

    def __init__(self, sn="TEST123", ip="192.168.1.100"):
        self.sn = sn
        self.ip = ip

    def get_SN(self):
        return self.sn


def test_diagnostic_logger():
    """Test the diagnostic logger functionality"""

    # Create a temporary file for testing
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        test_log_path = f.name

    try:
        # Initialize logger with test file (using custom path for testing)
        logger = SolarmanDiagnosticLogger(test_log_path)

        # Create mock device
        device = MockSolarmanDevice()

        print(f"Testing diagnostic logger with file: {test_log_path}")

        # Test ping functionality
        print("\n1. Testing ping functionality:")
        success, response_time = logger.ping_device("8.8.8.8", timeout=3)
        print(f"   Ping 8.8.8.8: success={success}, time={response_time}ms")

        success, response_time = logger.ping_device("192.168.255.255", timeout=2)  # Should fail
        print(f"   Ping invalid IP: success={success}, time={response_time}ms")

        # Test exception logging
        print("\n2. Testing exception logging:")
        try:
            raise ConnectionError("Test connection error")
        except Exception as e:
            logger.log_exception(device, e, 42, 12500, 2000)
            print(f"   Logged exception: {e}")

        # Test connection failure logging
        print("\n3. Testing connection failure logging:")
        logger.log_connection_failure(device, "Test connection failure", "Additional test info")
        print("   Logged connection failure")

        # Test statistics logging
        print("\n4. Testing statistics logging:")
        stats = {"avg_harvest_time_ms": 125.5, "test_stat": "test_value"}
        logger.log_statistics(device, 100, 25000, 1500, stats)
        print("   Logged statistics")

        # Test ping test logging
        print("\n5. Testing ping test logging:")
        logger.log_ping_test(device, "Manual ping test")
        print("   Logged ping test")

        # Read and display the log file
        print(f"\n6. Log file contents ({test_log_path}):")
        with open(test_log_path, 'r') as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                print(f"   Line {i+1}: {line.strip()}")

        print(f"\nTest completed successfully!")
        print(f"Created {len(lines)} log entries (including header)")

    finally:
        # Clean up
        if os.path.exists(test_log_path):
            os.unlink(test_log_path)
            print(f"Cleaned up test file: {test_log_path}")


if __name__ == "__main__":
    test_diagnostic_logger()
