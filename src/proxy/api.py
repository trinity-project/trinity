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
def regist_channle(sender_addr, receiver_addr, asset_type,deposit, open_blockchain):
    return manager.regist_channel(sender_addr, receiver_addr, asset_type,deposit, open_blockchain)


@jsonrpc.method("getchannelstate")
def get_channel_state(local_address):
    return manager.get_channel_state(local_address)


@jsonrpc.method("sendrawtransaction")
def send_raw_transaction(sender_address,channel_name, hex):
    return manager.send_raw_transaction(sender_address, channel_name, hex)


@jsonrpc.method("sendertoreceiver")
def sender_to_receiver(sender_addr, receiver_addr, channel_name, asset_type, count):
    return manager.sender_to_receiver(sender_addr, receiver_addr, channel_name, asset_type, count)


@jsonrpc.method("closechannel")
def close_channel(sender_addr, receiver_addr,channel_name):
    if manager.close_channel(sender_addr, receiver_addr,channel_name):
        return State.success()
    else:
        return State.raise_fail(102,"Close Channel Fail")

@jsonrpc.method("getbalanceonchain")
def get_balance_onchain(local_address,asset_type=None):
    return manager.get_balance_onchain(local_address, asset_type)


@jsonrpc.method("updatedeposit")
def update_deposit(local_address, channel_name, asset_type, value):
    return manager.update_deposit(local_address, channel_name, asset_type, value)



if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)