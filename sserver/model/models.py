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
import pymongo
from pymongo.errors import DuplicateKeyError
from trinity import DATABASE_CONFIG as cfg
from log import LOG


class DbModel(object):
    """
        Descriptions    :
        Created         : 2018-02-13
    """
    def __init__(self):
        self.db_client  = pymongo.MongoClient(self.uri)
        self.db         = self.db_client.get_database(self.db_name)

    @property
    def uri(self):
        # Standard URI format: mongodb://[dbuser:dbpassword@]host:port/dbname
        uri_list = [cfg['type']+':']
        uri_list.append(r'/'*2)

        # to get the authentication info from the configuration
        auth = cfg.get('authentication', {})
        if auth.get('user') and auth.get('password'):
            # authentication is optional, however, it MUST be used for security later
            uri_list.append('{}:{}@'.format(auth['user'], auth['password']))
            uri_list.append(r'/')

        # database host and port info
        uri_list.append('{}:{}'.format(cfg['host'], cfg['port']))
        uri_list.append(r'/')

        # database name
        uri_list.append(self.db_name)

        return ''.join(uri_list)

    @property
    def db_name(self):
        return cfg['name']


database_model = DbModel()


class DbManager(object):
    objects     = database_model
    db_table    = None
    primary_key = None
    if db_table:
        db_table.create_index(primary_key, unique=True)

    @classmethod
    def insert(cls, contents):
        # the contents should be dict type.
        if not isinstance(contents, dict):
            LOG.error('The format of contents should be dict type, but {} is given.'.format(type(contents)))
            return

        # to check whether the contents is full of table items
        if not cls.is_valid_contents(contents):
            LOG.error('Keys of Content must be equal to {}'.format(cls.table_items))
            return

        try:
            cls.db_table.insert(contents)
        except DuplicateKeyError as e:
            LOG.exception('Primary Key {} is Duplicated. Exception: {}'.format(cls.primary_key, e))
        except Exception as e:
            LOG.exception('Exception occurred with primary key {}. Exception: {}'.format(cls.primary_key, e))


    @classmethod
    def is_valid_contents(cls, contents):
        return False if (set(contents.keys()) ^ set(cls.table_items)) else True


class TableAddress(DbManager):
    """
        Descriptions    :
        contents        : {
                            address     : 'wallet address hash value',
                            chain       : 'type of block chain, such as btc, eth, neo, etc.'
                            public_key  : 'used to channel authentication'
                        }
        Created         : 2018-02-13
    """
    db_table    = DbManager.objects.db.Address
    table_items = ['address', 'chain', 'public_key', 'created_at']
    primary_key = 'address'


class TableChannel(DbManager):
    """
        Descriptions    :
        Created         : 2018-02-13
    """
    db_table    = DbManager.objects.db.Channel
    table_items = ['channel_name', 'sender', 'receiver', 'balance', 'state', 'alive_block', 'created_at', 'exchange']
    primary_key = 'channel_name'
    embedded_items  = {'exchange': ['asset_type', 'deposit']}

    @classmethod
    def is_valid_contents(cls, contents):
        if super(TableChannel, cls).is_valid_contents(contents):
            result_all = []
            for embedded_key in cls.embedded_items.keys():
                result_all.append(set(contents[embedded_key].keys() ^ set(cls.embedded_items[embedded_key])))
            return False if any(result_all) else True

        return False



class TableAssetType(DbManager):
    """
        Descriptions    :
        Created         : 2018-02-13
    """
    db_table    = DbManager.objects.db.AssetType
    table_items = ['asset_type', 'created_at']
    primary_key = 'asset_type'


class TableTransaction(DbManager):
    """
        Descriptions    :
        Created         : 2018-02-13
    """
    db_table    = DbManager.objects.db.Transaction
    table_items = ['transaction', 'channel_name', 'nonce', 'tx_time', 'tx_type', 'asset_type', 'amount', 'pre_hash']
    primary_key = 'transaction'


if '__main__' == __name__:
    print (database_model.uri)
    TableAddress.insert({'address':"t address"})
    TableChannel.insert({'channel_name': 'test channel'})
    # TableAssetType.insert({'asset_type': 'test asset type'})
    # TableTransaction.insert({'transaction': 'test transaction records'})
