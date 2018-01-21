import logging

from  channel_manager.channel import Channel, State, get_channelnames_via_address
from  channel_manager import blockchain
from  channel_manager.state import ChannelDatabase, ChannelFile, ChannelState, ChannelAddress, OpenDataBase, DBSession
from  exception import UnKnownType, NoChannelFound, ChannelNotInOpenState,ChannelFileNoExist,ChannelExistInDb
from  utils.common import CommonItem
from configure import Configure

Contract_addr = Configure["ContractAddr"]


log = logging.getLogger(__name__)


class ChannelManagent(Channel):
    """

    """

    def __init__(self, sender, receiver, deposit, open_block_number):
        super(ChannelManagent, self).__init__(sender, receiver)
        self.channel_item = CommonItem.from_dict(self.to_dict)

    def registe_channel(self):
        try:
            channel_name = self.create()
            return channel_name
        except (ChannelFileNoExist,ChannelExistInDb) as e:
            return str(e)

    def add_to_channel(self, address, type, channel_name, signature, public_key):
        if type not in ["sender", "receiver"]:
            raise UnKnownType("%s not sender or receiver" %type)
        else:
            if type == "sender":
                result = blockchain.add_to_channel(address=address, type=type, channel_name = channel_name, deposit=self.channel_item.deposit,
                                        open_block_number=self.channel_item.open_bolck_number)
                if result:
                    return self.channel_name
                else:
                    return None

    def close_channel(self):
        self.update_channel_to_database(state=State.SETTLING.value)
        result = blockchain.setting_transection(self.sender, self.receiver, self.channel_name)
        if result:
            self.update_channel_to_database(state=State.CLOSED.value)
            self.close()
            return True
        else:
            return False

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
                        "trad_info": None}
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

def send_raw_transaction(sender_address, channel_name, hex):
    """

    :param sender_address:
    :param channel_name:
    :param hex:
    :return:
    """

    blockchain.send_raw_transection(hex)
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
        ch = Channel(channel)
        channel_detail = [{"address": ch.sender,
                           "deposit": ch.sender_deposit,
                           "balance": ch.get_address_balance(ch.sender)},
                          {"address": ch.receiver,
                           "deposit": ch.receiver_deposit,
                           "balance": ch.get_address_balance(ch.receiver)}
                          ]
        channel_info  = {
            "channel_name": ch.channel_name,
            "channel_state": ch.senderinDB,
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

    ch = Channel(channel_name)
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
    channel = Channel(channel_name)
    return channel.close()





if __name__ == "__main__":
    result  = ChannelManagent(sender="AY8r7uG6rH7MRLhABALZvf8jM4bCSfn3YJ",
                    receiver="AUvupHdCKhaSsfPpzo6f4He4c9wFwhkLmZ", deposit=10,
                            open_block_number=10).registe_channel()
    print(result)


