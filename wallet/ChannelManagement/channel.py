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
import hashlib
import time
from enum import IntEnum
from exception.exceptions import ChannelExist
from sserver.model.address_model import APIWalletAddress
from sserver.model.channel_model import APIChannel
from sserver.model.base_enum import EnumChainType,EnumChannelState
from wallet.TransactionManagement import message as mg
from wallet.TransactionManagement import transaction as trans
from wallet.utils import pubkey_to_address
from wallet.Interface.gate_way import sync_channel

def get_gateway_ip():
    return "127.0.0.1:20554"

def query_ip(address):
    return "127.0.0.1:20554"


GateWayUrl = get_gateway_ip()


class Channel(object):
    """

    """
    def __init__(self,founder, partner):
        self.founder = founder
        self.partner = partner
        self.founder_pubkey = self.founder.split("@")[0]
        print(self.founder_pubkey)
        self.founder_address = pubkey_to_address(self.founder_pubkey)
        self.partner_pubkey = self.partner.split("@")[0]
        self.partner_address = pubkey_to_address(self.partner_pubkey)


    @staticmethod
    def get_channel(address1, address2):

        try:
            print(address1, address2)
            channel = APIChannel.batch_query_channel(filters={"src_addr": address1, "dest_addr": address2})
            print("debug1 ",channel)
            return channel["content"][0].channel
        except:
            try:
                channel= APIChannel.batch_query_channel(filters={"src_addr":address2, "dest_addr":address1})
                print("debug2 ", channel)
                return channel["content"][0].channel
            except:
                return None

    @classmethod
    def channel(cls,channelname):
        try:
            channel = APIChannel.query_channel(channel=channelname)
            channel_info = channel["content"][0]
        except Exception as e:
            return None
        ch =cls(channel_info.src_addr, channel_info.dest_addr)
        ch.channel_name = channelname
        return ch


    def _init_channle_name(self):
        md5s = hashlib.md5(self.founder.encode())
        md5s.update(self.partner.encode())
        md5s.update(str(time.time()).encode())
        return md5s.hexdigest().upper()

    def create(self, asset_type, deposit, cli=True):
        #if Channel.get_channel(self.founder_pubkey, self.partner_pubkey):
            #raise ChannelExist
        self.start_time = time.time()
        self.asset_type = asset_type
        self.deposit = {}
        self.deposit[self.founder_pubkey] = {}.setdefault(asset_type, deposit)
        self.deposit[self.partner_pubkey] = {}.setdefault(asset_type, deposit)
        self.channel_name = self._init_channle_name()
        print(self.channel_name)

        result = APIChannel.add_channel(self.channel_name,self.founder_pubkey, self.partner_pubkey,
                     EnumChannelState.INIT.name, 0, self.deposit, 0)
        if cli:
            message={"MessageType":"RegisterChannel",
                 "Sender": self.founder,
                 "Receiver": self.partner,
                 "ChannelName": self.channel_name,
                 "MessageBody":{
                                "AssetType":asset_type,
                                "Deposit":deposit
                                }
            }
            return mg.Message.send(message)

        return result

    def delete(self):
        pass

    def update_channel(self, **kwargs):
        return APIChannel.update_channel(self.channel_name, **kwargs)

    @property
    def state(self):
        return None

    @property
    def src_addr(self):
        ch = self._get_channel()
        if ch:
            return ch.src_addr
        else:
            return None

    @property
    def dest_addr(self):
        ch = self._get_channel()
        if ch:
            return ch.dest_addr
        else:
            return None

    def _get_channel(self):
        try:
            channel = APIChannel.query_channel(self.channel_name)
            print(channel)
            return channel["content"][0]
        except Exception as e:
            print(e)
            return None

    def get_balance(self):
        ch = self._get_channel()
        if ch:
            return ch.balance
        else:
            return None

    def get_deposit(self):
        ch = self._get_channel()
        if ch:
            return ch.deposit
        else:
            return None

    def toJson(self):
        jsn = {"ChannelName":self.channel_name,
               "Founder":self.founder,
               "Parterner":self.partner,
               "State":self.state,
               "Deposit":self.get_deposit(),
               "Balance":self.get_balance()}
        return jsn


def create_channel(founder, partner, asset_type, depoist:int, cli=True):
    return Channel(founder, partner).create(asset_type, depoist, cli)


def get_channel_name_via_address(address1, address2):
    channel = Channel.get_channel(address1, address2)
    return channel


def close_channel(channel_name, wallet):
    tx = trans.TrinityTransaction(channel_name, wallet)


def sync_channel_info_to_gateway(channel_name, type):
    ch = Channel.channel(channel_name)
    return sync_channel(type, ch.channel_name,ch.founder,ch.partner,ch.get_balance())


if __name__ == "__main__":
    result = APIChannel.query_channel(channel="1BE0FCD56A27AD46C22B8EEDC4E835EA")
    print(result)
    print(dir(result["content"][0]))
    print(result["content"][0].dest_addr)
    print(result["content"][0].src_addr)

    result = APIChannel.batch_query_channel(filters={"dest_addr": "022a38720c1e4537332cd6e89548eedb0afbb93c1fdbade42c1299601eaec897f4",
                                            "src_addr":"02cebf1fbde4786f031d6aa0eaca2f5acd9627f54ff1c0510a18839946397d3633"})
    print(result)