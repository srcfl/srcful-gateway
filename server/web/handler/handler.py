'''Base classes for handlers'''

from .requestData import RequestData


class Handler:
    '''Base class for handlers'''
    def schema_prot(self, method: str, description: str):
        '''Override to return the schema of the handler'''
        return {
            "type": method,
            "description": description,
            "required": {},
            "returns": {},
        }


class PostHandler(Handler):
    '''Base class for post handlers'''
    def schema(self):
        '''Override to return the schema of the handler'''
        return self.schema_prot("post", "post handler default documentation")

    def do_post(self, data: RequestData):
        '''Override to implement the handler'''
        raise NotImplementedError("doPost not implemented")


class GetHandler(Handler):
    '''Base class for get handlers'''

    def schema(self):
        '''Override to return the schema of the handler'''
        return self.schema_prot("get", "get handler default documentation")

    def do_get(self, data: RequestData):
        '''Override to implement the handler'''
        raise NotImplementedError("doGet not implemented")


class DeleteHandler(Handler):
    '''Base class for delete handlers'''

    def schema(self):
        '''Override to return the schema of the handler'''
        return self.schema_prot("delete", "delete handler default documentation")

    def do_delete(self, data: RequestData):
        '''Override to implement the handler'''
        raise NotImplementedError("doDelete not implemented")
