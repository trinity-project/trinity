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

BlockHeightRecord = os.path.join(TxDataDir,"block.data")

def monitorblock():

    while True:
        block = Blockchain.Default().GetBlock(str(Blockchain.Default().Height))
        try:
            block.LoadTransactions()
            jsn = block.ToJson()
            jsn['confirmations'] = Blockchain.Default().Height - block.Index + 1
            hash = Blockchain.Default().GetNextBlockHash(block.Hash)
            if hash:
                jsn['nextblockhash'] = '0x%s' % hash.decode('utf-8')
                send_message_to_gateway(jsn)
                handle_message(Blockchain.Default().Height,jsn)
                logger.info("Block %s / %s", str(jsn), str(Blockchain.Default().HeaderHeight))
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
        if txid in block_txids:
            value[1](value[0],*value[1:])
            match_list.append(value)
    for i in match_list:
        TxIDRegister.remove(i)

def register_monitor(*args):
    TxIDRegister.append(args)

def record_block(txid, block_height):
    with open(BlockHeightRecord, "wb+") as f:
        info = {}.setdefault(txid, block_height)
        crypto_channel(f,**info)







