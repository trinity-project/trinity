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


class TBLNode(DBManager):
    """
        Descriptions    :
        Created         : 2018-02-13
        Modified        : 2018-03-21
    """
    db_table = DBClient().db.Node
    primary_key = 'address'
    required_item = ['address', 'ip', 'port', 'deposit', 'fee', 'state', 'tti', 'spv_count']
    optional_item = ['node_name']

    def add_one(self, address: str, ip: str, port: int, deposit: dict, fee: int,
                state: str, tti: int, spv_count=0):
        return super(TBLNode, self).add(address=address, ip=ip, port=port, deposit=deposit, fee=fee,
                                        state=state, tti=tti, spv_count=0)


class APINode(object):
    table = TBLNode()

    @classmethod
    @rpc_response('AddNode')
    def add_ransaction(cls, *args):
        return cls.table.add_one(*args)

    @classmethod
    @rpc_response('DeleteNode')
    def delete_ransaction(cls, node):
        return cls.table.delete_one(node)

    @classmethod
    @rpc_response('BatchDeleteNode')
    def batch_delete_node(cls, filters):
        return cls.table.delete_many(filters)

    @classmethod
    @rpc_response('QueryNode')
    def query_node(cls, node, *args, **kwargs):
        return cls.table.query_one(node, *args, **kwargs)

    @classmethod
    @rpc_response('BatchQueryNode')
    def batch_query_node(cls, filters, *args, **kwargs):
        return cls.table.query_many(filters, *args, **kwargs)

    @classmethod
    @rpc_response('UpdateNode')
    def update_node(cls, node, **kwargs):
        return cls.table.update_one(node, **kwargs)

    @classmethod
    @rpc_response('BatchUpdateNode')
    def batch_update_node(cls, filters, **kwargs):
        return cls.table.update_many(filters, **kwargs)