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
from base_enum import EnumChainType


class TBLWalletAddress(DBManager):
    """
        Descriptions    :
        contents        : {
                            address     : 'wallet address hash value',
                            chain       : 'type of block chain, such as btc, eth, neo, etc.'
                            public_key  : 'used to channel authentication'
                            node_ip     : ''
                            create_at   :
                            update_at   :
                        }
        Created         : 2018-02-13
        Modified        : 2018-03-20
    """
    db_table = DBClient().db.Address
    primary_key = 'address'
    required_item = ['address', 'chain', 'public_key', 'node_ip']

    def add_one(self, address:str, chain:EnumChainType, public_key:str, node_ip=None):
        return super(TBLWalletAddress, self).add(address=address, chain=chain.value, public_key=public_key, node_ip=node_ip)


class APIWalletAddress(object):
    table = TBLWalletAddress()

    @classmethod
    @rpc_response('AddWalletAddress')
    def add_wallet_address(cls, *args):
        return cls.table.add_one(*args)

    @classmethod
    @rpc_response('DeleteWalletAddress')
    def delete_wallet_address(cls, address):
        return cls.table.delete_one(address)

    @classmethod
    @rpc_response('BatchDeleteWalletAddress')
    def batch_delete_wallet_address(cls, filters):
        return cls.table.delete_many(filters)

    @classmethod
    @rpc_response('QueryWalletAddress')
    def query_wallet_address(cls, address, *args, **kwargs):
        return cls.table.query_one(address, *args, **kwargs)

    @classmethod
    @rpc_response('BatchQueryWalletAddress')
    def batch_query_wallet_address(cls, filters, *args, **kwargs):
        return cls.table.query_many(filters, *args, **kwargs)

    @classmethod
    @rpc_response('UpdateWalletAddress')
    def update_wallet_address(cls, address, **kwargs):
        return cls.table.update_one(address, **kwargs)

    @classmethod
    @rpc_response('BatchUpdateWalletAddress')
    def update_wallet_address(cls, filters, **kwargs):
        return cls.table.update_many(filters, **kwargs)
