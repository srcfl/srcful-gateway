# Blixt Gateway Test Specification - Robustness Testing

## Overview

This document specifies robustness test requirements for the Blixt inverter gateway system. Blixt serves as a critical bridge between inverters and internet connectivity, requiring reliable operation under various network conditions and failure scenarios. The gateway must maintain inverter communication and data integrity regardless of internet connectivity status.

While following a spec is good, as a tester you need to be creative in setups and situations. The idea is not to mechanically follow a spec, and ticking the boxes, rather it is to give an as true view of the status of the Blixt as possible.

Do not hesitate to add test cases, procedures, details tips and trix to the specification.

## Robustness Testing

#### 1.1 Network Connectivity Tests

**Test ID: ROB-001 - Blixt Offline Operation**
- **Description**: Verify Blixt operates correctly without internet connectivity. Both ethernet and wifi should be tested for the network connection.
- **Test Steps**:
  1. Disconnect internet connection while Blixt is running
  2. Monitor inverter communication continues uninterrupted
  3. Verify local data logging/buffering functions
  4. Check status indicators reflect offline state
  5. Confirm inverter monitoring and control remains fully functional
- **Expected Result**: Blixt maintains all inverter communication and logs data locally with no degradation
- **Duration**: 1h continuous operation, on occation longer tests are beneficial
- **Success Criteria**: 
  - Zero inverter communication failures
  - All data points captured and buffered
  - Local interface shows offline state/data sending issues
  - Local web interface remains accessible
  - TODO: Decide how remote control features should behave.

**Test ID: ROB-002 - Blixt Internet Recovery**
- **Description**: Verify graceful recovery when internet connectivity is restored to Blixt
- **Test Steps**:
  1. Start with Blixt in offline state (from ROB-001)
  2. Restore internet connection  
  3. Monitor automatic reconnection process
  4. Verify buffered data synchronization and upload
  5. Check status indicators update correctly
  6. Confirm no data gaps or duplicates in uploaded data
- **Expected Result**: Automatic reconnection within 60 seconds, all buffered data uploaded successfully
- **Acceptance Criteria**: 
  - No data loss during offline period
  - No manual intervention required
  - Data timestamps preserved correctly
  - Normal operation resumes seamlessly
  - TODO: Decide how remote control features should behave.

**Test ID: ROB-003 - Blixt Intermittent Connectivity**
- **Description**: Test Blixt behavior with unstable internet connection
- **Test Steps**:
  1. Simulate intermittent connectivity patterns:
     - Pattern A: 5-minute cycles (2 min up, 3 min down)
     - Pattern B: Random intervals (30 sec to 10 min up/down)
     - Pattern C: Brief disconnections (5-30 second outages every 15 minutes)
  2. Run each pattern for 1 hour
  3. Monitor data integrity and system stability
  4. Check for resource exhaustion, e.g. is connect/disconnect patterns stable or do they take longer time as the test progress?
  5. Verify buffer management during transitions
- **Expected Result**: Stable operation across all patterns, no crashes, data consistency maintained
- **Data Collection**:
  - Should behave as defined in previous test cases.
  - Monitor and log all odd-behaviors in test report.

#### 1.2 Power Cycle and Boot Tests

**Test ID: ROB-004 - Blixt Cold Boot Without Internet**
- **Description**: Verify proper Blixt startup sequence when no internet is available
- **Test Steps**:
  1. Ensure no internet connectivity is available
  2. Power cycle Blixt from completely powered off state
  3. Monitor complete boot sequence and initialization
  4. Verify local operations start correctly
  5. Check inverter communication establishment
  6. Confirm offline mode is properly detected and handled
  7. Test local interface accessibility
- **Expected Result**: Complete boot within 120 seconds, all local functions operational
- **Pass Criteria**: 
  - No hanging processes or boot loops
  - Proper error handling for missing internet
  - All inverter connections established
  - System ready for normal offline operation
  - Boot time consistent across multiple attempts

