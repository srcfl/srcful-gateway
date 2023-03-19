"""
Modbus/TCP server with virtual data
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Map the system date and time to @ 0 to 5 on the "holding registers" space.
Only the reading of these registers in this address space is authorized. All
other requests return an illegal data address except.

Run this as root to listen on TCP priviliged ports (<= 1024).

requires: pyModbusTCP

"""

import argparse
from pyModbusTCP.server import ModbusServer, DataBank


class MyDataBank(DataBank):
    """A custom ModbusServerDataBank for override get_holding_registers method."""

    def __init__(self):
        # turn off allocation of memory for standard modbus object types
        # only "holding registers" space will be replaced by dynamic build values.
        super().__init__(virtual_mode=True)

    def get_holding_registers(self, address, number=1, srv_info=None):
        """Get virtual holding registers."""
        # populate virtual registers dict with current datetime values
        v_regs_d = {40069: 118,
                    40070: 52,
                    40071: 53,
                    40072: 93,
                    40073: 86,
                    40074: 238,
                    40075: 214,
                    40076: 97,
                    40077: 171,
                    40078: 62,
                    40079: 174,
                    40080: 64,
                    40081: 236,
                    40082: 47,
                    40083: 97,
                    40084: 2,
                    40085: 110,
                    40086: 238,
                    40087: 21,
                    40088: 52,
                    40089: 7,
                    40090: 8,
                    40091: 99,
                    40092: 33,
                    40093: 164,
                    40095: 104,
                    40096: 242,
                    40097: 17,
                    40098: 75,
                    40099: 164,
                    40100: 164,
                    40101: 96,
                    40103: 4,
                    40106: 223,
                    40107: 161,
                    40108: 51,
                    40121: 185,
                    40122: 54,
                    40123: 87,
                    40124: 131,
                    40125: 175,
                    40126: 117,
                    40127: 47,
                    40129: 164,
                    40130: 144,
                    40131: 104,
                    40132: 55,
                    40140: 50,
                    40141: 34,
                    40142: 184,
                    40143: 21,
                    40145: 98,
                    40147: 55,
                    40148: 218,
                    40149: 89,
                    40151: 69,
                    40152: 85,
                    40160: 246,
                    40161: 14,
                    40162: 195,
                    40163: 175,
                    40165: 135,
                    40167: 111,
                    40168: 240,
                    40169: 42,
                    40171: 45,
                    40172: 28,
                    40180: 224,
                    40181: 2,
                    40182: 109,
                    40183: 225,
                    40185: 192,
                    40187: 28,
                    40188: 231,
                    40189: 158}
        # build a list of virtual regs to return to server data handler
        # return None if any of virtual registers is missing
        try:
            return [v_regs_d[a] for a in range(address, address + number)]
        except KeyError:
            return


if __name__ == '__main__':
    print("Modbus/TCP server with virtual data")
    # parse args
    parser = argparse.ArgumentParser()
    parser.add_argument('-H', '--host', type=str, default='0.0.0.0', help='Host (default: localhost)')
    parser.add_argument('-p', '--port', type=int, default=502, help='TCP port (default: 502)')
    args = parser.parse_args()

    # init modbus server and start it
    server = ModbusServer(host=args.host, port=args.port, data_bank=MyDataBank())
    print("Start server on {}:{}".format(args.host, args.port))
    # parse args
    server.start()
