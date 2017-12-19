import time
from tnc.channel_manager.state import ChannelFile, ChannelState


class Channel(ChannelFile, ChannelState):
    """

    """

    def __init__(self, sender, receiver, deposit, open_block_number):
        ChannelState.__init__(self, sender)
        ChannelFile.__init__(self, sender, receiver)
        self.deposit = deposit
        self.open_block_number = open_block_number
        self.balance = 0
        self.is_closed = False
        self.last_signature = None
        self.settle_timeout = -1
        self.ctime = time.time()
        self.mtime = self.ctime
        self.confirmed = False
        self.nonce = 0

    def to_dict(self):
        return self.__dict__

    @classmethod
    def from_dict(cls, state: dict):
        ret = cls(None, None, None, None)
        assert (set(state) - set(ret.__dict__)) == set()
        for k, v in state.items():
            if k in ret.__dict__.keys():
                setattr(ret, k, v)
        return ret
