# --*-- coding : utf-8 --*--
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

from exception import ChannelNotExist
import hashlib
from functools import wraps


def check_channel_exist(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not self.has_channel():
            raise ChannelNotExist
        else:
            return func(self,*args, **kwargs)
    return wrapper


class Channel(object):
    """
    """
    def __init__(self, founder, peer):
        self.founder = founder
        self.peer = peer

    @property
    def state(self):
        return None

    @property
    def channel_id(self):
        hash256 = hashlib.sha256()
        hash256.update(self.founder.encode("utf-8"))
        hash256.update(self.peer.encode("utf-8"))
        return hash256.hexdigest()

    def send_deposit(self, asset_type, deposit):
        pass

    def update_deposit(self, deposit):
        pass

    def update_balance(self):

        pass

    def has_channel(self):
        return True

    @classmethod
    def from_address(cls, address1, address2, channel_id):
        rets = [cls(address1, address2), cls(address2, address1)]
        for ret in rets:
            if ret.channel_id == channel_id:
                return ret
        return None

    def create(self):
        return