**Test ID: ROB-005 - Blixt Repeated Power Cycles**
- **Description**: Test Blixt resilience to frequent power interruptions
- **Test Steps**:
  1. Perform 200 power cycles with varying scenarios:
     - 100 cycles with internet available
     - 100 cycles without internet
  2. Use random power-off intervals (10-600 seconds)
  3. Alternate between online/offline network states randomly
  4. Monitor system stability and data integrity throughout
  5. Check filesystem consistency after test completion
  6. Verify boot time consistency
- **Expected Result**: No corruption, consistent behavior across all cycles
- **Data Collection**: 
  - Boot times for each cycle
  - Error logs and exceptions
  - Filesystem status checks
  - Memory usage patterns
  - Configuration integrity verification

**Test ID: ROB-006 - Blixt Unclean Shutdown Recovery**
- **Description**: Test Blixt recovery from unexpected power loss during various operations
- **Test Steps**:
  1. During active operations, remove power without shutdown command:
     - While uploading buffered data
     - During inverter communication
     - While writing configuration changes
     - During firmware operations (if applicable)
  2. Restore power after random intervals (5-300 seconds)
  3. Monitor recovery process and data integrity
  4. Repeat 50 times with varying system loads and states
  5. Test both online and offline scenarios
- **Expected Result**: Automatic recovery, no data corruption, proper filesystem recovery
- **Recovery Metrics**:
  - Filesystem check (fsck) completes successfully
  - Configuration files remain valid
  - Buffered data recoverable
  - System returns to previous operational state

**Test ID: ROB-007 - Blixt Boot Sequence Timing**
- **Description**: Verify consistent and reliable boot timing under various conditions
- **Test Steps**:
  1. Measure boot times under different scenarios:
     - Cold boot with internet available
     - Cold boot without internet
     - Warm reboot with internet
     - Warm reboot without internet
     - Boot after unclean shutdown
  2. Perform 20 boots for each scenario
  3. Monitor services startup order and timing
  4. Check for any boot-time race conditions
- **Expected Result**: Consistent boot times within acceptable ranges
- **Timing Requirements**:
  - Cold boot: < 120 seconds
  - Warm reboot: < 60 seconds
  - Boot time variation: < 20% between attempts
  - All critical services start in correct order

#### 1.3 Resource Stress and Endurance Tests

**Test ID: ROB-008 - Blixt Memory Stress**
- **Description**: Verify Blixt stable operation under memory pressure
TODO

**Test ID: ROB-009 - Blixt Storage Stress**
- **Description**: Test Blixt behavior when storage approaches capacity
TODO

**Test ID: ROB-010 - Blixt Long-Term Stability**
- **Description**: Test Blixt stability over extended periods with varying network conditions
TODO

#### 1.4 Environmental and Edge Case Tests

**Test ID: ROB-011 - Blixt Network Interface Recovery**
- **Description**: Test recovery from network interface failures
TODO

**Test ID: ROB-012 - Blixt Concurrent Stress**
- **Description**: Test Blixt under multiple simultaneous stress conditions
TODO

#### 1.5 Inverter Connectivity Tests

**Test ID: ROB-013 - Blixt Inverter Connection Recovery**
- **Description**: Verify Blixt's ability to recover from lost inverter connections
- **Test Steps**:
  1. Simulate inverter connection loss scenarios:
     - Physical disconnection of inverter
     - Network interface failure on inverter
     - Inverter power cycle
  2. Monitor Blixt's reconnection attempts
  3. Verify data collection resumes after reconnection
  4. Check error logging and status indicators
- **Expected Result**: Blixt reconnects to inverter within 6 minutes
- **Success Criteria**:
  - Automatic reconnection within specified timeframe
  - Proper error handling and logging
  - Data collection resumes after reconnection
  - Status indicators accurately reflect connection state

**Test ID: ROB-014 - Blixt Multiple Inverter Connection Management**
- **Description**: Test Blixt's handling of multiple inverter connections with varying stability
- **Test Steps**:
  1. Connect multiple inverters to Blixt
  2. Simulate different connection scenarios:
     - One inverter disconnects while others remain connected
     - Multiple inverters disconnect simultaneously
     - Staggered disconnections and reconnections
  3. Monitor Blixt's connection management
  4. Verify data collection for stable connections
  5. Check reconnection attempts for disconnected inverters
