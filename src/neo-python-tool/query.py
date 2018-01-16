
# -*- coding: utf-8 -*-
import pprint

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from model import Vout, LocalBlockCout

engine = create_engine('sqlite:///privtnet.db')
Session = sessionmaker(bind=engine)

session=Session()

localBlockCount = session.query(LocalBlockCout).all()
if localBlockCount:
    localBlockCountInstace=localBlockCount[0]
    print (u"目前同步的区块数:",localBlockCountInstace.height)


def get_utxo_by_address(address):
    class_instacce=session.query(Vout).filter(Vout.address==address).all()
    reszult=[]
    if class_instacce:
        for i in class_instacce:
            reszult.append (i.to_json())
        return reszult


address="AVV143sXT2Veq8wKDT9Q2Skp2bezMZk2"  #更换不同的地址，返回相应的未消费的输出


pprint.pprint(get_utxo_by_address(address))





