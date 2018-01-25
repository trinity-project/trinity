
# -*- coding: utf-8 -*-
import pprint

from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker

from neo_python_tool.model import Vout, LocalBlockCout
import os

PATH =  os.path.dirname(__file__)
BlockDB = os.path.join(PATH,"privtnet.db")

engine = create_engine('sqlite:///'+BlockDB)
SessionBlock = sessionmaker(bind=engine)

sessionblock=SessionBlock()

def get_current_block_number():
    localBlockCount = sessionblock.query(LocalBlockCout).all()
    if localBlockCount:
        localBlockCountInstace=localBlockCount[0]
        print ("Current Block Number:",localBlockCountInstace.height)
        return localBlockCountInstace.height
    else:
        return None


def get_utxo_by_address(address, asset_id):
    class_instacce=sessionblock.query(Vout).filter(and_(Vout.address==address, Vout.asset_id == asset_id)).all()
    result=[]
    if class_instacce:
        for i in class_instacce:
            result.append (i.to_json())
        return result