- **Expected Result**: Blixt maintains stable connections and recovers disconnected inverters within 6 minutes
- **Success Criteria**:
  - Stable connections remain unaffected by other disconnections
  - Each disconnected inverter reconnects within 6 minutes
  - No impact on data collection from stable connections
  - Proper error handling and logging for each inverter

**Test ID: ROB-015 - Blixt Inverter Connection Stability**
- **Description**: Test Blixt's behavior with intermittent inverter connections
- **Test Steps**:
  1. Simulate intermittent connection patterns:
     - Pattern A: 2-minute cycles (1 min connected, 1 min disconnected)
     - Pattern B: Random intervals (30 sec to 5 min connected/disconnected)
     - Pattern C: Brief disconnections (5-30 second outages every 10 minutes)
  2. Run each pattern for 1 hour
  3. Monitor reconnection success rate
  4. Verify data collection during stable periods
  5. Check system resource usage during reconnection attempts
- **Expected Result**: Consistent reconnection within 6 minutes for all patterns
- **Success Criteria**:
  - 100% reconnection success rate
  - No resource exhaustion from reconnection attempts
  - Accurate data collection during stable periods
  - Proper error handling and logging

## Test Environment Setup

### Hardware Requirements
- Blixt gateway units for parallel testing
- Network simulation equipment for connectivity testing (managed switches with port disable capability)
- Controllable power supplies for power cycle testing
- Inverter simulators or actual inverter units for load testing
- Computer on same network as blixt and simulator.

### Software Requirements
- blixt.local interface should work in combination with local api-endpoints.

### Test Data Collection Requirements
- Device logs - we likely need an endpoint for this
- Performance metrics:
  - In general use low precision timing for e.g. booting sequence times.
- Error counts and categorization

## Pass/Fail Criteria

### Robustness Pass Criteria
- **System Stability**: Blixt remains stable for minimum test duration without crashes or hangs
- **Data Integrity**: Zero data loss during network/power interruptions, all data timestamps preserved
- **Automatic Recovery**: System recovers without manual intervention within specified timeframes
- **Performance Consistency**: Boot times and resource usage remain within acceptable ranges
- **Offline Operation**: Full functionality maintained without internet connectivity
- **Buffer Management**: Data buffering and synchronization works correctly under all conditions

### Robustness Fail Criteria  
- **System Failure**: Blixt crashes, hangs, or requires manual recovery
- **Data Loss**: Any data corruption, loss, or timestamp inconsistencies detected
- **Performance Degradation**: Boot times exceed limits or system performance degrades over time
- **Recovery Issues**: Manual intervention required for recovery from any failure scenario
- **Resource Leaks**: Memory leaks, disk space issues, or resource exhaustion detected
- **Communication Failure**: Inverter communication interrupted or degraded during any test

## Test Execution Guidelines

### Pre-Test Setup
1. Document baseline performance metrics for comparison
2. Ensure all monitoring tools are configured and operational
3. Verify test environment network configuration
4. Backup any critical Blixt configurations
5. Synchronize all system clocks for accurate logging

### During Test Execution
1. Continuous monitoring of all defined metrics
2. Regular log collection and analysis  
3. Documentation of any anomalies or unexpected behavior
4. Immediate investigation of any failures
5. Preservation of system state for post-test analysis

### Post-Test Analysis
1. Comprehensive log analysis for errors and warnings
2. Performance metrics comparison against baseline
3. Data integrity verification
4. Resource usage pattern analysis
5. Identification of any degradation trends

## Test Reporting

Start each report with a table of testcases/variants executed, and their overall result, Pass, Fail, and a brief comment. Details can follow. Not all tests need to be executed for every report. Try to test things that are not well tested.

### File Naming Standard

Test reports should follow this naming convention:
```rob-<test-ids>-<sequence>.md
```

Examples:
- `rob-013-014-001.md` (covers ROB-013 and ROB-014)
- `rob-002-001.md` (covers ROB-002)
- `rob-013-014-002.md` (another report covering ROB-013 and ROB-014)

Note: Since reports are stored in git, the following metadata is automatically available:
- Author (from git commit)
- Date (from git commit)
- Version history (from git history)
- Related commits and changes

