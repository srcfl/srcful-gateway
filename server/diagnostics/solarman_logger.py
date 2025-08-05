import csv
import os
import threading
import time
import logging
import subprocess
import platform
from datetime import datetime
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict
from server.devices.ICom import ICom


logger = logging.getLogger(__name__)


@dataclass
class SolarmanLogEntry:
    """Data class for solarman diagnostic log entries"""
    timestamp: str
    device_sn: str
    device_ip: str
    event_type: str  # 'exception', 'connection_failure', 'statistics', 'ping_test'
    reason: str
    harvest_count: int
    total_harvest_time_ms: int
    backoff_time_ms: int
    ping_success: Optional[bool]
    ping_time_ms: Optional[float]
    exception_details: Optional[str]
    additional_info: Optional[str]


class SolarmanDiagnosticLogger:
    """
    CSV logger for solarman device diagnostics and responsiveness monitoring.
    Logs exceptions, connection failures, ping tests, and periodic statistics.
    """

    def __init__(self, log_file_path: str = None):
        if log_file_path is None:
            # Auto-detect the correct srcful data path
            if os.path.exists("/data/srcful"):
                log_file_path = "/data/srcful/solarman_diagnostics.csv"
            elif os.path.exists("/var/srcful"):
                log_file_path = "/var/srcful/solarman_diagnostics.csv"
            else:
                # Fallback to /tmp if no persistent volume is found
                log_file_path = "/tmp/solarman_diagnostics.csv"
                logger.warning("No persistent volume found, logs will be saved to /tmp and may be lost on container restart")

        self.log_file_path = log_file_path
        self._lock = threading.Lock()
        self._ensure_log_directory()
        self._initialize_csv_file()

    def _ensure_log_directory(self):
        """Ensure the log directory exists"""
        log_dir = os.path.dirname(self.log_file_path)
        os.makedirs(log_dir, exist_ok=True)

    def _initialize_csv_file(self):
        """Initialize CSV file with headers if it doesn't exist"""
        if not os.path.exists(self.log_file_path):
            with open(self.log_file_path, 'w', newline='') as csvfile:
                fieldnames = [
                    'timestamp', 'device_sn', 'device_ip', 'event_type', 'reason',
                    'harvest_count', 'total_harvest_time_ms', 'backoff_time_ms',
                    'ping_success', 'ping_time_ms', 'exception_details', 'additional_info'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

    def ping_device(self, ip: str, timeout: int = 5) -> tuple[bool, Optional[float]]:
        """
        Ping a device and return success status and response time.

        Args:
            ip: IP address to ping
            timeout: Timeout in seconds

        Returns:
            Tuple of (success, response_time_ms)
        """
        try:
            # Determine ping command based on OS
            if platform.system().lower() == "windows":
                cmd = ["ping", "-n", "1", "-w", str(timeout * 1000), ip]
            else:
                cmd = ["ping", "-c", "1", "-W", str(timeout), ip]

            start_time = time.time()
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 1)
            end_time = time.time()

            success = result.returncode == 0
            response_time = (end_time - start_time) * 1000 if success else None

            logger.debug(f"Ping {ip}: {'success' if success else 'failed'}, time: {response_time}ms")
            return success, response_time

        except subprocess.TimeoutExpired:
            logger.debug(f"Ping {ip}: timeout")
            return False, None
        except Exception as e:
            logger.error(f"Error pinging {ip}: {e}")
            return False, None

    def log_exception(self, device: ICom, exception: Exception, harvest_count: int,
                      total_harvest_time_ms: int, backoff_time_ms: int):
        """Log an exception with ping test"""
        device_ip = getattr(device, 'ip', 'unknown')
        ping_success, ping_time = self.ping_device(device_ip)

        entry = SolarmanLogEntry(
            timestamp=datetime.now().isoformat(),
            device_sn=device.get_SN(),
            device_ip=device_ip,
            event_type='exception',
            reason=f"{type(exception).__name__}: {str(exception)}",
            harvest_count=harvest_count,
            total_harvest_time_ms=total_harvest_time_ms,
            backoff_time_ms=backoff_time_ms,
            ping_success=ping_success,
            ping_time_ms=ping_time,
            exception_details=str(exception),
            additional_info=None
        )

        self._write_log_entry(entry)
        logger.info(f"Logged exception for {device.get_SN()}: {str(exception)}, ping: {ping_success}")

    def log_connection_failure(self, device: ICom, reason: str, additional_info: Optional[str] = None):
        """Log a connection failure with ping test"""
        device_ip = getattr(device, 'ip', 'unknown')
        ping_success, ping_time = self.ping_device(device_ip)

        entry = SolarmanLogEntry(
            timestamp=datetime.now().isoformat(),
            device_sn=device.get_SN(),
            device_ip=device_ip,
            event_type='connection_failure',
            reason=reason,
            harvest_count=0,
            total_harvest_time_ms=0,
            backoff_time_ms=0,
            ping_success=ping_success,
            ping_time_ms=ping_time,
            exception_details=None,
            additional_info=additional_info
        )

        self._write_log_entry(entry)
        logger.info(f"Logged connection failure for {device.get_SN()}: {reason}, ping: {ping_success}")

    def log_statistics(self, device: ICom, harvest_count: int, total_harvest_time_ms: int,
                       backoff_time_ms: int, additional_stats: Optional[Dict[str, Any]] = None):
        """Log periodic statistics"""
        device_ip = getattr(device, 'ip', 'unknown')
        entry = SolarmanLogEntry(
            timestamp=datetime.now().isoformat(),
            device_sn=device.get_SN(),
            device_ip=device_ip,
            event_type='statistics',
            reason='periodic_statistics',
            harvest_count=harvest_count,
            total_harvest_time_ms=total_harvest_time_ms,
            backoff_time_ms=backoff_time_ms,
            ping_success=None,
            ping_time_ms=None,
            exception_details=None,
            additional_info=str(additional_stats) if additional_stats else None
        )

        self._write_log_entry(entry)
        logger.debug(f"Logged statistics for {device.get_SN()}: {harvest_count} harvests")

    def log_ping_test(self, device: ICom, reason: str):
        """Log a standalone ping test"""
        device_ip = getattr(device, 'ip', 'unknown')
        ping_success, ping_time = self.ping_device(device_ip)

        entry = SolarmanLogEntry(
            timestamp=datetime.now().isoformat(),
            device_sn=device.get_SN(),
            device_ip=device_ip,
            event_type='ping_test',
            reason=reason,
            harvest_count=0,
            total_harvest_time_ms=0,
            backoff_time_ms=0,
            ping_success=ping_success,
            ping_time_ms=ping_time,
            exception_details=None,
            additional_info=None
        )

        self._write_log_entry(entry)
        logger.debug(f"Logged ping test for {device.get_SN()}: {ping_success}")

    def _write_log_entry(self, entry: SolarmanLogEntry):
        """Write a log entry to the CSV file"""
        with self._lock:
            try:
                with open(self.log_file_path, 'a', newline='') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=asdict(entry).keys())
                    writer.writerow(asdict(entry))
            except Exception as e:
                logger.error(f"Failed to write log entry: {e}")


# Global instance
_diagnostic_logger = None


def get_diagnostic_logger() -> SolarmanDiagnosticLogger:
    """Get the global diagnostic logger instance"""
    global _diagnostic_logger
    if _diagnostic_logger is None:
        _diagnostic_logger = SolarmanDiagnosticLogger()
    return _diagnostic_logger
