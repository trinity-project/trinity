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

from flask import Flask, request
from flask_jsonrpc import JSONRPC
from exception import ChannelDBAddFail
from sserver.channel import manager
from flask_cors import CORS
from log.log import LOG as log


app = Flask(__name__)
cors = CORS(app, support_credentials=True)
jsonrpc = JSONRPC(app, "/")


@jsonrpc.method("registeaddress")
def regist_address(address, pubkey):
    log.info("registeaddress %s pubkey %s" %(address, pubkey))
    ip_info = request.headers.getlist("X-Forwarded-For")[0] if request.headers.getlist("X-Forwarded-For") \
        else request.remote_addr
    channel_address = ChannelAddress()
    try:
        channel_address.add_address(address, ip=ip_info, pubkey= port)
    except ChannelDBAddFail:
        channel_address.delete_address(address)
        return  "Can Not Add The Address"
    return "SUCCESS"


@jsonrpc.method("registchannel")
def regist_channle(sender_addr, receiver_addr, asset_type,deposit, open_blockchain):
    log.info("registchannle %s  %s %s" %(sender_addr, receiver_addr,deposit))
    return manager.regist_channel(sender_addr, receiver_addr, asset_type,deposit, open_blockchain)


@jsonrpc.method("getchannelstate")
def get_channel_state(local_address):
    #logger.info("getchannelstate %s" %local_address)
    return manager.get_channel_state(local_address)


@jsonrpc.method("sendrawtransaction")
def send_raw_transaction(sender_address,channel_name, hex):
    log.info("sendrawtransaction %s" %channel_name)
    return manager.send_raw_transaction(sender_address, channel_name, hex)


@jsonrpc.method("sendertoreceiver")
def sender_to_receiver(sender_addr, receiver_addr, channel_name, asset_type, count):
    log.info("sendertoreceiver %s %s %s" %(sender_addr, receiver_addr, count))
    return manager.sender_to_receiver(sender_addr, receiver_addr, channel_name, asset_type, count)


@jsonrpc.method("closechannel")
def close_channel(sender_addr, receiver_addr,channel_name):
    log.info("closechannel %s" %channel_name)
    if manager.close_channel(sender_addr, receiver_addr,channel_name):
        return "SUCCESS"
    else:
        return "Close Channel Fail"

@jsonrpc.method("getbalanceonchain")
def get_balance_onchain(local_address,asset_type=None):
    #logger.info("getbalanceonchain %s" %local_address)
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


@jsonrpc.method("depositin")
def depositin(address, value):
    log.info("depositin %s" %address)
    return manager.depositin(address, value)


@jsonrpc.method("depositout")
def depoistout(address, value):
    log.info("depositout %s" %address)
    return manager.depoistout(address, value)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)