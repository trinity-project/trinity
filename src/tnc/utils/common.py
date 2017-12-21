class CommonItem(object):
    def __init(self):
        pass

    @classmethod
    def from_dict(cls, common_dict):
        ret = cls()
        for k, v in common_dict.items():
            setattr(ret, k, v)
        return ret