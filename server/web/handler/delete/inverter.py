from ..handler import DeleteHandler
from ..requestData import RequestData
import json


class Handler(DeleteHandler):
    def schema(self) -> dict:
        return self.create_schema(
            "Delete and remove the inverter, currently this does not affect the bootstrapping process",
            returns={
                "isTerminated": "bool, True if the inverter is terminated",
                "isOpen": "bool, True if the inverter is open",
            },
        )

    def do_delete(self, data: RequestData):
        if len(data.bb.inverters.lst) > 0:
            inverter = data.bb.inverters.lst[0]
            inverter.terminate()
            data.bb.inverters.remove(inverter)

            data = {
                "isTerminated": inverter.isTerminated(),
                "isOpen": inverter.isOpen(),
            }

            return 200, json.dumps(data)

        return 400, json.dumps({"error": "no inverter initialized"})
