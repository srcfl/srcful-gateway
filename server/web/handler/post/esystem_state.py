# a simple echo endpoint that returns the data it received

import json

from ..handler import PostHandler
from ..requestData import RequestData

from server.e_system.e_system import ESystemState


class Handler(PostHandler):
    def schema(self):
        return {
            "type": "post",
            "description": "sets the state of the esystem",
            "returns": {"status": "string, ok or error",
                        "message": "string, message"},
            "required": {"state": "string, the desired state of the esystem, self-consumption or stop"},
        }

    def do_post(self, data: RequestData):

        # check so we have an esystem and that it is configured
        if data.bb.esystem is None or len(data.bb.esystem.sn_list()) == 0:
            return 400, json.dumps({"status": "error", "message": "ESystem not configured"})
        
        if data.data["state"] == ESystemState.SELF_CONSUMPTION.value:

            
            if data.bb.esystem.state == ESystemState.STOP:
                data.bb.add_task(ESystemTask(data.bb.time_ms() + 100, data.bb, data.bb.esystem))

            data.bb.esystem.set_state(ESystemState.SELF_CONSUMPTION)


            return 200, json.dumps({"status": "ok", "message": "Self-consumption mode set"})
        elif data.data["state"] == ESystemState.STOP.value:
            data.bb.esystem.set_state(ESystemState.STOP)
            return 200, json.dumps({"status": "ok", "message": "Stop mode set"})
        else:
            return 400, json.dumps({"status": "error", "message": "Invalid state"})

