import pytest
import sys
from unittest.mock import MagicMock, patch
from server.inverters.ModbusTCP import ModbusTCP
from server.inverters.ModbusRTU import ModbusRTU 
from server.inverters.SolarmanTCP import SolarmanTCP
from server.inverters.supported_inverters.profiles import InverterProfiles
from pymodbus.exceptions import ModbusException, ModbusIOException, ConnectionException


profiles = InverterProfiles()
huawei = profiles.get('huawei')
lqt40s = profiles.get('lqt40s')


def get_inverters():
    """
    Returns a list of two inverters, one TCP and one RTU.
    """

    inv_tcp = ModbusTCP(("localhost", 8081, "HUAWEI" , 1))
    # We open to make the client attribute available, then
    # we mock the socket attribute to make the is_open() method return True.
    # This would normally be true if a real connection was established.
    inv_tcp.open(reconnect_delay=0, retries=0, timeout=0.1, reconnect_delay_max=0)
    inv_tcp.client.socket = MagicMock()

    if sys.platform != "win32":
        inv_rtu = ModbusRTU(("/dev/ttyUSB0", 9600, 8, "N", 1, "LQT40S", 1))
        inv_rtu.open(reconnect_delay=0, retries=0, timeout=0.1, reconnect_delay_max=0)
        inv_rtu.client.socket = MagicMock()

        return [inv_tcp, inv_rtu]
    else:
        return [inv_tcp]

def test_solarmanv5_inverter():
    inv_solarmanv5 = SolarmanTCP(("localhost", 123456789, 8899, "DEYE_HYRID", 1, False))
    
    
    # Expect that NoSocketAvailableError is raised 
    with pytest.raises(Exception):
        inv_solarmanv5.open(reconnect_delay=0, retries=0, timeout=0.1, reconnect_delay_max=0)

    inv_solarmanv5.client = MagicMock()

    inv_solarmanv5.client.sock = MagicMock()

    assert inv_solarmanv5.is_open() == True

    inv_solarmanv5.terminate()

    assert inv_solarmanv5.is_terminated() == True

    new_inverter = inv_solarmanv5.clone()

    assert new_inverter.get_host() == "localhost"

    assert new_inverter.get_port() == 8899




def test_sma_inverter():
    """
    Test that the SMA inverter is created correctly.
    """
    inv = ModbusTCP(("localhost", 8081, "SMA", 1))

    assert inv.get_type() == "SMA"
    assert inv.get_address() == 1

    registers = inv.profile.get_registers_verbose()

    assert len(registers) > 0

def test_inverters_are_open():
    """
    Test that the inverters are open after the open() method has been called.
    """
    inverters = get_inverters()

    for inv in inverters:
        assert inv.is_open()

def test_inverters_are_not_open():
    """
    Test that the inverters are not open after the terminate() method has been called.
    """
    inverters = get_inverters()

    for inv in inverters:
        
        assert not inv.is_terminated()
        assert inv.is_open()

        inv.terminate()

        assert inv.is_terminated()
        assert not inv.is_open()
        assert not inv.open()

def test_get_tcp_config():
    """
    Test that the get_config_dict() method returns the correct dictionary.
    """
    inv = ModbusTCP(("localhost", 8081, "HUAWEI", 1))

    assert inv.get_config_dict() == {
        "connection": "TCP",
        "type": "HUAWEI",
        "address": 1,
        "host": "localhost",
        "port": 8081,
    }

def test_get_rt_config():
    """
    Test that the get_config_dict() method returns the correct dictionary.
    """
    inv = ModbusRTU(("/dev/ttyUSB0", 9600, 8, "N", 1, "LQT40S", 1))

    assert inv.get_config_dict() == { 
        "connection": "RTU",
        "type": "LQT40S",
        "address": 1,
        "host": "/dev/ttyUSB0",
        "baudrate": 9600,
        "bytesize": 8,
        "parity": "N",
        "stopbits": 1
    }

def test_inverter_clone():
    inverters = get_inverters()

    for inv in inverters:
        print(inv.clone().setup)
        print(inv.setup)
        assert inv.setup == inv.clone().setup

def test_read_harvest_data():
    """
    Test that the read_harvest_data() method returns a dictionary with data.
    """

    inverters = get_inverters()

    for inv in inverters:

        def read_registers(operation, address, size):
            return [i for i in range(address, address + size)]

        inv.read_registers = read_registers

        result = inv.read_harvest_data()
        assert type(result) is dict
        assert len(result) > 0

def test_read_harvest_data_terminated_exception():
    """
    Test that an exception is raised when trying to read from a terminated inverter.
    """
    inverters = get_inverters()

    for inv in inverters:

        inv.terminate()

        with pytest.raises(Exception):
            inv.read_harvest_data()

def test_read_harvest_no_data_exception():
    """
    Test that an exception is raised when no data is read from the inverter.
    """

    inverters = get_inverters()

    for inv in inverters:
        
        inv.get_address = MagicMock(return_value=1)

        def read_registers(operation, address, size):
            return [i for i in range(address, address + size)]

        inv.client.read_registers = read_registers
        
        # Empty register array should raise an exception
        with pytest.raises(Exception):
            inv.read_harvest_data()

def test_modbus_connection_exception():
    """
    Test that an exception is raised when a connection exception occurs while reading from an inverter.
    """
    inverters = get_inverters()

    for inverter in inverters:
        # Patch the read_registers or the internal method that performs the actual communication
        with patch.object(inverter, '_read_registers') as mock_read_registers, \
             patch.object(inverter, 'get_address', return_value=1), \
             patch('server.inverters.inverter.log') as mock_log:

            # Set the side effect to raise a ConnectionException
            mock_read_registers.side_effect = ConnectionException("Connection error")

            # Determine the operation code based on inverter type
            operation_code = 0x04 if inverter.get_type() == "LQT40S" else 0x03

            # Call the method under test
            registers = inverter.read_registers(operation_code, 0, 12)
            
            # Assert the return value is as expected (likely an empty list or similar)
            assert registers == [], "Expected empty list on ConnectionException"

            # Verify that the correct log message was emitted
            # Adjust the assert to match the actual log message format and content
            expected_log_msg = "Modbus Error: [Connection] Connection error"
            mock_log.error.assert_called_with("ConnectionException occurred: %s", expected_log_msg)

def test_modbus_io_exception():
    """
    Test that an exception is raised when an IO exception occurs while reading from an inverter.
    """
    inverters = get_inverters()

    for inverter in inverters:
        # Patch the read_registers method which is called internally by read_registers
        with patch.object(inverter, '_read_registers') as mock_read_registers, \
             patch.object(inverter, 'get_address', return_value=1), \
             patch('server.inverters.inverter.log') as mock_log:

            # Set up the side effect for read_registers
            mock_read_registers.side_effect = ModbusIOException("Exception occurred while reading registers")

            # Determine the operation code based on inverter type
            operation_code = 0x04 if inverter.get_type() == "LQT40S" else 0x03

            # Call the method under test
            registers = inverter.read_registers(operation_code, 0, 12)
            
            # Assert the return value is as expected (likely an empty list or similar)
            assert registers == [], f"Expected empty list on ModbusIOException, got {registers} instead"

            # Verify that the correct log message was emitted
            expected_log_msg = "Modbus Error: [Input/Output] Exception occurred while reading registers"
            mock_log.error.assert_called_with("ModbusIOException occurred: %s", expected_log_msg)