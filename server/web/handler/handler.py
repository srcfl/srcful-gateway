from .requestData import RequestData


class PostHandler:
    def schema(self):
        return {
            "type": "post",
            "description": "post handler default documentation",
            "required": {},
            "returns": {},
        }

    def do_post(self, data: RequestData):
        raise NotImplementedError("doPost not implemented")


class GetHandler:
    def schema(self):
        return {
            "type": "get",
            "description": "get handler default documentation...",
            "required": {},
            "returns": {},
        }

    def do_get(self, data: RequestData):
        raise NotImplementedError("doGet not implemented")


class DeleteHandler:
    def schema(self):
        return {
            "type": "delete",
            "description": "delete handler default documentation",
            "required": {},
            "returns": {},
        }

    def do_delete(self, data: RequestData):
        raise NotImplementedError("doDelete not implemented")
