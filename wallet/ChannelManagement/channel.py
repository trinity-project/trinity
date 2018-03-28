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
from sserver.model.base_enum import EnumChainType
from wallet.TransactionManagement import message as mg

def get_gateway_ip():
    return "127.0.0.1:20554"

def query_ip(address):
    return "127.0.0.1:20554"


GateWayUrl = get_gateway_ip()



class State(IntEnum):
    INITIAL=0
    OPENING = 1
    OPEN = 2
    SETTLING = 3
    SETTLED = 4
    CLOSED = 5
    UPDATING = 6


class Channel(object):
    """

    """
    def __init__(self,founder, partner):
        self.founder = founder
        self.partner = partner
        #self.founder_pubkey = APIWalletAddress.query_wallet_address(self.founder).public_key
        #self.partner_pubkey = APIWalletAddress.query_wallet_address(self.partner).public_key
        self.founder_pubkey = "02cebf1fbde4786f031d6aa0eaca2f5acd9627f54ff1c0510a18839946397d3633"
        self.partner_pubkey = "02cebf1fbde4786f031d6aa0eaca2f5acd9627f54ff1c0510a18839946397d3633"

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

    def create(self, asset_type, deposit, wallet):
        if not wallet:
            raise Exception("Please Open The Wallet First")
        if Channel.get_channel(self.founder, self.partner):
            raise ChannelExist
        self.start_time = time.time()
        self.asset_type = asset_type
        self.depoist = {"asset_type":asset_type, "count":deposit}
        self.channel_name = self._init_channle_name()

        result = APIChannel.add_channel(self.channel_name,self.founder, self.partner,
                     str(State.INITIAL.value), 0, self.depoist, self.start_time )
        peer_ip = query_ip(self.partner)

        message={"MessageType":"RegisterChannel",
                 "Sender": "{}@{}".format(self.founder_pubkey,GateWayUrl),
                 "Receiver": "{}@{}".format(self.partner_pubkey, peer_ip),
                 "MessageBody":{"ChannelName":self.channel_name,
                                "Depoist":self.depoist,
                                }
        }
        result = mg.Message().send(message)
        if not result:
            APIChannel.delete_channel(filters={"channel_name":self.channel_name})

        return result


    def delete(self):
        pass

    @property
    def state(self):
        return None


def create_channel(wallet, founder, partner, asset_type, depoist):
    return Channel(founder, partner).create(asset_type, depoist, wallet)


def get_channel_name_via_address(address1, address2):
    channel = Channel.get_channel(address1, address2)
    return channel.channel_name


if __name__ == "__main__":
    md5s = hashlib.md5("AM3wPXYSPDuDxXfbPdrDeioDhiNU5oeAP8".encode())
    md5s.update("Aetwx1BNtXD78f25v47kLTrBaXQr1moZEs".encode())
    print(md5s.hexdigest().upper())