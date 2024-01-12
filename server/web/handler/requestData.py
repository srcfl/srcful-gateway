from server.blackboard import BlackBoard

class RequestData():
    def __init__(self, bb:BlackBoard, post_params:dict, query_params:dict, data:dict, tasks):
        self.bb = bb
        self.post_params = post_params  # parameters part of the endpoint x/y/{z}
        self.query_params = query_params # parameters part of the query string ?x=y&z=a
        self.tasks = tasks  # the task queue to add new tasks to
        self.data = data    # the data from the post request