import logging

from  channel_manager.channel import Channel, State, get_channelnames_via_address
from  channel_manager import blockchain
from utils.channel import split_channel_name
from  channel_manager.state import ChannelDatabase, ChannelFile, ChannelState, ChannelAddress
from  exception import UnKnownType, NoChannelFound, ChannelNotInOpenState,ChannelFileNoExist,ChannelExistInDb
from  utils.common import CommonItem
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
        if channel.sender == sender_addr and channel.receiver == receiver_addr:
            if channel.state_in_database != State.OPEN:
                return {"channel_name":channel.channel_name,
                        "trad_info": "Channel exist but in state %s" %str(State(channel.state_in_database))}
            else:
                raw_tans = blockchain.NewTransection(asset_type, sender_addr, Contract_addr, int(deposit))
                channel.update_channel_to_database(sender_deposit=channel.sender_deposit + int(deposit))
                channel.update_channel_state(state=State.OPENING)
                return {"channel_name": channel.channel_name,
                        "trad_info": raw_tans}
        elif channel.sender == receiver_addr and channel.receiver == sender_addr:
            raw_tans = blockchain.NewTransection(asset_type, receiver_addr, Contract_addr, int(deposit))
            channel.update_channel_to_database(receiver_deposit=channel.receiver_deposit + int(deposit))
            channel.update_channel_state(state=State.OPENING)
            return {"channel_name": channel.channel_name,
                    "trad_info": raw_tans}
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
    ch.update_channel_state(State.OPEN)
    return None


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
        return ch.sender_to_receiver(count)
    elif receiver_addr == ch.sender and sender_addr == ch.receiver:
        return ch.receiver_to_sender(count)
    else:
        return "Error:Address and Channelname not match"


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





if __name__ == "__main__":
    result  = get_channel_state("AY8r7uG6rH7MRLhABALZvf8jM4bCSfn3YJ")
    print(result)


