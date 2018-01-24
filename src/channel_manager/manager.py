import logging

from  channel_manager.channel import Channel, State, get_channelnames_via_address
from  channel_manager import blockchain
from utils.channel import split_channel_name
from channel_manager.state import ChannelDatabase, ChannelFile, ChannelState, ChannelAddress
from exception import ChannelExist, NoChannelFound, ChannelNotInOpenState,ChannelFileNoExist,ChannelExistInDb
from utils.common import CommonItem
from utils.channel import split_channel_name
from configure import Configure

Contract_addr = Configure["ContractAddr"]


log = logging.getLogger(__name__)

def regist_channel(sender_addr, receiver_addr, asset_type,deposit, open_blockchain):
    """

    :param sender_addr:
    :param receiver_addr:
    :param asset_type:
    :param deposit:
    :param open_blockchain:
    :return:
    """
    channel = Channel(sender_addr,receiver_addr)
    if channel.find_channel():
        return {"error": "channel already exist"}
    else:
        channel_name = channel.create(sender_deposit=int(deposit),reciever_deposit=0,open_block_number=int(open_blockchain),settle_timeout=10)
        raw_tans = blockchain.NewTransection(asset_type, sender_addr, Contract_addr, int(deposit))
        return {"channel_name":channel_name,
                "trad_info":raw_tans}


def send_raw_transaction(sender_address, channel_name, hex):
    """

    :param sender_address:
    :param channel_name:
    :param hex:
    :return:
    """

    blockchain.send_raw_transection(hex)
    sender,receiver = split_channel_name(channel_name)
    ch = Channel(sender, receiver)
    sender_deposit = ch.sender_deposit
    receiver_deposit = ch.receiver_deposit
    sender_cache = ch.sender_deposit_cache
    receiver_cache = ch.receiver_deposit_cache
    ch.update_channel_deposit(sender_deposit= sender_deposit+sender_cache,
                              receiver_deposit = receiver_deposit+receiver_cache)

    return ch.set_channel_open()



def get_channel_state(address):
    """

    :param sender_addr:
    :param receiver_addr:
    :return:
    """
    channel_infos =[]
    channels = get_channelnames_via_address(address)
    for channel in channels:
        ch = Channel(channel.sender, channel.receiver)
        channel_detail = [{"address": ch.sender,
                           "deposit": ch.sender_deposit,
                           "balance": ch.get_address_balance(ch.sender)},
                          {"address": ch.receiver,
                           "deposit": ch.receiver_deposit,
                           "balance": ch.get_address_balance(ch.receiver)}
                          ]
        channel_info  = {
            "channel_name": ch.channel_name,
            "channel_state": str(State(ch.stateinDB)),
            "open_block":ch.open_block_number,
             "tx_info": channel_detail
        }
        channel_infos.append(channel_info)
    return channel_infos



def sender_to_receiver(sender_addr, receiver_addr, channel_name, asset_type, count):
    """

    :param sender_addr:
    :param receiver_addr:
    :param channel_name:
    :param asset_type:
    :param count:
    :return:
    """
    sender,receiver = split_channel_name(channel_name)
    ch = Channel(sender,receiver)
    if sender_addr == ch.sender and receiver_addr == ch.receiver:
        return ch.sender_to_receiver(int(count))
    elif receiver_addr == ch.sender and sender_addr == ch.receiver:
        return ch.receiver_to_sender(int(count))
    else:
        return {"error":"Address and Channelname not match"}


def close_channel(sender_addr, receiver_addr,channel_name):
    """

    :param sender_addr:
    :param receiver_addr:
    :param channel_name:
    :return:
    """
    sender, receiver = split_channel_name(channel_name)
    ch = Channel(sender, receiver)
    return ch.close()


def get_balance_onchain(address, asset_type):
    """

    :param address:
    :param asset_type:
    :return:
    """
    return blockchain.get_balance(address,asset_type)


def update_deposit(address, channel_name, asset_type, value):
    """

    :param address:
    :param channel_name:
    :param asset_type:
    :param value:
    :return:
    """

    sender, receiver = split_channel_name(channel_name)
    channel = Channel(sender, receiver)

    if channel.sender == address:
        if channel.state_in_database != State.OPEN:
            return {"channel_name": channel.channel_name,
                    "trad_info": "Channel exist but in state %s" % str(State(channel.state_in_database))}
        else:
            raw_tans = blockchain.NewTransection(asset_type, address, Contract_addr, int(value))
            channel.update_channel_to_database(sender_deposit_cache=int(value))
    elif channel.receiver == address:
        raw_tans = blockchain.NewTransection(asset_type, address, Contract_addr, int(value))
        channel.update_channel_to_database(receiver_deposit_cache=int(value))
    else:
        return {"error":"channel name not match the address"}
    channel.update_channel_state(state=State.OPENING)
    return {"channel_name": channel.channel_name,
            "trad_info": raw_tans}



if __name__ == "__main__":
    result  = send_raw_transaction("AY8r7uG6rH7MRLhABALZvf8jM4bCSfn3YJ",
                                   "AATT55AeVVHHBBxxpp44TTHH55kk55nnii11xx22mm8811PP77HHggaaJJUUWW88hh97",
                                   "899999919919919191991919111111111111111")
    print(result)


