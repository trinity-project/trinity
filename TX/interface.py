import binascii
import time

from TX.MyTransaction import InvocationTransaction
from TX.TransactionAttribute import TransactionAttribute, TransactionAttributeUsage
from TX.config import *
from TX.utils import hex_reverse, ToAddresstHash,  createTxid, createMultiSigContract, create_opdata, \
    createRSMCContract


def createFundingTx(walletSelf,walletOther): #qian ming shi A de qian min zai hou
    '''

    :param walletSelf: dict {
            "pubkey":"",
            "address":"",
            "deposit":0
    }
    :param walletOhter: dict {
            "pubkey":"",
            "address":"",
            "deposit":0
    :return:
    '''

    multi_contract = createMultiSigContract([walletSelf["pubkey"],walletOther["pubkey"]])
    contractAddress = multi_contract["address"]
    time_stamp = TransactionAttribute(usage=TransactionAttributeUsage.Remark,
                                      data=bytearray.fromhex(hex(int(time.time()))[2:]))
    address_hash_self = TransactionAttribute(usage=TransactionAttributeUsage.Script,
                                         data=ToAddresstHash(walletSelf["address"]).Data)
    address_hash_other = TransactionAttribute(usage=TransactionAttributeUsage.Script,
                                         data=ToAddresstHash(walletOther["address"]).Data)
    txAttributes = [address_hash_self, address_hash_other, time_stamp]

    op_dataSelf = create_opdata(address_from=walletSelf["address"], address_to=contractAddress, value=walletSelf["deposit"],
                             contract_hash=TNC)
    op_dataOther = create_opdata(address_from=walletOther["address"], address_to=contractAddress, value=walletOther["deposit"],
                             contract_hash=TNC)

    tx = InvocationTransaction()
    tx.Version = 1
    tx.Attributes = txAttributes
    tx.Script = binascii.unhexlify(op_dataSelf + op_dataOther)

    return {
        "txData":tx.get_tx_data(),
        "addressFunding":contractAddress,
        "script":multi_contract["script"],
        "txId": createTxid(tx.get_tx_data())
    }


def createCTX(addressFunding,addressSelf,balanceSelf,addressOther,balanceOther,pubkeySelf,pubkeyOther):
    RSMCContract=createRSMCContract(hashSelf=ToAddresstHash(addressSelf).ToString2(),pubkeySelf=pubkeySelf,
                       hashOther=ToAddresstHash(addressOther).ToString2(),pubkeyOther=pubkeyOther,magicTimestamp=time.time())
    time_stamp = TransactionAttribute(usage=TransactionAttributeUsage.Remark,
                                      data=bytearray.fromhex(hex(int(time.time()))[2:]))
    address_hash_funding = TransactionAttribute(usage=TransactionAttributeUsage.Script,
                                         data=ToAddresstHash(addressFunding).Data)
    txAttributes = [address_hash_funding, time_stamp]

    op_data_to_RSMC = create_opdata(address_from=addressFunding, address_to=RSMCContract["address"], value=balanceSelf,contract_hash=TNC)
    op_data_to_other = create_opdata(address_from=addressFunding, address_to=addressOther, value=balanceOther,contract_hash=TNC)

    tx = InvocationTransaction()
    tx.Version = 1
    tx.Attributes = txAttributes
    tx.Script = binascii.unhexlify(op_data_to_RSMC+op_data_to_other)

    return {
        "txData":tx.get_tx_data(),
        "addressRSMC":RSMCContract["address"],
        "script":RSMCContract["script"],
        "txId":createTxid(tx.get_tx_data())
    }

def createRDTX(addressRSMC,addressSelf,balanceSelf,CTxId):

    time_stamp = TransactionAttribute(usage=TransactionAttributeUsage.Remark,
                                      data=bytearray.fromhex(hex(int(time.time()))[2:]))
    address_hash_RSMC = TransactionAttribute(usage=TransactionAttributeUsage.Script,
                                         data=ToAddresstHash(addressRSMC).Data)
    pre_txid = TransactionAttribute(usage=TransactionAttributeUsage.Remark1, data=bytearray.fromhex(
        hex_reverse(CTxId)))

    outputTo= TransactionAttribute(usage=TransactionAttributeUsage.Remark2, data=ToAddresstHash(addressSelf).Data)

    txAttributes = [address_hash_RSMC, time_stamp,pre_txid,outputTo]

    op_data_to_self = create_opdata(address_from=addressRSMC, address_to=addressSelf, value=balanceSelf,contract_hash=TNC)


    tx = InvocationTransaction()
    tx.Version = 1
    tx.Attributes = txAttributes
    tx.Script = binascii.unhexlify(op_data_to_self)

    return tx.get_tx_data()


def createBRTX(addressRSMC,addressOther,balanceSelf):

    time_stamp = TransactionAttribute(usage=TransactionAttributeUsage.Remark,
                                      data=bytearray.fromhex(hex(int(time.time()))[2:]))
    address_hash_RSMC = TransactionAttribute(usage=TransactionAttributeUsage.Script,
                                         data=ToAddresstHash(addressRSMC).Data)
    outputTo = TransactionAttribute(usage=TransactionAttributeUsage.Remark1, data=ToAddresstHash(addressOther).Data)
    txAttributes = [address_hash_RSMC, time_stamp,outputTo]

    op_data_to_other = create_opdata(address_from=addressRSMC, address_to=addressOther, value=balanceSelf,contract_hash=TNC)


    tx = InvocationTransaction()
    tx.Version = 1
    tx.Attributes = txAttributes
    tx.Script = binascii.unhexlify(op_data_to_other)

    return tx.get_tx_data()

