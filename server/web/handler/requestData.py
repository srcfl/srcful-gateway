from server.blackboard import BlackBoard


class RequestData:

    bb: BlackBoard

    '''This class is used to pass data from the request and the system to the handlers'''
    def __init__(self, bb: BlackBoard, post_params: dict, query_params: dict, data: dict):
        self.bb = bb    # system blackboard
        self.post_params = post_params  # parameters part of the endpoint x/y/{z}
        self.query_params = query_params  # parameters part of the query string ?x=y&z=a
        self.data = data  # the data from the post request eg the json body
