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

from flask_jsonrpc.proxy import ServiceProxy
from trinity import CONFIGURE
from log import LOG as gatewaylog
from flask_jsonrpc import JSONRPC

class Sserver(object):
    ServerConfig = CONFIGURE["SSERVER"]
    Server = ServiceProxy("{0}:{1}/api".format(ServerConfig["url"], ServerConfig["port"]))

    @classmethod
    def register_address( cls,address, pubkey):
        gatewaylog.info("register address",address, pubkey)
        return cls.Server.registeaddress(address, pubkey)

    @classmethod
    def register_channel(cls, sender_addr, receiver_addr, asset_type, deposit, open_blockchain):
        gatewaylog.info("register channel",sender_addr, receiver_addr, asset_type, deposit, open_blockchain)
        return cls.Server.registchannel(sender_addr, receiver_addr, asset_type, deposit, open_blockchain)

    @classmethod
    def get_channel_state(cls, local_address):
        gatewaylog.info("get channel state", local_address)
        return cls.Server.getchannelstate(local_address)

    @classmethod
    def send_raw_transaction(cls, sender_address,channel_name, hex):
        gatewaylog.info("send raw transaction", sender_address, channel_name, hex)
        return cls.Server.sendrawtransaction(sender_address, channel_name, hex)

    @classmethod
    def sender_to_receiver(cls, sender_addr, receiver_addr, channel_name, asset_type, count):
        gatewaylog.info("sender to receiver",sender_addr, receiver_addr, count)
        return cls.Server.sendertoreceiver(sender_addr, receiver_addr, channel_name, asset_type, count)

    @classmethod
    def close_channel(cls, sender_addr, receiver_addr, channel_name):
        gatewaylog.info("closechannel", channel_name)
        return cls.Server.closechannel(sender_addr, receiver_addr, channel_name)


class BlockChainServer(object):
    ServerConfig = CONFIGURE["BLOCKCHAIN"]
    Server = ServiceProxy("{0}:{1}/api".format(ServerConfig["url"], ServerConfig["port"]))

    @classmethod
    def get_balance_onchain(cls, local_address,asset_type=None):
        gatewaylog.info("getbalanceonchain %s" %local_address)
        return cls.Server.getbalanceonchain(local_address, asset_type)



