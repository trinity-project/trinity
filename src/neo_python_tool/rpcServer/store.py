
import requests
import time

from decimal import Decimal

from model import session,NeoVout,GasVout,Balance,LocalBlockCout



NEO_ASSETID="0xc56f33fc6ecfcd0c225c4ab356fee59390af8560be0e930faebe74a6daff7c9b"
GAS_ASSETID="0x602c79718b16e442de58778e148d0b1084e3b2dffd5de6b7b16cee7969282de7"

url="http://192.168.203.64:20332"
headers={
    "Content-Type":"application/json"
}
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
    res = requests.post(url, headers=headers, json=data).json()
    return res

def getblock(index):
    data = {
          "jsonrpc": "2.0",
          "method": "getblock",
          "params": [index,1],
          "id": 1
}
    res = requests.post(url, headers=headers, json=data).json()
    return res


localBlockCount = session.query(LocalBlockCout).first()
if localBlockCount:

    local_block_count=localBlockCount.height
else:
    local_block_count=0
    localBlockCount=LocalBlockCout(height=0)
    session.add(localBlockCount)
    session.commit()


while True:
    time.sleep(0.01)
    chain_block_count=getblockcount()
    if local_block_count<chain_block_count["result"]-2:
        block_info=getblock(local_block_count)
        if len(block_info["result"]["tx"])>1:
            print (block_info["result"]["index"])
            for tx in block_info["result"]["tx"][1:]:


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

                    else:
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




