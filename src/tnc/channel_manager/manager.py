import logging

from .channel import Channel
from .state import ChannelDatabase, ChannelFile, ChannelState





log = logging.getLogger(__name__)


class ChannelManager(object):
    """

    """
    def __init__(self, contract, private_key, channel):
        self.contract = contract
        self.private_key = private_key
        self.channel  = channel

    def establish_channel(self):
        pass

    def close_channle(self):
        pass





