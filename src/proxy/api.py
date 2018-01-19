from flask import Flask, request
from flask_jsonrpc import JSONRPC
from proxy.state import State
from channel_manager.state import ChannelAddress
from exception import ChannelDBAddFail
from channel_manager import manager
from flask_cors import CORS


app = Flask(__name__)
CORS(app)
jsonrpc = JSONRPC(app, "/")


@jsonrpc.method("registeaddress")
def regist_address(address, port = "20556"):
    ip_info = request.headers.getlist("X-Forwarded-For")[0] if request.headers.getlist("X-Forwarded-For") else request.remote_addr
    channel_address = ChannelAddress()
    try:
        channel_address.add_address(address, ip=ip_info, port= port)
    except ChannelDBAddFail:
        channel_address.delete_address(address)
        return State.raise_fail(101, "Can Not Add The Address")
    return State.success()


@jsonrpc.method("registchannle")
def regist_channle(sender_addr, receiver_addr, deposit, open_blockchain):
    return manager.ChannelManagent(sender=sender_addr, receiver=receiver_addr, deposit=deposit,
                               open_block_number=open_blockchain).registe_channel()


@jsonrpc.method("addtochannel")
def add_to_channel(addr, type, channel_name, signature, public_key):
    return manager.add_to_channel


@jsonrpc.method("getchannelstate")
def get_channel_state(self, sender_addr, receiver_addr):
    return manager.get_channel_state(sender_addr, receiver_addr)


@jsonrpc.method("sendertoreceiver")
def sender_to_receiver(sender_addr, receiver_addr, count):
    return manager.sender_to_receiver(sender_addr, receiver_addr, count)


@jsonrpc.method("getassetproof")
def get_asset_proof(channel_name):
    return manager.get_asset_proof(channel_name)


@jsonrpc.method("closechannel")
def close_channel(channel_name):
    if manager.close_channel(channel_name):
        return State.success()
    else:
        return State.raise_fail(102,"Close Channel Fail")



if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)