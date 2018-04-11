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

from neo.Core.TX.Transaction import Transaction
from neocore.Cryptography.Crypto import Crypto
from neo.Network.NodeLeader import NodeLeader
import os
import pickle
from TX.interface import *
from wallet.utils import sign
from wallet.BlockChain import interface as Binterface
from log import LOG

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

    def transaction_exist(self):
        return os.path.isfile(self.tx_file)

    def signature(self, rawdata):
        return self.wallet.Sign(rawdata)

    def create_tx_file(self,channel_name):
        os.mknod(os.path.join(TxDataDir, channel_name+".data"))
        self.tx_file = self.get_transaction_file()

    def get_transaction_file(self):

         return os.path.join(TxDataDir, self.channel+".data")

    def store_transaction(self, tx_message):
        with open(self.tx_file, "wb+") as f:
            crypto_channel(f, **tx_message)
        return None

    def read_transaction(self):
        with open(self.tx_file, "rb") as f:
            try:
               return uncryto_channel(f)
            except:
                return None

    def update_transaction(self, tx_nonce, **kwargs):
        tx_infos = self.read_transaction()
        if tx_infos:
            info = tx_infos.get(tx_nonce)
            if not info:
                tx_infos[tx_nonce] = kwargs
            else:
                dictMerged = dict(info, **kwargs)
                tx_infos[tx_nonce] = dictMerged
        else:
            tx_infos=dict([(tx_nonce, kwargs)])
        self.store_transaction(tx_infos)

    @staticmethod
    def sendrawtransaction(raw_data):
        LOG.info("SendRawTransaction: {}".format(raw_data))
        result = Binterface.send_raw(raw_data)
        LOG.info("SendRawTransaction Result: {}".format(result))
        return result

    @staticmethod
    def genarate_raw_data(Singtxdata,Witness):
        return Singtxdata+Witness

    def get_founder(self):
        tx = self.read_transaction()
        return tx["0"]["Founder"]

    def get_balance(self, tx_nonce):
        tx = self.get_tx_nonce(tx_nonce)
        try:
            return tx["Balance"]
        except KeyError:
            return None

    def get_tx_nonce(self, tx_nonce):
        tx = self.read_transaction()
        return tx.get(tx_nonce) if tx else None

    def get_latest_nonceid(self, tx=None):
        tx = tx if tx else self.read_transaction()
        if tx is None:
            return 0
        nonce = []
        for i in tx.keys():
            try:
                nonce.append(int(i))
            except ValueError:
                continue
        return max(nonce)

    def get_transaction_state(self):
        tx = self.read_transaction()
        if tx:
            return tx.get("State")
        else:
            return None

    def realse_transaction(self):
        tx = self.read_transaction()
        tx_state = tx.get("State")
        if tx_state !="confirm":
            return False, "transaction state not be confirmed"
        latest_nonce =self.get_latest_nonceid(tx)
        latest_tx = tx.get(str(latest_nonce))
        latest_ctx = latest_tx.get("Commitment")
        ctx_txData = latest_ctx.get("originalData").get("txData")
        tx_id = latest_ctx.get("originalData").get("txId")
        ctx_witness = latest_ctx.get("originalData").get("witness")
        ctx_txData_other = latest_ctx.get("txDataSing")
        ctx_txData_sign = sign(ctx_txData, self.wallet)
        raw_data = ctx_txData+ctx_witness.format(signSelf=ctx_txData_other, signOther = ctx_txData_sign)
        TrinityTransaction.sendrawtransaction(raw_data)
        print("Commitment Tx TO Chain    ", tx_id)


def dic2byte(file_handler, **kwargs):
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
    return pickle.dump(kwargs, file_handler)

def uncryto_channel(file_handler):
    """

    :param file_handler:
    :return:
    """
    return pickle.load(file_handler)

def byte2dic(file_hander):
    """

    :param file_hander:
    :return:
    """
    try:
        pickle.load(file_hander)
    except:
        return None

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
            return pickles[0] if pickles else None

def scriptToAddress(script):
    scriptHash=Crypto.ToScriptHash(script)
    address=Crypto.ToAddress(scriptHash)
    return address

def construt_init_channel_transction(params):

    walletSelf={
        "pubkey":params[0],
        "deposit":params[1],
    }
    walletOther={
        "pubkey":params[2],
        "deposit":params[3],
    }
    funding_tx = createFundingTx(walletSelf=walletSelf, walletOther=walletOther)

    C_tx = createCTX(addressFunding=funding_tx["addressFunding"], balanceSelf=walletSelf["deposit"],
                          balanceOther=walletOther["deposit"], pubkeySelf=walletSelf["pubkey"],
                          pubkeyOther=walletOther["pubkey"], fundingScript=funding_tx["scriptFunding"])

    RD_tx = createRDTX(addressRSMC=C_tx["addressRSMC"], addressSelf=pubkeyToAddress(walletSelf["pubkey"]),
                            balanceSelf=walletSelf["deposit"], CTxId=C_tx["txId"],
                            RSMCScript=C_tx["scriptRSMC"])

    return {"funding_TX":funding_tx,"C_TX":C_tx,"R_TX":RD_tx}

def construt_update_channel_transction(params):
    walletSelf={
        "pubkey":params[0],
        "balance":params[1],
    }
    walletOther={
        "pubkey":params[2],
        "balance":params[3],
    }
    script_funding=params[4]
    script_rsmc=params[5]
    C_tx = createCTX(addressFunding=scriptToAddress(script_funding), balanceSelf=walletSelf["balance"],
                          balanceOther=walletOther["balance"], pubkeySelf=walletSelf["pubkey"],
                          pubkeyOther=walletOther["pubkey"], fundingScript=script_funding)

    RD_tx = createRDTX(addressRSMC=C_tx["addressRSMC"], addressSelf=pubkeyToAddress(walletSelf["pubkey"]),
                            balanceSelf=walletSelf["deposit"], CTxId=C_tx["txId"],
                            RSMCScript=C_tx["scriptRSMC"])

    BR_tx = createBRTX(addressRSMC=scriptToAddress(script_rsmc), addressOther=pubkeyToAddress(walletSelf["pubkey"]),
                            balanceSelf=walletSelf["deposit"], RSMCScript=script_rsmc)

    return {"BR_tx": BR_tx, "C_TX": C_tx, "R_TX": RD_tx}

if __name__== "__main__":
    tx = TrinityTransaction("Mytest","walle")
    TrinityTransaction("Mytest","wallt")
    m = {"test1":1}
    m1 = {"test2":2}
    tx.update_transaction("0",test1=1)
    tx.update_transaction("0",test2=2)
    print(tx.read_transaction())
    tx.update_transaction("1",H=1,x="tt")
    print(tx.read_transaction())





