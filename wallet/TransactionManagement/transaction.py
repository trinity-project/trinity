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

#from wallet.ChannelManagement.channel import Channel
#from neo.Wallets.Wallet import Wallet

import binascii
from neo.Core.TX.Transaction import Transaction
from neocore.UInt160 import UInt160
from neocore.UInt256 import UInt256
from neo.Core.Helper import Helper
from neo.Network.NodeLeader import NodeLeader
import json
import os
import pickle


BlockHightRegister=[]
TxIDRegister= []


TxDataDir = os.path.join(os.path.dirname(__file__),"txdata")
if not os.path.exists(TxDataDir):
    os.makedirs(TxDataDir)


class TrinityTransaction(object):

    def __init__(self, channel, wallet):
        self.channel = channel
        self.wallet = wallet
        self.tx_file = self.get_transaction_file()

    def signature(self, rawdata):
        return self.wallet.Sign(rawdata)

    def get_transaction_file(self):
         return self.wallet.LoadStoredData(self.channel)

    def store_transaction(self, tx_message):
        with open(self.tx_file, "ab+") as f:
            crypto_channel(f, **tx_message)
        return None

    def read_transaction(self):
        with open(self.tx_file, "rb") as f:
            return uncryto_channel(f)

    @staticmethod
    def sendrawtransaction(raw_data):
        tx_script = binascii.unhexlify(raw_data.encode('utf-8'))
        transaction = Transaction.DeserializeFromBufer(tx_script)
        result = NodeLeader.Instance().Relay(transaction)
        return result

    @staticmethod
    def genarate_raw_data(txdata, txid, pubkey):
        return ""


def dic2btye(file_handler, **kwargs):
    """

    :param kwargs:
    :return:
    """
    return pickle.dump(kwargs, file_handler)


def crypto_channel(file_handler, **kwargs):
    """
    :param kwargs:
    :return:
    """
    return dic2btye(file_handler, **kwargs)

def uncryto_channel(file_handler):
    """

    :param file_handler:
    :return:
    """
    return byte2dic(file_handler)

def byte2dic(file_hander):
    """

    :param file_hander:
    :return:
    """
    return pickle_load(file_hander)

def pickle_load(file):
    """

    :param file:
    :return:
    """
    pickles = []
    while True:
        try:
            pickles.append(pickle.load(file))
        except EOFError:
            return pickles








if __name__== "__main__":
    print(TxDataDir)


