from .requestData import RequestData

class PostHandler:
    def doPost(self, data: RequestData):
        raise NotImplementedError("doPost not implemented")
    
class GetHandler:
    def doGet(self, data: RequestData):
        raise NotImplementedError("doGet not implemented")