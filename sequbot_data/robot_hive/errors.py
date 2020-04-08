

class HiveErrorInResponse(Exception):
    def __init__(self, message, request, response):
        self.request = request
        self.response= response
        super(HiveErrorInResponse, self).__init__(message)


class HiveConnectionError(Exception): pass
class HiveEmptyResponse(Exception): pass
