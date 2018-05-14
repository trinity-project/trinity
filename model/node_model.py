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
from .manager import DBManager, rpc_response, connection_singleton


class TBLNode(DBManager):
    """
        Descriptions    :
        Created         : 2018-02-13
        Modified        : 2018-03-21
    """
    # def add_one(self, address: str, public_key:str, ip: str, balance: int, deposit: dict, fee: int,
    #             name:str, state: str, tti=0, type=''):
    #     return super(TBLNode, self).add(address=address, public_key=public_key, ip=ip, balance=balance,
    #                                     deposit=deposit, fee=fee, name=name, state=state, tti=tti, type='')
    def add_one(self, **kwargs):
        return super(TBLNode, self).add(
            public_key=kwargs.get("public_key"),
            cli_ip=kwargs.get("cli_ip"),
            ip=kwargs.get("ip"),
            balance={},
            deposit=kwargs.get("deposit"),
            fee=kwargs.get("fee"), 
            name=kwargs.get("name"), 
            status=kwargs.get("status"), 
            tti=kwargs.get("tti"), 
            type=kwargs.get("type")
        )

    @property
    @connection_singleton
    def client(self):
        return super(TBLNode, self).client

    @property
    def db_table(self):
        return self.client.db.Node

    @property
    def primary_key(self):
        # return 'address'
        return "public_key"

    @property
    def required_item(self):
        return ['public_key', 'ip', 'cli_ip', 'deposit', 'name', 'fee', 'status', 'tti']

    @property
    def optional_item(self):
        return ['name', 'type']


class APINode(object):
    table = TBLNode()

    @classmethod
    @rpc_response('AddNode')
    def add_ransaction(cls, **kwargs):
        return cls.table.add_one(**kwargs)

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