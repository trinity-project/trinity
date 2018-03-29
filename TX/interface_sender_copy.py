

import binascii
import time

from TX.MyTransaction import InvocationTransaction
from TX.TransactionAttribute import TransactionAttribute, TransactionAttributeUsage
from TX.config import *
from TX.utils import hex_reverse, ToAddresstHash, createTxid, createMultiSigContract, create_opdata, \
    createRSMCContract, createHTLCContract, createVerifyScript, pubkeyToAddress, pubkeyToAddressHash


def createFundingTx(walletSender,walletReceiver): #qian ming shi A de qian min zai hou
    '''

    :param walletSender: dict {
            "pubkey":"",
            "deposit":0
    }
    :param walletReceiver: dict {
            "pubkey":"",
            "deposit":0
    :return:
    '''

    multi_contract = createMultiSigContract([walletSender["pubkey"],walletReceiver["pubkey"]])
    contractAddress = multi_contract["address"]
    time_stamp = TransactionAttribute(usage=TransactionAttributeUsage.Remark,
                                      data=bytearray.fromhex(hex(int(time.time()))[2:]))
    address_hash_Sender = TransactionAttribute(usage=TransactionAttributeUsage.Script,
                                         data=ToAddresstHash(pubkeyToAddress(walletSender["pubkey"])).Data)
    address_hash_Receiver = TransactionAttribute(usage=TransactionAttributeUsage.Script,
                                         data=ToAddresstHash(pubkeyToAddress(walletReceiver["pubkey"])).Data)
    txAttributes = [address_hash_Sender, address_hash_Receiver, time_stamp]

    op_dataSender = create_opdata(address_from=pubkeyToAddress(walletSender["pubkey"]), address_to=contractAddress,
                                value=walletSender["deposit"],contract_hash=TNC)
    op_dataReceiver = create_opdata(address_from=pubkeyToAddress(walletReceiver["pubkey"]), address_to=contractAddress,
                                 value=walletReceiver["deposit"],contract_hash=TNC)

    tx = InvocationTransaction()
    tx.Version = 1
    tx.Attributes = txAttributes
    tx.Script = binascii.unhexlify(op_dataSender + op_dataReceiver)
    return {
        "txData":tx.get_tx_data(),
        "addressFunding":contractAddress,
        "txId": createTxid(tx.get_tx_data()),
        "scriptFunding":multi_contract["script"],
        "witness":"024140{signReceiver}2321"+walletReceiver["pubkey"]+"ac"+"4140{signSender}2321"+walletSender["pubkey"]+"ac"
    }



def createCTX(addressFunding,balanceSender,balanceReceiver,pubkeySender,pubkeyReceiver,fundingScript):
    RSMCContract=createRSMCContract(hashSender=pubkeyToAddressHash(pubkeySender),pubkeySender=pubkeySender,
                       hashReceiver=pubkeyToAddressHash(pubkeyReceiver),pubkeyReceiver=pubkeyReceiver,magicTimestamp=time.time())
    time_stamp = TransactionAttribute(usage=TransactionAttributeUsage.Remark,
                                      data=bytearray.fromhex(hex(int(time.time()))[2:]))
    address_hash_funding = TransactionAttribute(usage=TransactionAttributeUsage.Script,
                                         data=ToAddresstHash(addressFunding).Data)
    txAttributes = [address_hash_funding, time_stamp]

    op_data_to_RSMC = create_opdata(address_from=addressFunding, address_to=RSMCContract["address"], value=balanceSender,contract_hash=TNC)
    op_data_to_Receiver = create_opdata(address_from=addressFunding, address_to=pubkeyToAddress(pubkeyReceiver), value=balanceReceiver,contract_hash=TNC)

    tx = InvocationTransaction()
    tx.Version = 1
    tx.Attributes = txAttributes
    tx.Script = binascii.unhexlify(op_data_to_RSMC+op_data_to_Receiver)

    return {
        "txData":tx.get_tx_data(),
        "addressRSMC":RSMCContract["address"],
        "scriptRSMC":RSMCContract["script"],
        "txId":createTxid(tx.get_tx_data()),
        "witness":"018240{signSender}40{signReceiver}47"+fundingScript
    }

