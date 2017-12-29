
class State(object):

    def __init__(self):
        pass

    @classmethod
    def success(cls):
        return (0, "SUCCESS")

    @classmethod
    def raise_fail(cls,err_no: int, err_reason: str):
        return (err_no, err_reason)