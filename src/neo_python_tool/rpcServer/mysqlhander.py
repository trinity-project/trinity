
# -*- coding: utf-8 -*-

import pymysql
from pymysql import escape_string


class MysqlHander(object):

    def __init__(self,database):
        self.conn=pymysql.connect(**database)
        self.cursor = self.conn.cursor()

    def insert(self,table_name,table_data):
        table_keys=','.join(k for k in table_data.keys())
        table_values=','.join("'"+escape_string(str(v))+"'"  for v in table_data.values())
        sql = 'INSERT INTO %s(%s) VALUES (%s)' %(table_name,table_keys,table_values)
        self.cursor.execute(sql)
        self.conn.commit()



    def update(self,table_name,table_data,condition):
        table_data=','.join(k+"='"+escape_string(str(v))+"'"  for k,v in table_data.items() )
        sql='UPDATE %s SET %s %s'%(table_name,table_data,condition)
        self.cursor.execute(sql)
        self.conn.commit()


# localhost_database = {
#     'host': 'localhost',
#     'db': 'exampledb',
#     'user': 'root',
#     'passwd': '123456',
#     'charset':'utf8',
#     'cursorclass':pymysql.cursors.DictCursor
# }
# mysql=MysqlHander(localhost_database)
# mysql.cursor.execute('SELECT * FROM test')
# ress=mysql.cursor.fetchall()
# # ress=mysql.insert('test',{'test':'bb,cc'})
# print ress[2]