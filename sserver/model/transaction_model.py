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


class TBLTransaction(DBManager):
    """
        Descriptions    :
        Created         : 2018-02-13
        Modified        : 2018-03-21
    """
    db_table = DBClient().db.Transaction
    primary_key = 'transaction'
    required_item = ['transaction', 'channel', 'nonce', 'tx_time', 'tx_type', 'asset_type', 'amount', 'pre_hash',
                     'fee', 'state']

    def add_one(self, transaction: str, channel: str, nonce: int, tx_time: str, tx_type: str, asset_type: str,
                amount: int, pre_hash: str, fee: int, state: str):
        # to check whether the state is correct:
        return super(TBLTransaction, self).add(transaction=transaction, channel=channel, nonce=nonce,
                                               tx_time=tx_time, tx_type=tx_type, asset_type=asset_type,
                                               amount=amount, pre_hash=pre_hash, fee=fee, state=state)


class APITransaction(object):
    table = TBLTransaction()

    @classmethod
    @rpc_response('AddTransaction')
    def add_ransaction(cls, *args):
        return cls.table.add_one(*args)

    @classmethod
    @rpc_response('DeleteTransaction')
    def delete_ransaction(cls, transaction):
        return cls.table.delete_one(transaction)

    @classmethod
    @rpc_response('BatchDeleteTransaction')
    def batch_delete_transaction(cls, filters):
        return cls.table.delete_many(filters)

    @classmethod
    @rpc_response('QueryTransaction')
    def query_transaction(cls, transaction, *args, **kwargs):
        return cls.table.query_one(transaction, *args, **kwargs)

    @classmethod
    @rpc_response('BatchQueryTransaction')
    def batch_query_transaction(cls, filters, *args, **kwargs):
        return cls.table.query_many(filters, *args, **kwargs)

    @classmethod
    @rpc_response('UpdateTransaction')
    def update_transaction(cls, transaction, **kwargs):
        return cls.table.update_one(transaction, **kwargs)

    @classmethod
    @rpc_response('BatchUpdateTransaction')
    def batch_update_transaction(cls, filters, **kwargs):
        return cls.table.update_many(filters, **kwargs)