The test IDs in the filename should be the actual test case IDs from this specification (e.g., ROB-013). This makes it easy to:
- Find all reports for a specific test case
- Understand exactly what was tested
- Track test coverage over time
- Link directly to the test specification

### Example Test Report

```markdown
# Blixt Robustness Test Report
**Date**: 2024-03-15  
**Tester**: Local Development Test  
**Firmware Version**: Development Build  
**Test Focus**: Network Recovery and Offline Operation  
**Test Duration**: 15 minutes

## Test Summary Table

| Test ID | Variant | Result | Comment |
|:--------|:--------|:-------|:--------|
| ROB-001 | Wifi disconnect | PASS | System handled disconnect gracefully |
| ROB-002 | Wifi recovery | PASS | Automatic reconnection successful |
| ROB-013 | VPN-based inverter disconnect | PASS | Inverter connection lost and recovered with internet |

## Detailed Results

### ROB-001, ROB-002 & ROB-013 Network and Inverter Connection Recovery
**Test Setup**:
- Blixt running in local development environment
- Connected to real inverter via internet-based VPN at remote site
- Wifi connection to local network
- System in normal operation state

**Test Steps**:
1. System running normally with active inverter connection through VPN
2. Disabled wifi on test computer
3. Monitored system behavior during disconnect
4. Re-enabled wifi
5. Observed recovery process

**Observed Behavior**:
- System detected network loss
- Lost both internet and VPN connection to inverter
- Gracefully handled both connection losses
- Maintained system stability during offline period
- Automatically reconnected to internet when wifi restored
- Automatically reconnected to inverter through VPN
- Normal operations resumed without manual intervention

**Success Criteria Met**:
- ✓ System remained stable during disconnect
- ✓ Proper handling of both internet and inverter disconnection
- ✓ Automatic recovery of both connections when network restored
- ✓ No manual intervention required
- ✓ Normal operation resumed seamlessly

## System Metrics

### Resource Usage
- System remained stable throughout test
- No resource spikes observed during disconnect/reconnect
- Normal operation maintained during all phases

## Test Spec Improvements

1. Add specific test case for VPN-based inverter connections
2. Include metrics for reconnection time for both internet and inverter
3. Add monitoring of inverter communication state during disconnect
4. Specify expected behavior for different network interface types (wifi vs ethernet)
5. Add test scenarios for VPN-based inverter connections in ROB-013

## Reproducibility

To reproduce this test:
1. Set up Blixt in local development environment
2. Establish VPN connection to remote inverter over internet
3. Ensure system is in normal operation
4. Disable wifi on test computer
5. Monitor system behavior
6. Re-enable wifi
7. Verify recovery of both internet and inverter connections

## Follow-up Actions

1. [ ] Add specific wifi disconnect test case to specification
2. [ ] Implement reconnection time monitoring
3. [ ] Test with different network interface types
4. [ ] Add metrics collection for network state transitions
5. [ ] Add VPN-based inverter connection scenarios to ROB-013

Each test execution must include:
- **Test Metadata**: Execution date, duration, Blixt firmware version, test environment details
- **Detailed Results**: Test outcomes with precise timestamps and measurements
- **Performance Data**: All collected metrics with graphical representations where applicable
- **Issue Documentation**: Any deviations from expected behavior with severity classification
- **Log Analysis**: Summary of significant log entries and error patterns
- **Recommendations**: Suggested improvements or follow-up testing requirements
- **Reproducibility**: Sufficient detail to reproduce any identified issues
- **Test Spec Improvement**: Improve the test spec in any way to make it more clear, give hints and tips for testing.

## Future Test Areas (TODO)

### Safety Testing (TODO)
- Fail-safe behavior verification
- Data integrity under fault conditions
- Hardware fault response testing
- Critical process failure handling

### Security Testing (TODO)  
- Network security validation
- Encrypted communication verification
- Firmware integrity testing
- Local data protection validation
- Access control testing

---

**Document Version**: 1.0  
**Product**: Blixt Gateway  
**Focus**: Robustness Testing  
**Last Updated**: [Current Date]  
**Next Review**: After each major firmware release