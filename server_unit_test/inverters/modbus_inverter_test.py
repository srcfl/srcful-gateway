import pytest
import sys
from unittest.mock import MagicMock, patch
from server.inverters.InverterTCP import InverterTCP
from server.inverters.InverterRTU import InverterRTU 
from server.inverters.supported_inverters.profiles import InverterProfiles
from pymodbus.exceptions import ModbusException, ModbusIOException, ConnectionException

from server.inverters.enums import InverterKey

profiles = InverterProfiles()
huawei = profiles.get(InverterKey.HUAWEI.name)
lqt40s = profiles.get(InverterKey.LQT40S.name)


def get_inverters():
    """
    Returns a list of two inverters, one TCP and one RTU.
    """

    
    

    # We open to make the client attribute available, then
    # we mock the socket attribute to make the is_open() method return True.
    # This would normally be true if a real connection was established.
    inv_tcp = InverterTCP(("localhost", 8081, huawei.name, 1))
    inv_tcp.open(reconnect_delay=0, retries=0, timeout=0.1, reconnect_delay_max=0)
    inv_tcp.client.socket = MagicMock()

    if sys.platform != "win32":
        inv_rtu = InverterRTU(("/dev/ttyUSB0", 9600, 8, "N", 1, lqt40s.name, 1))
        inv_rtu.open(reconnect_delay=0, retries=0, timeout=0.1, reconnect_delay_max=0)
        inv_rtu.client.socket = MagicMock()

        return [inv_tcp, inv_rtu]
    else:
        return [inv_tcp]


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
    inv = InverterTCP(("localhost", 8081, huawei.name, 1))

    assert inv.get_config_dict() == {
        "connection": "TCP",
        "type": huawei.name,
        "address": 1,
        "host": "localhost",
        "port": 8081,
    }


def test_get_rt_config():
    """
    Test that the get_config_dict() method returns the correct dictionary.
    """
    inv = InverterRTU(("/dev/ttyUSB0", 9600, 8, "N", 1, lqt40s.name, 1))

    assert inv.get_config_dict() == { 
        "connection": "RTU",
        "type": lqt40s.name,
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
        assert inv.setup == inv.clone().setup


def test_read_harvest_data():
    """
    Test that the read_harvest_data() method returns a dictionary with data.
    """

    inverters = get_inverters()

    for inv in inverters:
        
        def read_registers(address, size, slave):
            class Ret:
                def __init__(self):
                    self.registers = [i for i in range(address, address + size)]

            return Ret()

        inv.client.read_holding_registers = read_registers
        inv.client.read_input_registers = read_registers

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

        def read_registers(address, size, slave):
            class Ret:
                def __init__(self):
                    self.registers = []

            return Ret()

        inv.client.read_holding_registers = read_registers
        inv.client.read_input_registers = read_registers
        
        # Empty register array should raise an exception
        with pytest.raises(Exception):
            inv.read_harvest_data()



def test_modbus_connection_exception():
    """
    Test that an exception is raised when a connection exception occurs while reading from an inverter.
    """
    inverters = get_inverters()

    for inverter in inverters:
        with patch.object(inverter, 'client') as mock_client, \
            patch.object(inverter, 'get_address', return_value=1), \
            patch('server.inverters.inverter.log') as mock_log:

            # We check the type since we want to test both read_holding_registers
            # and read_input_registers. Huawei inverters use holding registers and
            # lqt40s uses input registers.
            if inverter.get_type() == huawei.name:
                mock_client.read_holding_registers.side_effect = ConnectionException()
                registers = inverter.read_holding_registers(0, 12)
            elif inverter.get_type() == lqt40s.name:
                mock_client.read_input_registers.side_effect = ConnectionException()
                registers = inverter.read_input_registers(0, 12)
            
            # Assert the return value is as expected (likely an empty list or similar)
            assert registers == [], "Expected empty list on ConnectionException"

            # Verify that the correct log message was emitted
            mock_log.error.assert_called_with("ConnectionException occurred: %s", "Modbus Error: [Connection] ")


def test_modbus_io_exception():
    """
    Test that an exception is raised when an IO exception occurs while reading from an inverter.
    """
    inverters = get_inverters()

    for inverter in inverters:
        with patch.object(inverter, 'client') as mock_client, \
            patch.object(inverter, 'get_address', return_value=1), \
            patch('server.inverters.inverter.log') as mock_log:

            # We check the type since we want to test both read_holding_registers
            # and read_input_registers. Huawei inverters use holding registers and
            # lqt40s uses input registers.
            if inverter.get_type() == huawei.name:
                mock_client.read_holding_registers.side_effect = ModbusIOException()
                registers = inverter.read_holding_registers(0, 12)
            elif inverter.get_type() == lqt40s.name:
                mock_client.read_input_registers.side_effect = ModbusIOException()
                registers = inverter.read_input_registers(0, 12)
            
            # Assert the return value is as expected (likely an empty list or similar)
            assert registers == [], "Expected empty list on ModbusIOException"

            # Verify that the correct log message was emitted
            mock_log.error.assert_called_with("ModbusIOException occurred: %s", "Modbus Error: [Input/Output] ")