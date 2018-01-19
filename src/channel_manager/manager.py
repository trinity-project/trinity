import logging

from  channel_manager.channel import Channel, State
from  channel_manager import blockchain
from  channel_manager.state import ChannelDatabase, ChannelFile, ChannelState, ChannelAddress, OpenDataBase, DBSession
from  exception import UnKnownType, NoChannelFound, ChannelNotInOpenState,ChannelFileNoExist,ChannelExistInDb
from  utils.common import CommonItem


log = logging.getLogger(__name__)


class ChannelManagent(Channel):
    """

    """

    def __init__(self, sender, receiver, deposit, open_block_number):
        super(ChannelManagent, self).__init__(sender, receiver, deposit, open_block_number)
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
        self.update_channel_to_database(receiver=self.receiver, deposit=self.deposit,
                                                open_block_number=self.open_block_number,channel_name=self.channel_name,
                                                state=State.SETTLING)
        result = blockchain.setting_transection(self.sender, self.receiver, self.channel_name)
        if result:
            self.update_channel_to_database(receiver=self.receiver, deposit=self.deposit,
                                                    open_block_number=self.open_block_number,
                                                    channel_name=self.channel_name,
                                                    state=State.CLOSED)
            self.close()
            return True
        else:
            return False


def get_channel_from_channel_name(channel_name):
    """

    :param channel_name:
    :return:
    """
    with OpenDataBase(DBSession) as channle:
        try:
            match = channle.query(ChannelDatabase).filter(ChannelDatabase.channel_name == channel_name).one()
            return ChannelManagent(sender= match.sender, receiver = match.receiver, deposit= match.deposit,
                                   open_block_number=match.open_block_number)
        except:
            return None


def add_to_channel(address, type, channel_name, signature, public_key):
    """

    :param address:
    :param type:
    :param channel_name:
    :param signature:
    :return:
    """

    channel = get_channel_from_channel_name(channel_name)
    if channel:
        return channel.add_to_channel(address, type, channel_name, signature, public_key)
    else:
        raise NoChannelFound



def get_channel_state(address):
    """

    :param sender_addr:
    :param receiver_addr:
    :return:
    """

    return ChannelState(sender_addr).state_in_database


def sender_to_receiver(sender_addr, receiver_addr, count):
    """

    :param sender_addr:
    :param receiver_addr:
    :param count:
    :return:
    """
    channel_name = ChannelFile(sender_addr, receiver_addr).channel_name
    channel = get_channel_from_channel_name(channel_name)
    return channel.sender_to_receiver(count)


def get_asset_proof(channel_name):
    """

    :param channel_name:
    :return:
    """
    channel = get_channel_from_channel_name(channel_name)
    return channel.get_asset_proof()


def close_channel(channel_name):
    """

    :param channel_name:
    :return:
    """
    channel = get_channel_from_channel_name(channel_name)
    return channel.close_channel()





if __name__ == "__main__":
    result  = ChannelManagent(sender="AY8r7uG6rH7MRLhABALZvf8jM4bCSfn3YJ",
                    receiver="AUvupHdCKhaSsfPpzo6f4He4c9wFwhkLmZ", deposit=10,
                            open_block_number=10).registe_channel()
    print(result)


