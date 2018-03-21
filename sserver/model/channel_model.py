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
from manager import DBClient, DBManager, rpc_response
from base_enum import EnumAssetType, EnumChannelState
from log import LOG


class TBLChannel(DBManager):
    """
        Descriptions    :
        Created         : 2018-02-13
        Modified        : 2018-03-21
    """
    db_table = DBClient().db.Channel
    primary_key = 'channel'
    required_item = ['channel', 'src_addr', 'dest_addr', 'balance', 'state', 'alive_block', 'deposit']

    def add_one(self, channel: str, src_addr: str, dest_addr: str, balance: int, state: str, alive_block: int,
                deposit:dict):
        if not self.is_valid_channel_state(state):
            LOG.error('Error Channel state<{}> is used.'.format(state))

        # Guarantee no possession loss even if users do some wrong operations.
        for asset_type in deposit.keys():
            if not self.is_valid_asset_type(asset_type):
                deposit.pop(asset_type)

        return super(TBLChannel, self).add(channel=channel, src_addr=src_addr, dest_addr=dest_addr,
                                           balance=balance, state=state, alive_block=alive_block,
                                           deposit=deposit)

    def is_valid_channel_state(self, state):
        return state in EnumChannelState.__members__

    def is_valid_asset_type(self, asset_type):
        return asset_type in EnumAssetType.__members__


class APIChannel(object):
    table = TBLChannel()

    @classmethod
    @rpc_response('AddChannel')
    def add_channel(cls, *args):
        return cls.table.add_one(*args)

    @classmethod
    @rpc_response('DeleteChannel')
    def delete_channel(cls, channel):
        return cls.table.delete_one(channel)

    @classmethod
    @rpc_response('BatchDeleteChannel')
    def batch_delete_channel(cls, filters):
        return cls.table.delete_many(filters)

    @classmethod
    @rpc_response('QueryChannel')
    def query_channel(cls, channel, *args, **kwargs):
        return cls.table.query_one(channel, *args, **kwargs)

    @classmethod
    @rpc_response('BatchQueryChannel')
    def batch_query_channel(cls, filters, *args, **kwargs):
        return cls.table.query_many(filters, *args, **kwargs)

    @classmethod
    @rpc_response('UpdateChannel')
    def update_channel(cls, channel, **kwargs):
        return cls.table.update_one(channel, **kwargs)

    @classmethod
    @rpc_response('BatchUpdateChannel')
    def batch_update_channel(cls, filters, **kwargs):
        return cls.table.update_many(filters, **kwargs)
