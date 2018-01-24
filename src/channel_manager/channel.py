import time
from channel_manager.state import ChannelFile, ChannelState, query_channel_from_address
from enum import IntEnum
from exception import (
    ChannelFileNoExist,
    ChannelExistInDb,
    ChannleNotInCloseState,
    ChannelNotExistInDb,
    ChannelClosed,
    ChannelSettling,
    ChannelNotInOpenState,
    NoBalanceEnough,
    TransCanNotBelessThanZ,
    ChannelExist
)

class State(IntEnum):
    OPENING = 1
    OPEN = 2
    SETTLING = 3
    SETTLED = 4
    CLOSED = 5

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
    def __init__(self, sender, receiver):
        self.sender = sender
        self.receiver = receiver
        ChannelState.__init__(self, self.channel_name)

    @property
    def channel_name(self):
        channel_name = "".join(map(lambda x, y: x+y, self.sender, self.receiver))
        peer_channel_name= "".join(map(lambda x, y: x+y, self.receiver, self.sender))
        if ChannelState(peer_channel_name).find_channel():
            return peer_channel_name
        else:
            return channel_name

    @property
    def to_dict(self):
        return self.__dict__

    @classmethod
    def from_dict(cls, state: dict):
        ret = cls(None, None)
        assert (set(state) - set(ret.__dict__)) == set()
        for k, v in state.items():
            if k in ret.__dict__.keys():
                setattr(ret, k, v)
        return ret

    def create(self, sender_deposit,open_block_number, settle_timeout, reciever_deposit=0):
        if not self.find_channel():
            self.add_channle_to_database(sender= self.sender, receiver= self.receiver, channel_name=self.channel_name,
                                             state=State.OPENING, sender_deposit=0,receiver_deposit=0,
                                             open_block_number = open_block_number, sender_deposit_cache=sender_deposit,
                                             receiver_deposit_cache=reciever_deposit,settle_timeout=settle_timeout)
            self.initialize_channel_file()
            return self.channel_name
        else:
            raise ChannelExistInDb

    @check_channel_exist
    def delete(self):
        if self.state_in_database != State.CLOSED:
            raise ChannleNotInCloseState
        else:
            self.delete_channle_in_database()
            self.delete_channel()


    def close(self):
        if self.state_in_database == State.SETTLING:
            raise ChannelSettling
        else:
            self.find_channel()
            self.delete_channel()
            self.delete_channle_in_database()

    @check_channel_exist
    def settle(self):
        if self.state_in_database != State.OPEN:
            raise ChannelNotInOpenState
        else:
            self.find_channel()
            self.update_channel_to_database(sender=self.match.sender, receiver=self.match.receiver,
                                            channel_name=self.match.channel_name,
                                            state=State.SETTLING, sender_deposit=self.match.sender_deposit,
                                            receiver_deposit=self.match.reciever_deposit,
                                            open_block_number=self.match.open_block_number,
                                            settle_timeout=self.match.settle_timeout,
                                            start_block_number=self.match.start_block_number)
            if self.settle_banlace_in_lockchain():
                self.update_channel_to_database(sender=self.match.sender, receiver=self.match.receiver,
                                                channel_name=self.match.channel_name,
                                                state=State.SETTLED, sender_deposit=self.match.sender_deposit,
                                                receiver_deposit=self.match.reciever_deposit,
                                                open_block_number=self.match.open_block_number,
                                                settle_timeout=self.match.settle_timeout,
                                                start_block_number=self.match.start_block_number)


    def settle_banlace_in_lockchain(self):
        return True

    def get_address_balance(self, address, channels = None):
        try:
            if not channels:
                channels = self.read_channel()
            trans_detail = channels[-1]["tx_detail"]
            trans = [i for i in trans_detail if i["address"]==address]
            if trans:
                return int(trans[0]["balance"])
            else:
                return None
        except:
            return None



    def get_address_deposit(self, address, channels = None):
        if not channels:
            channels = self.read_channel()
        trans_detail = channels[-1]["tx_detail"]
        trans = [i for i in trans_detail if i["address"] == address]
        if trans:
            return int(trans[0]["deposit"])
        else:
            return None

    @property
    def channel_txid(self):
        channels = self.read_channel()
        return channels[-1]["tx_id"]

    @property
    def channel_transdetail(self):
        channels = self.read_channel()
        return channels[-1]["tx_detail"]

    @check_channel_exist
    def sender_to_receiver(self, count):
        transdetail = [
            {"address": self.sender,
             "deposit": 0,
             "trans": 0,
             "balance": 0,

             },
            {"address": self.receiver,
             "deposit": 0,
             "trans": 0,
             "balance": 0,
             }
        ]
        if count <= 0:
            raise TransCanNotBelessThanZ
        if not self.state_in_database == State.OPEN:
            raise ChannelNotInOpenState
        else:
            channels = self.read_channel()
            sender_deposit = self.get_address_deposit(self.sender, channels)
            transdetail[0]["deposit"] = int(self.sender_deposit)
            delta = int(self.sender_deposit) - int(sender_deposit)
            sender_balance = self.get_address_balance(self.sender, channels) + delta
            if count > sender_balance:
                raise NoBalanceEnough
            else:
                transdetail[0]["trans"] = -int(count)
                sender_balance -=int(count)
            transdetail[0]["balance"] = sender_balance

            receiver_deposit = self.get_address_deposit(self.receiver, channels)
            transdetail[1]["deposit"] = int(self.receiver_deposit)
            delta = int(self.receiver_deposit) - int(receiver_deposit)
            receiver_balance = self.get_address_balance(self.receiver, channels) + delta
            transdetail[1]["trans"] = int(count)
            receiver_balance += int(count)
            transdetail[1]["balance"] = receiver_balance

            tx_id = int(channels[-1]["tx_id"])
            tx = {"tx_id":str(tx_id+1), "tx_detail":transdetail}
            self.update_channel(**tx)

        return "SUCCESS"

    @check_channel_exist
    def receiver_to_sender(self, count):
        transdetail = [
            {"address": self.sender,
             "deposit": 0,
             "trans": 0,
             "balance": 0,

             },
            {"address": self.receiver,
             "deposit": 0,
             "trans": 0,
             "balance": 0,
             }
        ]
        if count <= 0:
            raise TransCanNotBelessThanZ
        if not self.state_in_database == State.OPEN:
            raise ChannelNotInOpenState
        else:
            channels = self.read_channel()
            transdetail[0]["deposit"] = int(self.sender_deposit)
            sender_balance = self.get_address_balance(self.sender, channels)
            transdetail[0]["trans"] = int(count)
            sender_balance += int(count)
            transdetail[0]["balance"] = sender_balance

            transdetail[1]["deposit"] = int(self.receiver_deposit)
            receiver_balance = self.get_address_balance(self.receiver, channels)
            if count > sender_balance:
                raise NoBalanceEnough
            else:
                transdetail[1]["trans"] = -int(count)
                receiver_balance -=int(count)
            transdetail[1]["balance"] = receiver_balance

            tx_id = int(channels[-1]["tx_id"])
            tx = {"tx_id": str(tx_id + 1), "tx_detail": transdetail}
            self.update_channel(**tx)

        return "SUCCESS"

    @check_channel_exist
    def check_closed(self):
        return self.state_in_database == State.CLOSED

    def has_channel(self):
        return self.find_channel() and self.has_channel_file()

    def initialize_channel_file(self):
        transdetail = [
            {"address": self.sender,
             "deposit": 0,
             "trans": 0,
             "balance": 0,

             },
            {"address": self.receiver,
             "deposit": 0,
             "trans": 0,
             "balance": 0,
             }
        ]
        transinfo = {"tx_id": 0, "tx_detail": transdetail}
        try:
            self.create_channelfile(**transinfo)
        except ChannelExist:
            pass
        return self.channel_name

    def set_channel_open(self):
        if not self.has_channel():
            return "No channel find"
        else:
            tx_id = self.channel_txid
            sender_balance = self.get_address_balance(self.sender)
            receiver_balance = self.get_address_balance(self.receiver)
            tx_detail = [
                {"address": self.sender,
                 "deposit": self.sender_deposit,
                 "trans": 0,
                 "balance": sender_balance + self.sender_deposit_cache,

                 },
                {"address": self.receiver,
                 "deposit": self.receiver_deposit,
                 "trans": 0,
                 "balance": receiver_balance + self.receiver_deposit_cache,
                 }
            ]
            trans_info = {"tx_id": int(tx_id)+ 1, "tx_detail": tx_detail}
            self.update_channel(**trans_info)
        self.update_channel_state(State.OPEN)
        self.update_deposit_cache(sender_deposit_cache=0, receiver_deposit_cache=0)
        return "SUCCESS"


def get_channelnames_via_address(address):
    return query_channel_from_address(address)






