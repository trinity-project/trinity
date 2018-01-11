#!/usr/bin/env python
# encoding: utf-8
"""
@author: Maiganne
@contact: xuyunqiao826@gmail.com
@time: 2017/6/19 15:15
"""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, relationship




# engine = create_engine('mysql://root:root@localhost/test')
engine = create_engine('sqlite:///privtnet.db')
Session = sessionmaker(bind=engine)
Base = declarative_base()


class Vout(Base):
    __tablename__ = 'vout'
    id = Column(Integer, primary_key=True)
    tx_id = Column(String(256))
    address = Column(String(256))
    asset_id = Column(String(256))
    vout_number = Column(Integer)
    value = Column(String(256))
    # bs = relationship("B", backref="a")
    def __repr__(self):
        return "<Vout(tx_id='%s', vout_number='%s',address='%s')>" % (self.tx_id,self.vout_number,self.address)

    def to_json(self):
        return {
                'tx_id': self.tx_id,
                'address': self.address,
                'asset_id': self.asset_id,
                'vout_number': self.vout_number,
                'value' : self.value
                }


class LocalBlockCout(Base):
    __tablename__ = 'local_block_count'
    id = Column(Integer, primary_key=True)
    height = Column(Integer)




Base.metadata.create_all(engine)
