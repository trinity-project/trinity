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
#from jsonrpc import dispatcher

from .base_enum import EnumStatusCode
from trinity import DATABASE_CONFIG as cfg
from log import LOG


def connection_singleton(callback):
    instance={}
    def wrapper(*args):
        if callback not in instance:
            instance[callback] = callback(args[0])
        return instance[callback]

    return wrapper


def rpc_response(name):
    def handler(f):
        def rpc_call_register(f, name):
            pass
            #TODO
            #try:
                #dispatcher.add_method(f, name)
            #except Exception as exp_info:
                #LOG.error("Failed to register RPC call<name: {}>.".format(name))

        def wrapper(*args, **kwargs):
            result = f(*args, **kwargs)
            if isinstance(result, EnumStatusCode):
                return {'status': result.value, 'status_content': result.name}
            else:
                return {'status': EnumStatusCode.OK.value,
                        'status_content': EnumStatusCode.OK.name,
                        'content': result}

        # register the JSONRPC callback
        rpc_call_register(f, name)

        return wrapper
    return handler


class ModelSet(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class DBClient(object):
    """
        Descriptions    :
        Created         : 2018-02-13
    """
    def __init__(self):
        self.db_client = pymongo.MongoClient(self.uri)
        self.db = self.db_client.get_database(self.db_name)

    def close(self):
        try:
            self.db_client.close()
        except Exception as exp_info:
            LOG.exception('Exception happened to close DB client. Exception: {}'.format(exp_info))

        # reset the class member's value
        self.db_client = None
        self.db = None

    @property
    def uri(self):
        if hasattr(self, "_{}__uri".format(self.__class__.__name__)):
            LOG.info('Trinity DB URI: {}'.format(self.__uri))
            return self.__uri

        # Standard URI format: mongodb://[dbuser:dbpassword@]host:port/dbname
        uri_list = [cfg['type'] + ':', r'/' * 2]

        # to get the authentication info from the configuration
        auth = cfg.get('authentication', {})
        if auth.get('user') and auth.get('password'):
            # authentication is optional, however, it MUST be used for security later
            uri_list.append('{}:{}@'.format(auth['user'], auth['password']))

        # database host and port info
        uri_list.append('{}:{}/'.format(cfg['host'], cfg['port']))

        # database name
        uri_list.append(self.db_name)

        self.__uri = ''.join(uri_list)
        LOG.info('Trinity Configuration DB URI: {}'.format(self.__uri))

        return self.__uri

    @property
    def db_name(self):
        return cfg['name']


class DBManager(object):
    """
    Descriptions: This class will manage the operations of the databases. Include: add, delete, update, query.
    Created         : 2018-02-13
    Modified        : 2018-3-20

    ATTENTION: we didn't check any input from users, so each user MUST check whether their inputs are correct or not.
    """
    def add(self, **kwargs):
        """
        Description: Realize the database 'add' operation.
        :param kwargs:
        :return: True if success, False if failure
        """
        if not self.db_table:
            LOG.error('DB Collection is Invalid.')
            return EnumStatusCode.InvalidDatabaseConnection

        # create primary key if user specify primary_key one valid value
        if self.primary_key:
            if kwargs.get(self.primary_key):
                self.db_table.create_index(self.primary_key, unique=True)
            else:
                LOG.error('Could not find the primary key {} in the table item {}.'.format(self.primary_key, kwargs))
                return EnumStatusCode.PrimaryKeyNotFoundInAddingNewItem
        else:
            pass

        # to add a common part for each items of the table
        content = self.create_at
        content.update(kwargs)

        try:
            self.db_table.insert_one(content)

            return EnumStatusCode.OK
        except DuplicateKeyError as exp_info:
            LOG.exception('Primary Key {} is Duplicated. Exception: {}'.format(kwargs.get(self.primary_key), exp_info))
            return EnumStatusCode.PrimaryKeyIsDuplicated
        except Exception as exp_info:
            LOG.exception('Exception occurred during add item {}. Exception'.format(kwargs, exp_info))
            return EnumStatusCode.PrimaryKeyInsertWithException

    def update_one(self, primary_key, **kwargs):
        """
        :param primary_key:
        :param kwargs:
        :return:
        """
        if self.primary_key in kwargs.keys():
            LOG.warning('Primary key MUST not be changed.')
            kwargs.pop(self.primary_key)

        # add the update time.
        kwargs.update(self.update_at)
        result = self.db_table.update_one({self.primary_key: primary_key}, {'$set': kwargs})
        return self.__result_of_update(result)

    def update_many(self, filters, **kwargs):
        """

        :param filters:
        :param kwargs:
        :return:
        """
        if not filters:
            return EnumStatusCode.DBUpdatedWithDangerousFilters

        if self.is_all(filters):
            LOG.warning('All of items will be updated.')
            filters = {}

        if self.primary_key in kwargs.keys():
            LOG.warning('Primary key MUST not be changed.')
            kwargs.pop(self.primary_key)

        # add the update time.
        kwargs.update(self.update_at)
        result = self.db_table.update_many(filters, {'$set': kwargs})
        return self.__result_of_update(result)

    def delete_one(self, primary_key):
        """
        Delete items from the table
        :param primary_key:
        :return:
        """
        result = self.db_table.delete_one({self.primary_key: primary_key})
        return self.__result_of_delete(result)

    def delete_many(self, filters):
        if not filters:
            return EnumStatusCode.DBDeletedWithDangerousFilters

        if self.is_all(filters):
            LOG.warning('All of items will be deleted.')
            filters = {}

        result = self.db_table.delete_many(filters)
        return self.__result_of_delete(result)

    def query_one(self, primary_key, *args, **kwargs):
        result = self.db_table.find_one({self.primary_key: primary_key}, *args, **kwargs)
        return [ModelSet(**result)] if result else EnumStatusCode.DBQueryWithoutMatchedItems

    def query_many(self, filters, *args, **kwargs):
        cursor = self.db_table.find(filters, *args, **kwargs)
        result = [ModelSet(**res) for res in cursor.limit(0)]
        return result if result else EnumStatusCode.DBQueryWithoutMatchedItems

    def is_all(self, filters):
        return 'all' == filters.get(self.primary_key)

    @classmethod
    def close(cls):
        if cls.client:
            cls.client.close()

    @property
    def create_at(self):
        return {'create_at': datetime.utcnow(), 'update_at': ''}

    @property
    def update_at(self):
        return {'update_at': datetime.utcnow()}

    @property
    def client(self):
        return DBClient()

    @property
    def db_table(self):
        return None

    @property
    def primary_key(self):
        return None

    def __result_of_delete(self, result):
        if 0 >= result.deleted_count:
            LOG.info('No table items are deleted.')
            return EnumStatusCode.DBDeletedWithoutAnyItems

        return EnumStatusCode.OK

    def __result_of_update(self, result):
        """
        :param result:
        :return:
        """
        if 0 == result.matched_count:
            return EnumStatusCode.DBUpdatedButNoMatchedItemsOK
        elif 0 == result.modified_count:
            LOG.warning('Matched count: {}.'.format( result.matched_count))
            return EnumStatusCode.NOK
        elif result.matched_count != result.modified_count:
            LOG.warning('Matched count: {}; Modified count: {}.'.format(result.matched_count, result.modified_count,))
            return EnumStatusCode.DBUpdatedPartOfItemsOK

        return EnumStatusCode.OK
