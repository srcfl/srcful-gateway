from ..handler import DeleteHandler
from ..requestData import RequestData
import json

class Handler(DeleteHandler):
    def schema(self) -> dict:
        return self.create_schema(
            "Delete a message by id",
            required = {"id": "int"},
            returns = {
                "deleted": "bool",
            },
        )