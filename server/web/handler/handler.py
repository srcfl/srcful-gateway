'''Base classes for handlers'''

from .requestData import RequestData


class Handler:
    '''Base class for handlers'''
    def schema_prot(self, method: str, description: str, required: dict = None, optional: dict = None, returns: dict = None) -> dict:
        '''Override to return the schema of the handler'''
        return {
            "type": method,
            "description": description,
            "required": required if required is not None else {},
            "optional": optional if optional is not None else {},
            "returns": returns if returns is not None else {}
        }


class PostHandler(Handler):
    '''Base class for post handlers'''
    def schema(self) -> dict:
        '''Override to return the schema of the handler'''
        return self.create_schema("post handler default documentation")

    def create_schema(self, description: str, required: dict = None, optional: dict = None, returns: dict = None) -> dict:
        '''Use to create the schema of the handler'''
        return super().schema_prot("post", description, required, optional, returns)

    def do_post(self, data: RequestData):
        '''Override to implement the handler'''
        raise NotImplementedError("doPost not implemented")


class GetHandler(Handler):
    '''Base class for get handlers'''

    def schema(self) -> dict:
        '''Override to return the schema of the handler'''
        return self.create_schema("get handler default documentation")

    def create_schema(self, description: str, required: dict = None, optional: dict = None, returns: dict = None) -> dict:
        '''Use to create the schema of the handler'''
        return super().schema_prot("get", description, required, optional, returns)

    def do_get(self, data: RequestData):
        '''Override to implement the handler'''
        raise NotImplementedError("doGet not implemented")


class DeleteHandler(Handler):
    '''Base class for delete handlers'''

    def schema(self) -> dict:
        '''Override to return the schema of the handler'''
        return self.create_schema("delete handler default documentation")

    def create_schema(self, description: str, required: dict = None, optional: dict = None, returns: dict = None):
        '''Use to create the schema of the handler'''
        return super().schema_prot("delete", description, required, optional, returns)

    def do_delete(self, data: RequestData):
        '''Override to implement the handler'''
        raise NotImplementedError("doDelete not implemented")
