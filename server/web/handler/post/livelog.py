# this is the inverter live log post handler
import json
import server.inverters.registerValue as RegisterValue


from ..handler import PostHandler
from ..requestData import RequestData


import logging
logger = logging.getLogger(__name__)


class Handler(PostHandler):
    def schema(self):
        return {
            "status": "under development",
            "type": "post",
            "description": "creates a new live log object",
            "required": {
                "frequency": "how many samples per second",
                "size": "the size of the logging buffer, the buffer is circular so if the buffer is full the oldest data is overwritten",
                "registers": "a list of registers to log, each register is a dictionary with the following register: holding/input, keys: address, size, type, endianess",
            },
            "returns": {"object": "a unique identifier for the live log object"},
        }

    def json_schema(self):
        return json.dumps(self.schema())

    def do_post(self, request_data: RequestData):
        if len(request_data.bb.inverters.lst) > 0:
            return 400, json.dumps({"error": "inverter not initialized"})

        if (
            "frequency" in request_data.data
            and "size" in request_data.data
            and "registers" in request_data.data
        ):
            inverter = request_data.bb.inverters.lst[0]
            if inverter.isOpen():
                # create a new live log object
                register_values = []
                for register in request_data.data["registers"]:
                    try:
                        register_type = RegisterValue.RegisterType.from_str(
                            register["register"]
                        )
                        datatype = RegisterValue.Type.from_str(register["type"])
                        endianess = RegisterValue.Endianness.from_str(
                            register["endianess"]
                        )
                        register_values.append(
                            RegisterValue(
                                register["address"],
                                register["size"],
                                register_type,
                                datatype,
                                endianess,
                            )
                        )
                    except Exception as e:
                        return 400, json.dumps({"error": str(e)})
            else:
                return 400, json.dumps({"error": "inverter not open"})
        else:
            # return a bad request and append the json schema
            return 400, json.dumps({"status": "bad request", "schema": self.schema()})
