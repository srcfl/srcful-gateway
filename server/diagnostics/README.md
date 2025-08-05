# Solarman Diagnostics Logging

This module provides comprehensive logging and diagnostics for Solarman devices to help debug responsiveness issues.

## Features

- **Exception Logging**: Automatically logs all exceptions during harvest operations with ping tests
- **Connection Failure Logging**: Logs connection failures during device opening with ping tests
- **Periodic Statistics**: Logs device statistics every 5 minutes
- **Ping Testing**: Tests device responsiveness via ICMP ping on all failures
- **CSV Output**: All logs are saved in CSV format for easy analysis

## Log Location

Logs are saved to the `srcful-data` persistent volume:

- `/data/srcful/solarman_diagnostics.csv` (most configurations)
- `/var/srcful/solarman_diagnostics.csv` (docker-compose-no-ecc.yml)
- `/tmp/solarman_diagnostics.csv` (fallback if no volume detected)

## CSV Columns

| Column                | Description                                                                 |
| --------------------- | --------------------------------------------------------------------------- |
| timestamp             | ISO format timestamp of the event                                           |
| device_sn             | Serial number of the solarman device                                        |
| device_ip             | IP address of the device                                                    |
| event_type            | Type of event: 'exception', 'connection_failure', 'statistics', 'ping_test' |
| reason                | Reason for the event/error description                                      |
| harvest_count         | Number of successful harvests                                               |
| total_harvest_time_ms | Total time spent harvesting (ms)                                            |
| backoff_time_ms       | Current backoff time (ms)                                                   |
| ping_success          | Whether ping was successful (True/False/null)                               |
| ping_time_ms          | Ping response time in milliseconds                                          |
| exception_details     | Full exception details if applicable                                        |
| additional_info       | Additional context information                                              |

## Event Types

### exception

Logged when an exception occurs during data harvesting. Includes:

- Full exception details
- Ping test to verify device connectivity
- Current harvest statistics

### connection_failure

Logged when device connection fails. Includes:

- Reason for failure
- Ping test to verify device connectivity
- Device configuration details

### statistics

Logged every 5 minutes for active solarman devices. Includes:

- Total harvest count
- Average harvest time
- Current backoff time
- No ping test (to avoid unnecessary network traffic)

### ping_test

Standalone ping tests (currently not used but available for manual testing)

## Usage

The logging is automatically enabled for all solarman devices. No configuration is required.

### Accessing Logs

1. **Via Docker**:

   ```bash
   # Most configurations use /data/srcful
   docker exec -it <container_name> cat /data/srcful/solarman_diagnostics.csv

   # docker-compose-no-ecc.yml uses /var/srcful
   docker exec -it <container_name> cat /var/srcful/solarman_diagnostics.csv
   ```

2. **Copy from container**:

   ```bash
   # Most configurations
   docker cp <container_name>:/data/srcful/solarman_diagnostics.csv ./solarman_diagnostics.csv

   # docker-compose-no-ecc.yml
   docker cp <container_name>:/var/srcful/solarman_diagnostics.csv ./solarman_diagnostics.csv
   ```

3. **Analysis with tools**:

   ```bash
   # Find the log file location first
   docker exec -it <container_name> find /data /var /tmp -name "solarman_diagnostics.csv" 2>/dev/null

   # Then use the found path (example with /data/srcful)
   # View recent exceptions
   tail -n 100 /data/srcful/solarman_diagnostics.csv | grep exception

   # View statistics entries
   grep "statistics" /data/srcful/solarman_diagnostics.csv

   # Check ping failures
   grep "False" /data/srcful/solarman_diagnostics.csv
   ```

## Troubleshooting Scenarios

### Device becomes unresponsive

1. Check for recent exceptions in the log
2. Look at ping_success column - if False, network issue
3. Check backoff_time_ms - high values indicate repeated failures
4. Compare harvest_count over time to see if harvesting stopped

### Intermittent connectivity

1. Look for patterns in connection_failure events
2. Check ping response times (ping_time_ms) for high latency
3. Monitor statistics logs for changing average harvest times

### Performance degradation

1. Monitor avg_harvest_time_ms in statistics entries
2. Check if backoff_time_ms is increasing over time
3. Look for correlation between high harvest times and exceptions

## Implementation Details

- Logging is thread-safe using file locking
- Ping uses system ping command with configurable timeout
- Statistics are tracked per Harvest instance (per device)
- Only solarman devices are logged to avoid noise from other device types
- CSV headers are automatically created if file doesn't exist
