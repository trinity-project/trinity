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
from datetime import datetime
from trinity import DATABASE_CONFIG as cfg
from log import LOG


class DbModel(object):
    """
        Descriptions    :
        Created         : 2018-02-13
    """

    def __init__(self):
        self.db_client = pymongo.MongoClient(self.uri)
        self.db = self.db_client.get_database(self.db_name)

    @property
    def uri(self):
        # Standard URI format: mongodb://[dbuser:dbpassword@]host:port/dbname
        uri_list = [cfg['type'] + ':', r'/' * 2]

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
    objects = database_model
    db_table = None
    primary_key = None
    required_item = None

    def __init__(self, **kwargs):
        self.contents = kwargs
        if self.db_table:
            self.db_table.create_index(self.primary_key, unique=True)

    def save(self, **kwargs):
        # to check whether the contents is full of table items
        if not self.is_valid_contents(self.contents):
            LOG.error('Keys of Content must be equal to {}'.format(self.required_item))
            return

        self.contents.update({'created_at': datetime.utcnow()})

        if kwargs:
            self.contents.update(kwargs)

        try:
            self.db_table.insert(self.contents)
        except DuplicateKeyError as e:
            LOG.exception('Primary Key {} is Duplicated. Exception: {}'.format(self.primary_key, e))
            return
        except Exception as e:
            LOG.exception('Exception occurred with primary key {}. Exception: {}'.format(self.primary_key, e))
            return

        return True

    def update(self, filters=None, update_many=False, **update):
        """
        Update one table item.
        :param filters:
        :param update_many:
        :param update:
        :return:
        """
        if not isinstance(update, dict):
            LOG.error('Dict must be used by update')
            return False

        if self.primary_key in update.keys():
            LOG.error('Primary key MUST not be changed')
            return False
        if update_many:
            result = self.db_table.update_many(filters, {'$set': update})
        else:
            result = self.db_table.update_one(filters, {'$set': update})

        if 0 == result.matched_count or 0 == result.modified_count:
            LOG.error('update_many: {}.{} items matched. {} items modified.'.format(update_many, result.matched_count,
                                                                                    result.modified_count))
            return False

        return True

    def delete(self, filters=None, delete_many=False):
        """
        Delete items from the table
        :param filters:
        :param delete_many:
        :return:
        """
        if delete_many:
            result = self.db_table.delete_many(filters)
        else:
            result = self.db_table.delete_one(filters)

        if 0 >= result.deleted_count:
            LOG.error('No table items are deleted.')
            return False

        return True

    def query(self, filters=None, *args, query_all=False, **kwargs):
        if query_all:
            return self.db_table.find(filters, *args, **kwargs)
        else:
            return [self.db_table.find_one(filters, *args, **kwargs)]

    def is_valid_contents(self, contents):
        return (set(contents.keys()) & set(self.required_item)) == set(self.required_item)


class Address(DbManager):
    """
        Descriptions    :
        contents        : {
                            address     : 'wallet address hash value',
                            chain       : 'type of block chain, such as btc, eth, neo, etc.'
                            public_key  : 'used to channel authentication'
                        }
        Created         : 2018-02-13
    """
    db_table = DbManager.objects.db.Address
    primary_key = 'address'
    required_item = ['address', 'chain', 'public_key']


class Channel(DbManager):
    """
        Descriptions    :
        Created         : 2018-02-13
    """
    db_table = DbManager.objects.db.Channel
    primary_key = 'channel_name'
    required_item = ['channel_name', 'sender', 'receiver', 'balance', 'state', 'alive_block', 'exchange']
    embedded_item = {'exchange': ['asset_type', 'deposit']}

    def is_valid_contents(self, contents):
        if super(Channel, self).is_valid_contents(contents):
            for embedded_key in self.embedded_item.keys():
                if (set(contents[embedded_key].keys() & set(self.embedded_item[embedded_key]))
                        != set(self.embedded_item[embedded_key])):
                    return False
            return True

        return False


class AssetType(DbManager):
    """
        Descriptions    :
        Created         : 2018-02-13
    """
    db_table = DbManager.objects.db.AssetType
    primary_key = 'asset_type'
    required_item = ['asset_type']


class Transaction(DbManager):
    """
        Descriptions    :
        Created         : 2018-02-13
    """
    db_table = DbManager.objects.db.Transaction
    primary_key = 'transaction'
    required_item = ['transaction', 'channel_name', 'nonce', 'tx_time', 'tx_type', 'asset_type', 'amount', 'pre_hash']


if '__main__' == __name__:
    print(database_model.uri)
    Address(address = "tt address", chain = '122334', public_key='test_pubkey',).save()
    # Address().update({'address':'t address'}, update_many=False, created_at='aaaaa')
    # Address().delete({'address':'t address'})
    # TableChannel(channel_name='test channel', exchange = {'asset_type':'neo', 'deposit':1000}).save()
    # TableAssetType.insert({'asset_type': 'test asset type'})
    # TableTransaction.insert({'transaction': 'test transaction records'})
