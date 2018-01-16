import time
from channel_manager.state import ChannelFile, ChannelState
from enum import IntEnum
from exception import (
    ChannelFileNoExist,
    ChannelExistInDb,
    ChannleNotInCloseState,
    ChannelNotExistInDb,
    ChannelClosed,
    ChannelSettling,
    ChannelNotInOpenState,
    NoBalanceEnough
)

class State(IntEnum):
    OPENING = 1
    OPEN = 2
    SETTLING = 3
    CLOSED = 4

def check_channel_exist(func):
        def wrapper(self, *args, **kwargs):
            if not self.has_channel():
                raise ChannelNotExistInDb
            else:
                return func(self,*args, **kwargs)
        return wrapper


class Channel(ChannelFile, ChannelState):
    """

    """
    def __init__(self, sender, receiver, deposit, open_block_number):
        ChannelState.__init__(self, sender)
        ChannelFile.__init__(self, sender, receiver)
        self.deposit = deposit
        self.open_block_number = open_block_number
        self.balance = deposit
        self.is_closed = False
        self.last_signature = None
        self.settle_timeout = -1
        self.ctime = time.time()
        self.mtime = self.ctime
        self.confirmed = False
        self.nonce = 0

    @property
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

    def create(self):
        if not self.find_sender():
            self.create_channel(**self.to_dict)
            if self.check_channelfile():
                self.add_channle_to_database(receiver=self.receiver, channel_name=self.channel_name,state=State.OPEN,
                                         deposit=self.deposit,open_block_number=self.open_block_number)
            else:
                raise ChannelFileNoExist
        else:
            raise ChannelExistInDb
        return self.channel_name

    @check_channel_exist
    def delete(self):
        if self.state_in_database != State.CLOSED:
            raise ChannleNotInCloseState
        else:
            self.delete_channel()
            self.delete_channle_in_database()

    @check_channel_exist
    def close(self):
        channel_info = Channel.from_dict(self.read_channel()[-1])
        if self.state_in_database == State.SETTLING:
            raise ChannelSettling
        else:
            channel_info.is_closed = True
            self.update_channel(**channel_info.to_dict)
            self.update_channel_to_database(receiver=self.receiver, channel_name=self.channel_name,state=State.CLOSED,
                                         deposit=self.deposit,open_block_number=self.open_block_number)

    @check_channel_exist
    def sender_to_receiver(self, count):
        if not self.state_in_database == State.OPEN:
            raise ChannelNotInOpenState
        else:
            channels  = self.read_channel()
            channel = Channel.from_dict(channels[-1])
            if count > channel.balance:
                raise NoBalanceEnough
            else:
                channel.balance -= count
                channel.mtime = time.time()
                self.update_channel(**channel.to_dict)
        return True

    def get_asset_proof(self):
        channels = self.read_channel()
        channel_info = Channel.from_dict(channels[-1])
        if channel_info:
            return {"sender": self.sender,
        "receiver": self.receiver,
        "deposit" : self.deposit,
        "open_block_number" : self.open_block_number,
        "transcount": self.deposit -  channel_info.balance,
        "nonce": channel_info.nonce
                    }


    @check_channel_exist
    def check_closed(self):
        return self.state_in_database == State.CLOSED

    def has_channel(self):
        return self.find_sender()






