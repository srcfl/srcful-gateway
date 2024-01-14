from .requestData import RequestData

class PostHandler:
    def schema(self):
        return { 'type': 'post',
                        'description': 'post handler default documentation',
                        'required': {},
                        'returns': {}
                      }
    
    def doPost(self, data: RequestData):
        raise NotImplementedError("doPost not implemented")
    
class GetHandler:
    def schema(self):
        return { 'type': 'get',
                        'description': 'get handler default documentation...',
                        'required': {},
                        'returns': {}
                      }

    def doGet(self, data: RequestData):
        raise NotImplementedError("doGet not implemented")
    
class DeleteHandler:
    def schema(self):
        return { 'type': 'delete',
                        'description': 'delete handler default documentation',
                        'required': {},
                        'returns': {}
                      }

    def doDelete(self, data: RequestData):
        raise NotImplementedError("doDelete not implemented")