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


from logzero import logger
from neo.Core.Blockchain import Blockchain
import time
from wallet.TransactionManagement.transaction import BlockHightRegister, TxIDRegister,TxDataDir, crypto_channel
import os
from wallet.Interface.gate_way import send_message
import json
import requests


BlockHeightRecord = os.path.join(TxDataDir,"block.data")


TestNetUrl = "http://47.88.35.235:20332"


def get_block_count():
    request = {
  "jsonrpc": "2.0",
  "method": "getblockcount",
  "params": [],
  "id": 1
}

    result = requests.post(url = TestNetUrl, json = request)
    return result.json()["result"]

def send_raw(raw):
    request =  { "jsonrpc": "2.0",
  "method": "sendrawtransaction",
  "params": [raw],
  "id": 1}

    result = requests.post(url=TestNetUrl, json=request)
    return result.json()["result"]

def get_bolck(index):
    request = {
  "jsonrpc": "2.0",
  "method": "getblock",
  "params": [int(index), 1],
  "id": 1
}
    result = requests.post(url=TestNetUrl, json=request)
    return result.json()["result"]

def monitorblock():
    blockHeight = get_block_count()
    while True:
        #block = Blockchain.Default().GetBlock(str(Blockchain.Default().Height))
        try:

            block = get_bolck(int(blockHeight)-1)
            #block.LoadTransactions()
            #jsn = block.ToJson()
            #jsn['confirmations'] = Blockchain.Default().Height - block.Index + 1
            #hash = Blockchain.Default().GetNextBlockHash(block.Hash)
            #if hash:
                #jsn['nextblockhash'] = '0x%s' % hash.decode('utf-8')
            #send_message_to_gateway(block)
                #handle_message(Blockchain.Default().Height,jsn)
            logger.info("Block %s / %s", str(block), blockHeight)
            blockHeight +=1
        except Exception as e:
            logger.error("GetBlockError", e)
        time.sleep(15)

def send_message_to_gateway(message):
    send_message(message)

def handle_message(height,jsn):
    match_list=[]
    block_txids = [i.get("txid") for i in jsn.get("tx")]
    for index,value in enumerate(BlockHightRegister):
        if value[0] == height:
            value[1](*value[1:])
            match_list.append(value)
    for i in match_list:
        BlockHightRegister.remove(i)
    match_list =[]
    for index, value in enumerate(TxIDRegister):
        txid = value[0]
        print("Debug Handle Message:",txid)
        if txid in block_txids:
            value[1](value[0],*value[1:])
            match_list.append(value)
    for i in match_list:
        TxIDRegister.remove(i)

def register_monitor(*args):
    print("Debug Register ", args)
    TxIDRegister.append(args)

def register_block(*args):
    BlockHightRegister.append(args)

def record_block(txid, block_height):
    with open(BlockHeightRecord, "wb+") as f:
        info = {}
        info.setdefault(txid, block_height)
        crypto_channel(f,**info)



if __name__  == "__main__":
   blockcount = get_block_count()
   print(get_bolck(int(blockcount)-1))

   raw="d101a00400ca9a3b14f5db0e4427fbf90d1fa21c741545b3fd0a12e68314d3108141247338aa337da861b31ee214ce460fec53c1087472616e73666572675e7fb71d90044445caf77c0c36df0901fda8340cf10400ca9a3b14f5db0e4427fbf90d1fa21c741545b3fd0a12e6831487cc4b925bd8f6f3c4a77a20382af79c7d7c0b0753c1087472616e73666572675e7fb71d90044445caf77c0c36df0901fda8340cf100000000000000000320d3108141247338aa337da861b31ee214ce460fec2087cc4b925bd8f6f3c4a77a20382af79c7d7c0b07f0045ac207da0000024140803d8203470b8abbece6d7f47aafd738f1922571257cfaaee9c04915f84d547a25063c96e2c9f82624719f7d2b96e0e9350c8a8c16c99ec8124f3fda9c4d801d2321034531bfb4a0d5ed522d9d6bcb4243c8e15cb1ad04d76531a204e5e79784aa3719ac4140a492157372324c35fe1cc79d5bb3f44d946e1ce9a4e57154b926a549d3046722671032f765c503310793c0c24fcaf42370c96bd512c36249ce2765a0ebe61cd82321022369f2ed62f20b90a61053d26b8628cca4d4b267b8ac1f3cbc51e4d308711ae8ac"
   print(send_raw(raw))








