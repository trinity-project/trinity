#!/usr/bin/env python
# encoding: utf-8
"""
@author: Maiganne

"""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Numeric
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import pymysql
pymysql.install_as_MySQLdb()


engine = create_engine('mysql://root:root@localhost/testnet_wallet')
# engine = create_engine('sqlite:///test.db')
Session = sessionmaker(bind=engine)
Base = declarative_base()
session=Session()

class NeoVout(Base):
    __tablename__ = 'neo_vout'
    id = Column(Integer, primary_key=True)
    tx_id = Column(String(256))
    address = Column(String(256))
    asset_id = Column(String(256))
    vout_number = Column(Integer)
    value = Column(Integer,default=0)


    def to_json(self):
        return {
                'tx_id': self.tx_id,
                'address': self.address,
                'asset_id': self.asset_id,
                'vout_number': self.vout_number,
                'value' : self.value
                }
    @staticmethod
    def save(tx_id,address,asset_id,vout_number,value):
        new_instance = NeoVout(tx_id=tx_id, address=address, asset_id=asset_id, vout_number=vout_number,value=value)
        session.add(new_instance)
        session.commit()
    @staticmethod
    def delete(instanse):
        session.delete(instanse)
        session.commit()


class GasVout(Base):
    __tablename__ = 'gas_vout'
    id = Column(Integer, primary_key=True)
    tx_id = Column(String(256))
    address = Column(String(256))
    asset_id = Column(String(256))
    vout_number = Column(Integer)
    value = Column(Numeric(16,8),default=0)


    def to_json(self):
        return {
                'tx_id': self.tx_id,
                'address': self.address,
                'asset_id': self.asset_id,
                'vout_number': self.vout_number,
                'value' : self.value
                }

    @staticmethod
    def save(tx_id,address,asset_id,vout_number,value):
        new_instance = GasVout(tx_id=tx_id, address=address, asset_id=asset_id, vout_number=vout_number,value=value)
        session.add(new_instance)
        session.commit()
    @staticmethod
    def delete(instanse):
        session.delete(instanse)
        session.commit()

class Balance(Base):
    __tablename__ = 'balance'
    id = Column(Integer, primary_key=True)
    address = Column(String(256))
    neo_balance = Column(Integer,default=0)
    gas_balance =Column(Numeric(16,8),default=0)


    @staticmethod
    def save(self):
        session.add(self)
        session.commit()



class LocalBlockCout(Base):
    __tablename__ = 'local_block_count'
    id = Column(Integer, primary_key=True)
    height = Column(Integer)




Base.metadata.create_all(engine)