def createRDTX(addressRSMC,addressSender,balanceSender,CTxId,RSMCScript):

    time_stamp = TransactionAttribute(usage=TransactionAttributeUsage.Remark,
                                      data=bytearray.fromhex(hex(int(time.time()))[2:]))
    address_hash_RSMC = TransactionAttribute(usage=TransactionAttributeUsage.Script,
                                         data=ToAddresstHash(addressRSMC).Data)
    pre_txid = TransactionAttribute(usage=TransactionAttributeUsage.Remark1, data=bytearray.fromhex(
        hex_reverse(CTxId)))

    outputTo= TransactionAttribute(usage=TransactionAttributeUsage.Remark2, data=ToAddresstHash(addressSender).Data)

    txAttributes = [address_hash_RSMC, time_stamp,pre_txid,outputTo]

    op_data_to_Sender = create_opdata(address_from=addressRSMC, address_to=addressSender, value=balanceSender,contract_hash=TNC)


    tx = InvocationTransaction()
    tx.Version = 1
    tx.Attributes = txAttributes
    tx.Script = binascii.unhexlify(op_data_to_Sender)


    return {
        "txData":tx.get_tx_data(),
        "txId":createTxid(tx.get_tx_data()),
        "witness_part1":"01{lengthAll}{lengthOfBlockheight}{blockheight}40{signSender}40{signReceiver}",
        "witness_part2":createVerifyScript(RSMCScript)
    }

def createBRTX(addressRSMC,addressReceiver,balanceSender,RSMCScript):

    time_stamp = TransactionAttribute(usage=TransactionAttributeUsage.Remark,
                                      data=bytearray.fromhex(hex(int(time.time()))[2:]))
    address_hash_RSMC = TransactionAttribute(usage=TransactionAttributeUsage.Script,
                                         data=ToAddresstHash(addressRSMC).Data)
    outputTo = TransactionAttribute(usage=TransactionAttributeUsage.Remark1, data=ToAddresstHash(addressReceiver).Data)
    txAttributes = [address_hash_RSMC, time_stamp,outputTo]

    op_data_to_Receiver = create_opdata(address_from=addressRSMC, address_to=addressReceiver, value=balanceSender,contract_hash=TNC)


    tx = InvocationTransaction()
    tx.Version = 1
    tx.Attributes = txAttributes
    tx.Script = binascii.unhexlify(op_data_to_Receiver)


    return {
        "txData":tx.get_tx_data(),
        "txId":createTxid(tx.get_tx_data()),
        "witness_part1":"01{lengthAll}{lengthOfBlockheight}{blockheight}40{signSender}40{signReceiver}",
        "witness_part2":createVerifyScript(RSMCScript)
    }


def createHCTX(pubkeySender,pubkeyReceiver,HTLCValue,balanceSender,balanceReceiver,hashR,addressFunding,fundingScript):

    RSMCContract=createRSMCContract(hashSender=pubkeyToAddressHash(pubkeySender),pubkeySender=pubkeySender,
                       hashReceiver=pubkeyToAddressHash(pubkeyReceiver),pubkeyReceiver=pubkeyReceiver,magicTimestamp=time.time())

    HTLCContract=createHTLCContract(pubkeySender=pubkeySender,pubkeyReceiver=pubkeyReceiver,futureTimestamp=int(time.time())+600,
                                    hashR=hashR)
    time_stamp = TransactionAttribute(usage=TransactionAttributeUsage.Remark,
                                      data=bytearray.fromhex(hex(int(time.time()))[2:]))
    address_hash_funding = TransactionAttribute(usage=TransactionAttributeUsage.Script,
                                         data=ToAddresstHash(addressFunding).Data)
    txAttributes = [address_hash_funding, time_stamp]

    op_data_to_HTLC = create_opdata(address_from=addressFunding, address_to=HTLCContract["address"], value=HTLCValue,contract_hash=TNC)
    op_data_to_RSMC = create_opdata(address_from=addressFunding, address_to=RSMCContract["address"], value=balanceSender-HTLCValue,contract_hash=TNC)
    op_data_to_Receiver = create_opdata(address_from=addressFunding, address_to=pubkeyToAddress(pubkeyReceiver), value=balanceReceiver,contract_hash=TNC)

    tx = InvocationTransaction()
    tx.Version = 1
    tx.Attributes = txAttributes
    tx.Script = binascii.unhexlify(op_data_to_RSMC+op_data_to_Receiver+op_data_to_HTLC)

    return {
        "txData":tx.get_tx_data(),
        "addressRSMC":RSMCContract["address"],
        "addressHTLC":HTLCContract["address"],
        "RSMCscript":RSMCContract["script"],
        "HTLCscript":HTLCContract["script"],
        "txId":createTxid(tx.get_tx_data()),
        "witness": "018240{signSender}40{signReceiver}47" + fundingScript
    }


