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
from wallet.utils import pubkey_to_address

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
        self.founder_address = pubkey_to_address(self.founder_pubkey)
        self.partner_pubkey = self.partner.split("@")[0]
        self.partner_address = pubkey_to_address(self.partner_pubkey)

    @staticmethod
    def get_channel(address1, address2):
        #channel = APIChannel.batch_query_channel(filters={"src_addr":address1, "dest_adr":address2}, )
        channel = None
        if channel:
            return channel
        else:
            #return APIChannel.batch_query_channel(filters={"src_addr":address2, "dest_adr":address1})
            return None

    @classmethod
    def channel(cls,channelname):
        channel = APIChannel.query_channel(channel=channelname)
        return cls(channel.src_addr, channel.dest_addr)



    def _init_channle_name(self):
        md5s = hashlib.md5(self.founder.encode())
        md5s.update(self.partner.encode())
        md5s.update(str(time.time()).encode())
        return md5s.hexdigest().upper()

    def create(self, asset_type, deposit, cli=True):
        if Channel.get_channel(self.founder, self.partner):
            raise ChannelExist
        self.start_time = time.time()
        self.asset_type = asset_type
        self.deposit = {"source":{}.setdefault(asset_type, deposit), 'destination': {}.setdefault(asset_type, deposit)}
        self.channel_name = self._init_channle_name()
        print(self.channel_name)

        result = APIChannel.add_channel(self.channel_name,self.founder_address, self.partner_address,
                     EnumChannelState.INIT.name, 0, self.deposit, balance=self.deposit)
        print(result)
        if cli:
            message={"MessageType":"RegisterChannel",
                 "Sender": self.founder,
                 "Receiver": self.partner,
                 "MessageBody":{"ChannelName":self.channel_name,
                                "Depoist":self.deposit,
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

    def get_balance(self):
        channel = APIChannel.query_channel(self.channel_name)
        balance = channel.balance
        return balance


def create_channel(founder, partner, asset_type, depoist:int, cli=True):
    return Channel(founder, partner).create(asset_type, depoist, cli)


def get_channel_name_via_address(address1, address2):
    channel = Channel.get_channel(address1, address2)
    return channel.channel_name


if __name__ == "__main__":
    md5s = hashlib.md5("AM3wPXYSPDuDxXfbPdrDeioDhiNU5oeAP8".encode())
    md5s.update("Aetwx1BNtXD78f25v47kLTrBaXQr1moZEs".encode())
    print(md5s.hexdigest().upper())