import json
import queue
from server.tasks.modbusWriteTask import ModbusWriteTask


import logging
logger = logging.getLogger(__name__)

from ..handler import PostHandler
from ..requestData import RequestData

class Handler(PostHandler):

    def schema(self):
        return { 
            'type': 'post',
            'description': 'Execute a set of modbus commands',
            'required': {
                'commands': {
                    'description': 'list of command objects, each containing:',
                    'type': '(string) - type of command to execute (write or pause)',
                    'startingAddress': '(int, required for write commands) - starting address of register',
                    'values': '(list of ints in decimal, binary, or hex, required for write commands) - values to write starting from the startingAddress',
                    'duration': '(int, required for pause commands) - duration in milliseconds to pause the operation.'
                }
            },
            'returns': {'status': 'string, ok or error',
                        'message': 'string, error message or success confirmation'
            }
        }
    
    def jsonSchema(self):
        return json.dumps(self.schema())

    def map_values(self, values):
        mapped_values = []
        for value in values:
            if value.startswith('0b'):  # Binary
                mapped_values.append(int(value, 2))
            elif value.startswith('0x'):  # Hexadecimal
                mapped_values.append(int(value, 16))
            else:  # Decimal
                mapped_values.append(int(value))
        return mapped_values

    def doPost(self, request_data:RequestData) -> tuple[int, str]:

        if 'commands' not in request_data.data:
            return 400, json.dumps({'status': 'bad request', 'message': 'Missing commands in request'})

        if len(request_data.bb.inverters.lst) > 0:
            return 400, json.dumps({'status': 'error', 'message': 'No Modbus device initialized'})
        
        try:
            commands = request_data.data['commands']
            
            # Map values in commands for Modbus device
            raw_commands = request_data.data['commands']
            command_objects = []

            # Check command type and construct appropriate command objects
            for raw_command in raw_commands:
                if raw_command['type'] == 'write':
                    startingAddress = int(raw_command['startingAddress'])
                    values = self.map_values(raw_command['values'])
                    command_objects.append(ModbusWriteTask.WriteCommand(startingAddress, values))
                elif raw_command['type'] == 'pause':
                    duration = float(raw_command['duration'])
                    command_objects.append(ModbusWriteTask.PauseCommand(duration))
                else:
                    logger.error('Unknown command type: %s', raw_command['type'])
                    logger.error(e)
                    return 500, json.dumps({'status': 'error', 'message': str(e)})
            
            # Add ModbusTask to task queue
            request_data.tasks.put(ModbusWriteTask(100, request_data.bb, request_data.bb.inverters.lst[0], command_objects))
            
            return 200, json.dumps({'status': 'ok'})
        except Exception as e:
            logger.error('Failed to handle Modbus commands: %s', request_data.data)
            logger.error(e)
            return 500, json.dumps({'status': 'error', 'message': str(e)})
