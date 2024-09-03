import json
from ..handler import GetHandler

from ..requestData import RequestData

from server.inverters.registerValue import RegisterValue

# Example query: inverter/modbus/holding/40069?size=2&type=float&endianess=big


class RegisterHandler(GetHandler):
    def schema(self):
        return {
            "type": "get",
            "description": "Get data from a modbus registger",
            "required": {
                "{address}": "int, address of the register to read url parameter",
            },
            "optional": {
                "size": "int, size of the register to read (default 1)",
                "type": "string, data type of the register to read (default none)",
                "endianess": "string, endianess of the register to read little or big, (default little)",
            },
            "returns": {
                "register": "int, address of the register read",
                "size": "int, size of the register read",
                "raw_value": "string, hex representation of the raw value read",
                "value": "string, value read from the register, if applicable",
            },
        }

    def do_get(self, request_data: RequestData):
        if "address" not in request_data.post_params:
            return 400, json.dumps({"error": "missing address"})
        if len(request_data.bb.devices.lst) == 0:
            return 400, json.dumps({"error": "inverter not initialized"})

        raw = bytearray()
        address = int(request_data.post_params["address"])
        size = int(request_data.query_params.get("size", 1))

        try:
            datatype = RegisterValue.Type.from_str(
                request_data.query_params.get("type", "none")
            )
            endianness = RegisterValue.Endianness.from_str(
                request_data.query_params.get("endianess", "little")
            )
            raw, value = RegisterValue(
                address, size, self.get_register_type(), datatype, endianness
            ).read_value(request_data.bb.devices.lst[0])

            ret = {
                "register": address,
                "size": size,
                "raw_value": raw.hex(),
            }
            if value is not None:
                ret["value"] = value

            return 200, json.dumps(ret)
        except Exception as e:
            return 400, json.dumps({"error": str(e)})

    def get_register_type(self):
        raise NotImplementedError()


class HoldingHandler(RegisterHandler):
    def get_register_type(self):
        return RegisterValue.RegisterType.HOLDING


class InputHandler(RegisterHandler):
    def get_register_type(self):
        return RegisterValue.RegisterType.INPUT