def createHEDTX(addressHTLC,addressReceiver,HTLCValue,HTLCScript):

    time_stamp = TransactionAttribute(usage=TransactionAttributeUsage.Remark,
                                      data=bytearray.fromhex(hex(int(time.time()))[2:]))
    address_hash_HTLC = TransactionAttribute(usage=TransactionAttributeUsage.Script,
                                         data=ToAddresstHash(addressHTLC).Data)
    txAttributes = [address_hash_HTLC, time_stamp]

    op_data_to_Receiver = create_opdata(address_from=addressHTLC, address_to=addressReceiver, value=HTLCValue,contract_hash=TNC)


    tx = InvocationTransaction()
    tx.Version = 1
    tx.Attributes = txAttributes
    tx.Script = binascii.unhexlify(op_data_to_Receiver)

    return {
        "txData":tx.get_tx_data(),
        "txId":createTxid(tx.get_tx_data()),
        "witness_part1": "01{lengthAll}{lengthOfR}{R}40{signReceiver}40{signSender}",
        "witness_part2": createVerifyScript(HTLCScript)
    }


def createHTTX(addressHTLC, addressSender, HTLCValue,HTLCScript):
    time_stamp = TransactionAttribute(usage=TransactionAttributeUsage.Remark,
                                      data=bytearray.fromhex(hex(int(time.time()))[2:]))
    address_hash_HTLC = TransactionAttribute(usage=TransactionAttributeUsage.Script,
                                             data=ToAddresstHash(addressHTLC).Data)
    txAttributes = [address_hash_HTLC, time_stamp]

    op_data_to_Sender = create_opdata(address_from=addressHTLC, address_to=addressSender, value=HTLCValue,
                                     contract_hash=TNC)

    tx = InvocationTransaction()
    tx.Version = 1
    tx.Attributes = txAttributes
    tx.Script = binascii.unhexlify(op_data_to_Sender)

    return {
        "txData":tx.get_tx_data(),
        "txId":createTxid(tx.get_tx_data()),
        "witness_part1": "01{lengthAll}{lengthOfR}{R}40{signReceiver}40{signSender}",
        "witness_part2": createVerifyScript(HTLCScript)
    }



def createChannel(walletSender,walletReceiver):
    funding_tx = createFundingTx(walletSender=walletSender, walletReceiver=walletReceiver)

    Sender_C_tx = createCTX(addressFunding=funding_tx["addressFunding"], balanceSender=walletSender["deposit"],
                     balanceReceiver=walletReceiver["deposit"], pubkeySender=walletSender["pubkey"],
                     pubkeyReceiver=walletReceiver["pubkey"], fundingScript=funding_tx["scriptFunding"])

    Sender_RD_tx = createRDTX(addressRSMC=Sender_C_tx["addressRSMC"], addressSender=pubkeyToAddress(walletSender["pubkey"]),
                       balanceSender=walletSender["deposit"], CTxId=Sender_C_tx["txId"], RSMCScript=Sender_C_tx["scriptRSMC"])

    Receiver_BR_tx = createBRTX(addressRSMC=Sender_C_tx["addressRSMC"], addressReceiver=pubkeyToAddress(walletReceiver["pubkey"]),
                       balanceSender=walletSender["deposit"], RSMCScript=Sender_C_tx["scriptRSMC"])



    Receiver_C_tx = createCTX(addressFunding=funding_tx["addressFunding"], balanceSender=walletReceiver["deposit"],
                     balanceReceiver=walletSender["deposit"], pubkeySender=walletReceiver["pubkey"],
                     pubkeyReceiver=walletSender["pubkey"], fundingScript=funding_tx["scriptFunding"])

    Receiver_RD_tx = createRDTX(addressRSMC=Receiver_C_tx["addressRSMC"], addressSender=pubkeyToAddress(walletReceiver["pubkey"]),
                       balanceSender=walletReceiver["deposit"], CTxId=Receiver_C_tx["txId"], RSMCScript=Receiver_C_tx["scriptRSMC"])

    Sender_BR_tx = createBRTX(addressRSMC=Receiver_C_tx["addressRSMC"], addressReceiver=pubkeyToAddress(walletSender["pubkey"]),
                       balanceSender=walletSender["deposit"], RSMCScript=Receiver_C_tx["scriptRSMC"])

    return {
        "fundingTx":funding_tx,

        "SenderTxs":{
            "C_TX":Sender_C_tx,
            "RD_TX":Sender_RD_tx,
            "BR_TX":Sender_BR_tx,
        },

        "ReceiverTxs": {
            "C_TX": Receiver_C_tx,
            "RD_TX": Receiver_RD_tx,
            "BR_TX": Receiver_BR_tx,
        },
    }


