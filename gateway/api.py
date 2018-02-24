
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


from flask import Flask
from flask_jsonrpc import JSONRPC
from exception import ChannelDBAddFail
from sserver.channel import manager
from flask_cors import CORS
from log.log import LOG as log
from gateway.interface import Sserver as s_server
from gateway.interface import BlockChainServer as blockchain_server


app = Flask(__name__)
cors = CORS(app, support_credentials=True)
jsonrpc = JSONRPC(app, "/")


@jsonrpc.method("registeaddress")
def regist_address(address, pubkey):
    return s_server.register_address(address, pubkey)


@jsonrpc.method("registchannle")
def regist_channle(sender_addr, receiver_addr, asset_type,deposit, open_blockchain):
    return s_server.register_channel(sender_addr, receiver_addr, asset_type, deposit, open_blockchain)


@jsonrpc.method("getchannelstate")
def get_channel_state(local_address):
    return s_server.get_channel_state(local_address)


@jsonrpc.method("sendrawtransaction")
def send_raw_transaction(sender_address,channel_name, hex):
    return s_server.send_raw_transaction(sender_address, channel_name, hex)


@jsonrpc.method("sendertoreceiver")
def sender_to_receiver(sender_addr, receiver_addr, channel_name, asset_type, count):
    return s_server.sender_to_receiver(sender_addr, receiver_addr, channel_name, asset_type, count)


@jsonrpc.method("closechannel")
def close_channel(sender_addr, receiver_addr,channel_name):
    if s.close_channel(sender_addr, receiver_addr,channel_name):
        return "SUCCESS"
    else:
        return "Close Channel Fail"

@jsonrpc.method("getbalanceonchain")
def get_balance_onchain(local_address,asset_type=None):
    return manager.get_balance_onchain(local_address, asset_type)


@jsonrpc.method("updatedeposit")
def update_deposit(local_address, channel_name, asset_type, value):
    log.info("updatedeposit %s %s %s" %(channel_name, local_address, value))
    return manager.update_deposit(local_address, channel_name, asset_type, value)


@jsonrpc.method("allocateaddress")
def allocate_address():
    return manager.allocate_address()


@jsonrpc.method("txonchain")
def tx_onchain(from_addr, to_addr, asset_type, value):
    log.info("txonchain %s %s %s" %(from_addr, to_addr, value))
    return manager.tx_onchain(from_addr, to_addr, asset_type, value)


@jsonrpc.method("transaction")
def receive_transaction(address, transaction):
    pass



if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)