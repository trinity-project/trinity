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

import logging

from channel_manager.channel import Channel, State, get_channelnames_via_address
from channel_manager import blockchain
from utils.channel import split_channel_name
from channel_manager.state import Message, ChannelState
from logzero import logger



log = logging.getLogger(__name__)

def regist_channel(sender_addr, receiver_addr, asset_type,deposit, open_blockchain):
    """
    This func is to register channel
    :param sender_addr: String, the sender address
    :param receiver_addr: String, receiver's address
    :param asset_type: String, asset type should be symbol name , asset id should be configured in the configure.json
    :param deposit:  String, depoist number in block chain
    :param open_blockchain:  Open block chain number
    :return: Dictionary, {"channel_name":channel_name,
                "trad_info":raw_tans}
    """
    channel = Channel(sender_addr,receiver_addr)
    logger.info('start to register channel')
    if channel.qeury_channel():
        return {"error": "channel already exist"}
    else:
        channel_name = channel.create(sender_deposit=int(deposit),
                                      open_block_number=int(open_blockchain), settle_timeout=10)
        if not channel_name:
            return {"channel_name": None,
                    "contract_address": None,
                    "trad_info": "on pub key or not register pub key"}
        channel.qeury_channel()
        raw_tans,tx_id, state = blockchain.deposit_transaction(asset_type, sender_addr, channel.contract_address,
                                                         int(deposit))
        if state:
            channel.update_channel_to_database(tx_id=tx_id, state=State.OPENING)
            return {"channel_name": channel_name,
                    "contract_address": channel.contract_address,
                    "trad_info": raw_tans}
        else:
            channel.delete_channel()
            channel.delete_channel_in_database()
            return {"channel_name": None,
                    "contract_address": None,
                    "trad_info": raw_tans}


def send_raw_transaction(txdata, signature, publickey):
    """
    :param sender_address: String, the sender address
    :param channel_name: String, channel name
    :param hex: String, the digital signature string
    :return: String, SUCCESS
    """
    raw_tx = blockchain.construct_raw_tx(txdata, signature, publickey)
    return blockchain.send_raw_transaction(raw_tx)


def get_channel_state(address):
    """
    :param sender_addr: String, the sender address
    :param receiver_addr: String, receiver's address
    :return: Dictionary, the channel information
    """
    message_info={}
    message = Message.pull_message(address)
    if message:
        message_info["type"] = "signature"
        message_info["message"] = message

    else:
        channel_info = _get_channel_states_info(address)
        message_info["type"] = "transaction"
        message_info["message"] = channel_info
    return message_info

def _get_channel_states_info(address):
    channel_infos =[]
    channels = get_channelnames_via_address(address)
    for channel in channels:
        channel_detail =[]
        ch = Channel(channel.sender, channel.receiver)
        sender_info = {"address": ch.sender,
                           "deposit": ch.sender_deposit,
                           "balance": ch.get_address_balance(ch.sender) if ch.get_address_balance(ch.sender) else 0}
        recevier_info = {"address": ch.receiver,
                           "deposit": ch.receiver_deposit,
                           "balance": ch.get_address_balance(ch.receiver) if ch.get_address_balance(ch.receiver) else 0}
        if ch.sender == address:
            channel_detail.append(sender_info)
            channel_detail.append(recevier_info)
        else:
            channel_detail.append(recevier_info)
            channel_detail.append(sender_info)
        channel_info = {
            "channel_name": ch.channel_name,
            "channel_state": str(State(ch.stateinDB)),
            "open_block":ch.open_block_number,
            "contract_address": ch.contract_address,
             "tx_info": channel_detail
        }
        channel_infos.append(channel_info)
    return channel_infos



def sender_to_receiver(sender_addr, receiver_addr, channel_name, asset_type, count):
    """
    :param sender_addr: String, the sender address
    :param receiver_addr: String, receiver's address
    :param channel_name: String, channel name
    :param asset_type: String, asset type should be symbol name , asset id should be configured in the configure.json
    :param count:  String, depoist number in block chain
    :return:
    """
    sender,receiver = split_channel_name(channel_name)
    ch = Channel(sender,receiver)
    if sender_addr == ch.sender and receiver_addr == ch.receiver:
        return ch.sender_to_receiver(float(count))
    elif receiver_addr == ch.sender and sender_addr == ch.receiver:
        return ch.receiver_to_sender(float(count))
    else:
        return {"error":"Address and Channelname not match"}


