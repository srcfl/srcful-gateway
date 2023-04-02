#!/usr/bin/env python3

"""
Modbus/TCP server with virtual data
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Map the system date and time to @ 0 to 5 on the "holding registers" space.
Only the reading of these registers in this address space is authorized. All
other requests return an illegal data address except.

Run this as root to listen on TCP priviliged ports (<= 1024).
"""

import argparse
from pyModbusTCP.server import ModbusServer, DataBank
import random

import inverter_types as inverters


class MyDataBank(DataBank):
  """A custom ModbusServerDataBank for override get_holding_registers method."""

  def __init__(self, inv_type):
    # turn off allocation of memory for standard modbus object types
    # only "holding registers" space will be replaced by dynamic build values.
    super().__init__(virtual_mode=True)
    self.inv_type = inv_type

  def get_holding_registers(self, address, number=1, srv_info=None):
    """Get virtual holding registers."""
    # populate virtual registers dict with current datetime values
    v_regs_d = {}

    entries = inverters.INVERTERS[self.inv_type]
    print("Holding:", entries)

    for entry in entries:
      operation = entry['operation']
      start = entry['scan_start']
      end = start + entry['scan_range']

      if operation == 0x03:
        for i in range(start, end):
          v_regs_d[i] = random.randint(0, 250)

    print(v_regs_d)

    # build a list of virtual regs to return to server data handler
    # return None if any of virtual registers is missing
    try:
      return [v_regs_d[a] for a in range(address, address + number)]
    except KeyError:
      return

  def get_input_registers(self, address, number=1, srv_info=None):
    """Get virtual input registers."""
    # populate virtual registers dict with current datetime values
    v_regs_d = {}

    entries = inverters.INVERTERS[self.inv_type]
    print("Input:", self.inv_type)

    for entry in entries:
      operation = entry['operation']
      start = entry['scan_start']
      end = start + entry['scan_range']

      if operation == 0x04:
        for i in range(start, end):
          v_regs_d[i] = random.randint(0, 250)

    print(v_regs_d)

    # build a list of virtual regs to return to server data handler
    # return None if any of virtual registers is missing
    try:
      return [v_regs_d[a] for a in range(address, address + number)]
    except KeyError:
      return


if __name__ == '__main__':
  # parse args
  parser = argparse.ArgumentParser()
  parser.add_argument('-H', '--host', type=str,
                      default='localhost', help='Host (default: localhost)')
  parser.add_argument('-p', '--port', type=int,
                      default=502, help='TCP port (default: 502)')
  parser.add_argument('-t', '--type', type=str, default="solaredge",
                      help='Inverter type (default: solaredge)')
  args = parser.parse_args()

  # init modbus server and start it
  server = ModbusServer(host=args.host, port=args.port,
                        data_bank=MyDataBank(args.type))
  server.start()
