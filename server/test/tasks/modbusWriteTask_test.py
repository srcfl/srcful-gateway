from unittest.mock import Mock, call
from server.tasks.modbusWriteTask import ModbusWriteTask


# Test that write registers is called correctly
def test_write_registers_call():
    inverter = Mock()
    commands = [ModbusWriteTask.WriteCommand(10, [0, 1, 2])]
    task = ModbusWriteTask(0, {}, inverter, commands)

    task.execute(0)

    inverter.writeRegisters.assert_called_once_with(10, [0, 1, 2])

# Test that pause affects the next event time
def test_pause_command_changes_event_time():
    inverter = Mock()
    commands = [ModbusWriteTask.PauseCommand(1000),
                ModbusWriteTask.WriteCommand(20, [1, 2, 3])]
    task = ModbusWriteTask(0, {}, inverter, commands)

    next_task = task.execute(0)
    
    assert next_task.time == 1000
    assert inverter.writeRegisters.call_count == 0

    task.execute(1000)
    inverter.writeRegisters.assert_called_once_with(20, [1, 2, 3])

# Test that commands are processed in order
def test_commands_executed_in_order():
    inverter = Mock()
    commands = [ModbusWriteTask.WriteCommand(10, [0, 1, 2]),
                ModbusWriteTask.WriteCommand(20, [3, 4, 5])]
    task = ModbusWriteTask(0, {}, inverter, commands)

    task.execute(0)
    task.execute(0)

    inverter.writeRegisters.assert_has_calls([call(10, [0, 1, 2]), call(20, [3, 4, 5])])