def close_channel(sender_addr, receiver_addr,channel_name):
    """
    :param sender_addr: String, the sender address
    :param receiver_addr: String, receiver's address
    :param channel_name: String, channel name
    :return:
    """
    sender, receiver = split_channel_name(channel_name)
    ch = Channel(sender, receiver)
    return ch.settle_balance_onchain()



def get_balance_onchain(address, asset_type):
    """
    :param address: String, address
    :param asset_type: String, asset type should be symbol name , asset id should be configured in the configure.json
    :return: Blance
    """
    return blockchain.get_balance(address,asset_type)


def update_deposit(address, channel_name, asset_type, value):
    """

    :param address: String , address
    :param channel_name: String, channel name
    :param asset_type: String, asset type
    :param value: String , the deposit number
    :return: {"channel_name": channel.channel_name,
            "trad_info": raw_tans}
    """

    sender, receiver = split_channel_name(channel_name)
    channel = Channel(sender, receiver)

    if channel.sender == address:
        if channel.stateinDB != State.OPEN:
            return {"channel_name": channel.channel_name,
                    "trad_info": "Channel exist but in state %s" % str(State(channel.stateinDB))}
        else:
            channel.update_channel_to_database(sender_deposit_cache=float(value))
            raw_tans, tx_id, state= blockchain.deposit_transaction(asset_type, address,
                                                                    channel.contract_address,value)
            if state:
                channel.update_channel_to_database(tx_id=tx_id, state=State.UPDATING)
    elif channel.receiver == address:
        channel.update_channel_to_database(receiver_deposit_cache=float(value))
        raw_tans, tx_id, state = blockchain.deposit_transaction(asset_type, address,
                                                                 channel.contract_address, value)
        if state:
            channel.update_channel_to_database(tx_id=tx_id, state=State.UPDATING)

    else:
        return {"error":"channel name not match the address"}
    return {"channel_name": channel.channel_name,
            "trad_info": raw_tans}


def depositin(address, value):
    channels = get_channelnames_via_address(address)
    success_channel = []
    for channel in channels:
        print(channel.channel_name)
        sender, receiver = split_channel_name(channel.channel_name)
        ch = Channel(sender, receiver)
        # if address == sender and value == ch.sender_deposit_cache:
        if address == sender:
            ch.set_channel_open()
            success_channel.append(channel.channel_name)
        # elif address == receiver and value == ch.receiver_deposit_cache:
        elif address == receiver:
            ch.set_channel_open()
            success_channel.append(channel.channel_name)
        else:
            continue

def depoistout(address, value):
    channels = get_channelnames_via_address(address)
    success_channel = []
    for channel in channels:
        if channel.state == State.SETTLING.value:
            sender, receiver = split_channel_name(channel.channel_name)
            ch = Channel(sender, receiver)
            ch.close()
            success_channel.append(channel.channel_name)
        else:
            continue

def settle_raw_tx(address, channel_name, txdata, signature):
    sig_in_channel = ChannelState(channel_name)
    if sig_in_channel.senderinDB == address:
        sig_in_channel.update_sender_signature(signature)
    elif sig_in_channel.recieverinDB == address:
        sig_in_channel.update_receiver_signature(signature)
        Message.set_message_done(address, channel_name)
    else:
        return "address not match the channel"
    Message.set_message_done(address, channel_name)

    if sig_in_channel.sender_signature and sig_in_channel.receiver_signature:
        print("sig_in_channel")
        raw_data = blockchain.construct_deposit_raw_tx(txdata, sig_in_channel.sender_signature,
                                                       sig_in_channel.receiver_signature,
                                            sig_in_channel.contract_hash)
        blockchain.send_raw_transaction(raw_data)
        return "Success"
    else:
        return None


def tx_onchain(from_addr, to_addr, asset_type, value):
    tx_data, tx_id, state = blockchain.deposit_transaction(asset_type,from_addr, to_addr, int(value))
    if state:
        return {"tx_info":tx_data,
         "tx_id": tx_id}
    else:
        return {"tx_info":None,
         "tx_id": None}


def get_history(channel_name, index, count):
    sender, receiver = split_channel_name(channel_name)
    ch = Channel(sender, receiver)
    result = ch.read_channel()
    return result[int(index):int(index)+int(count)]






if __name__ == "__main__":
    result  = send_raw_transaction("AY8r7uG6rH7MRLhABALZvf8jM4bCSfn3YJ",
                                   "AATT55AeVVHHBBxxpp44TTHH55kk55nnii11xx22mm8811PP77HHggaaJJUUWW88hh97",
                                   "899999919919919191991919111111111111111")
    print(result)


