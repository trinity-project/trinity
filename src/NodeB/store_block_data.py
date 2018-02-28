import requests
import time
from decimal import Decimal
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Numeric,Boolean
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pymysql

from config import *

CONTRACTHASH="849d095d07950b9e56d0c895ec48ec5100cfdff1"

pymysql.install_as_MySQLdb()
engine = create_engine('mysql://%s:%s@%s/%s' %(MYSQLDATABASE["user"],MYSQLDATABASE["passwd"],MYSQLDATABASE["host"],MYSQLDATABASE["db"]))
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
                'value' : float(self.value)
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
                'value' : float(self.value)
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


class Tx(Base):
    __tablename__ = 'tx'
    id = Column(Integer, primary_key=True)
    tx_id = Column(String(256))
    tx_type = Column(String(32))
    confirmed = Column(Boolean,default=False)


    @staticmethod
    def save(tx_id,tx_type):
        new_instance = Tx(tx_id=tx_id, tx_type=tx_type)
        session.add(new_instance)
        session.commit()

Base.metadata.create_all(engine)


def hex_reverse(input):
    tmp_list = []
    for i in range(0, len(input), 2):
        tmp_list.append(input[i:i + 2])
    hex_str = "".join(list(reversed(tmp_list)))
    return hex_str


class TRANSACTION_TYPE(object):
    CONTRACT="ContractTransaction"
    CLAIM="ClaimTransaction"
    INVOKECONTRACT="InvocationTransaction"

def getblockcount():
    data = {
        "jsonrpc": "2.0",
        "method": "getblockcount",
        "params": [],
        "id": 1
    }
    res = requests.post(NEOCLIURL, headers=headers, json=data).json()
    return res

def getblock(index):

    data = {
          "jsonrpc": "2.0",
          "method": "getblock",
          "params": [index,1],
          "id": 1
}
    res = requests.post(NEOCLIURL, headers=headers, json=data).json()
    return res


localBlockCount = session.query(LocalBlockCout).first()
if localBlockCount:

    local_block_count=localBlockCount.height
else:
    local_block_count=0
    localBlockCount=LocalBlockCout(height=0)
    session.add(localBlockCount)
    session.commit()
i=0

while True:
    # time.sleep(0.01)
    chain_block_count=getblockcount()
    print (local_block_count)
    if local_block_count<chain_block_count["result"]:
        block_info=getblock(local_block_count)
        if len(block_info["result"]["tx"])>1:
            print (block_info["result"]["index"])
            for tx in block_info["result"]["tx"][1:]:
                if tx["type"]=="InvocationTransaction":
                    contract_hash=hex_reverse(tx["script"][-42:-2])
                    if contract_hash==CONTRACTHASH:
                        Tx.save(tx_id=tx["txid"],tx_type=tx["type"])

                if tx["type"] == "ContractTransaction":
                    Tx.save(tx_id=tx["txid"], tx_type=tx["type"])

                for vout in tx["vout"]:
                    if vout["asset"]==NEO_ASSETID:

                        NeoVout.save(tx_id=tx["txid"], address=vout["address"], asset_id=vout["asset"], vout_number=vout["n"], value=vout["value"])
                        exist_instance=session.query(Balance).filter(Balance.address==vout["address"]).first()
                        if exist_instance:
                            exist_instance.neo_balance+=int(vout["value"])
                            Balance.save(exist_instance)
                        else:
                            new_instance=Balance(address=vout["address"],neo_balance=vout["value"])
                            Balance.save(new_instance)

                    elif vout["asset"]==GAS_ASSETID:
                        GasVout.save(tx_id=tx["txid"], address=vout["address"], asset_id=vout["asset"], vout_number=vout["n"], value=Decimal(vout["value"]))
                        exist_instance=session.query(Balance).filter(Balance.address==vout["address"]).first()
                        if exist_instance:

                            exist_instance.gas_balance+=Decimal(vout["value"])
                            Balance.save(exist_instance)
                        else:
                            new_instance=Balance(address=vout["address"],gas_balance=Decimal(vout["value"]))
                            Balance.save(new_instance)

                for vin in tx["vin"]:
                    exist_instance=session.query(NeoVout).filter(NeoVout.tx_id == vin["txid"], NeoVout.vout_number == vin["vout"]).first()

                    if exist_instance:
                        print ("delete vout tx_id:{0} ".format(exist_instance.tx_id))
                        NeoVout.delete(exist_instance)
                        balance=session.query(Balance).filter(Balance.address==exist_instance.address).first()
                        balance.neo_balance-=exist_instance.value
                        Balance.save(balance)
                    else:
                        exist_instance=session.query(GasVout).filter(GasVout.tx_id == vin["txid"], GasVout.vout_number == vin["vout"]).first()
                        if exist_instance:
                            print ("delete vout tx_id:{0} ".format(exist_instance.tx_id))
                            GasVout.delete(exist_instance)
                            balance=session.query(Balance).filter(Balance.address==exist_instance.address).first()
                            balance.gas_balance-=exist_instance.value
                            Balance.save(balance)





        local_block_count+=1
        localBlockCount.height=local_block_count
        session.add(localBlockCount)
        session.commit()

    else:
        time.sleep(15)
