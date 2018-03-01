"""Author: Trinity Core Team

MIT License

Copyright (c) 2018 Trinity

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE."""

import time
from channel_manager import blockchain
from channel_manager.state import ChannelFile, ChannelState, query_channel_from_address, ChannelAddress, Message
from enum import IntEnum
from configure import Configure
from utils.channel import generate_channel_name
from logzero import logger
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
    INITIAL=0
    OPENING = 1
    OPEN = 2
    SETTLING = 3
    SETTLED = 4
    CLOSED = 5
    UPDATING = 6

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
        channel_name = ChannelState.query_channel_name(self.sender, self.receiver)
        return channel_name if channel_name else generate_channel_name(self.sender, self.receiver)

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

    def create(self, sender_deposit,open_block_number, settle_timeout, receiver_deposit=0):
        if not self.qeury_channel():
            sender_publickey = ChannelAddress.get_publickey(self.sender)
            receiver_publickey = ChannelAddress.get_publickey(self.receiver)
            if not sender_publickey or not receiver_publickey:
                return None
            contract = blockchain.create_contract_address(sender_publickey, receiver_publickey,
                                                          Configure["EyewitnessPublicKey"])
            contract_address = contract.get("contractForPublicKey1").get("address")
            contract_hash = contract.get("contractForPublicKey1").get("script")
            self.add_channel_to_database(sender= self.sender, receiver= self.receiver, channel_name=self.channel_name,
                                             state=State.INITIAL, sender_deposit=0,receiver_deposit=0,
                                             open_block_number = open_block_number, sender_deposit_cache=sender_deposit,
                                             receiver_deposit_cache=receiver_deposit,settle_timeout=settle_timeout,
                                         contract_address=contract_address, contract_hash=contract_hash)
            self.initialize_channel_file()
            return self.channel_name
        else:
            raise ChannelExistInDb

    @check_channel_exist
    def delete(self):
        if self.stateinDB != State.CLOSED.value:
            raise ChannleNotInCloseState
        else:
            self.delete_channel_in_database()
            self.delete_channel()

    def close(self):
        try:
            self.delete_channel()
            self.delete_channel_in_database()
        except:
            return False
        return True

    @property
    def sender_balance(self):
        return self.get_address_balance(self.sender)

    @property
    def receiver_balance(self):
        return self.get_address_balance(self.receiver)

    def settle_balance_onchain(self):
        raw_data, tx_id,state= blockchain.distribute_deposit_tx(asset_type="TNC", addressFrom=self.contract_address,
                                                               addressTo1=self.sender,value1=self.sender_balance,
                                                               addressTo2=self.receiver, value2=self.receiver_balance)
        if state:
            self.update_channel_to_database(tx_id=tx_id, state=State.SETTLING)
            Message.push_message(self.sender, "signature", raw_data, self.channel_name)
            Message.push_message(self.receiver, "signature", raw_data, self.channel_name)

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
            return float(trans[0]["deposit"])
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
        if not self.stateinDB == State.OPEN:
            raise ChannelNotInOpenState
        else:
            channels = self.read_channel()
            sender_deposit = self.get_address_deposit(self.sender, channels)
            transdetail[0]["deposit"] = float(self.sender_deposit)
            delta = float(self.sender_deposit) - float(sender_deposit)
            print(delta)
            sender_balance = self.get_address_balance(self.sender, channels) + delta
            print(self.sender, sender_balance)
            if count > sender_balance:
                raise NoBalanceEnough
            else:
                transdetail[0]["trans"] = -float(count)
                sender_balance -=float(count)
            transdetail[0]["balance"] = sender_balance

            receiver_deposit = self.get_address_deposit(self.receiver, channels)
            transdetail[1]["deposit"] = float(self.receiver_deposit)
            delta = float(self.receiver_deposit) - float(receiver_deposit)
            receiver_balance = self.get_address_balance(self.receiver, channels) + delta
            transdetail[1]["trans"] = float(count)
            receiver_balance += float(count)
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
        if not self.stateinDB == State.OPEN:
            raise ChannelNotInOpenState
        else:
            channels = self.read_channel()
            transdetail[0]["deposit"] = float(self.sender_deposit)
            sender_balance = self.get_address_balance(self.sender, channels)
            transdetail[0]["trans"] = float(count)
            sender_balance += float(count)
            transdetail[0]["balance"] = sender_balance

            transdetail[1]["deposit"] = float(self.receiver_deposit)
            receiver_balance = self.get_address_balance(self.receiver, channels)
            if count > sender_balance:
                raise NoBalanceEnough
            else:
                transdetail[1]["trans"] = -float(count)
                receiver_balance -=float(count)
            transdetail[1]["balance"] = receiver_balance

            tx_id = int(channels[-1]["tx_id"])
            tx = {"tx_id": str(tx_id + 1), "tx_detail": transdetail}
            self.update_channel(**tx)

        return "SUCCESS"

    @check_channel_exist
    def check_closed(self):
        return self.stateinDB == State.CLOSED

    def has_channel(self):
        return self.qeury_channel() and self.has_channel_file()

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
        transinfo = {"tx_id": "0", "tx_detail": transdetail}
        try:
            self.create_channelfile(**transinfo)
        except ChannelExist:
            pass
        return self.channel_name

    def set_channel_open(self):
        print("set_channel_open", self.channelname)
        if not self.has_channel():
            print("No channel find")
        else:
            tx_id = self.channel_txid
            sender_balance = self.get_address_balance(self.sender)
            receiver_balance = self.get_address_balance(self.receiver)
            print(self.sender_deposit_cache)
            print(self.sender_deposit)

            tx_detail = [
                {"address": self.sender,
                 "deposit": self.sender_deposit + self.sender_deposit_cache,
                 "trans": 0,
                 "balance": sender_balance + self.sender_deposit_cache,

                 },
                {"address": self.receiver,
                 "deposit": self.receiver_deposit + self.receiver_deposit_cache,
                 "trans": 0,
                 "balance": receiver_balance + self.receiver_deposit_cache,
                 }
            ]
            trans_info = {"tx_id": str(int(tx_id)+ 1), "tx_detail": tx_detail}
            self.update_channel(**trans_info)
            self.update_channel_deposit(sender_deposit=self.sender_deposit + self.sender_deposit_cache,
                                        receiver_deposit=self.receiver_deposit + self.receiver_deposit_cache)
            self.update_channel_state(State.OPEN)
            self.update_deposit_cache(sender_deposit_cache=0, receiver_deposit_cache=0)

            return "SUCCESS"


def get_channelnames_via_address(address):
    return query_channel_from_address(address)






