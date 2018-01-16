
class APIError(Exception):
    def __init__(self, *value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class APIParamError(APIError):
    pass


class APIResultError(APIError):
    pass