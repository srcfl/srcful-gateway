class RequestData():
    def __init__(self, stats, post_params, query_params, data, timeMSFunc, chipInfoFunc, tasks):
        self.stats = stats
        self.post_params = post_params  # parameters part of the endpoint x/y/{z}
        self.query_params = query_params # parameters part of the query string ?x=y&z=a
        self.timeMSFunc = timeMSFunc
        self.chipInfoFunc = chipInfoFunc
        self.tasks = tasks  # the task queue to add new tasks to
        self.data = data    # the data from the post request