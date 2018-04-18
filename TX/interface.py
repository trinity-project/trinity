import binascii
import time

from TX.MyTransaction import InvocationTransaction
from TX.TransactionAttribute import TransactionAttribute, TransactionAttributeUsage
from TX.config import *
from TX.utils import hex_reverse, ToAddresstHash, createTxid, createMultiSigContract, create_opdata, \
    createRSMCContract, createHTLCContract, createVerifyScript, pubkeyToAddress, pubkeyToAddressHash


def createFundingTx(walletSelf,walletOther): #self sign is behind
    '''

    :param walletSelf: dict {
            "pubkey":"",
            "deposit":0
    }
    :param walletOhter: dict {
            "pubkey":"",
            "deposit":0
    :return:
    '''

    multi_contract = createMultiSigContract([walletSelf["pubkey"],walletOther["pubkey"]])
    contractAddress = multi_contract["address"]
    time_stamp = TransactionAttribute(usage=TransactionAttributeUsage.Remark,
                                      data=bytearray.fromhex(hex(int(time.time()))[2:]))
    address_hash_self = TransactionAttribute(usage=TransactionAttributeUsage.Script,
                                         data=ToAddresstHash(pubkeyToAddress(walletSelf["pubkey"])).Data)
    address_hash_other = TransactionAttribute(usage=TransactionAttributeUsage.Script,
                                         data=ToAddresstHash(pubkeyToAddress(walletOther["pubkey"])).Data)
    txAttributes = [address_hash_self, address_hash_other, time_stamp]

    op_dataSelf = create_opdata(address_from=pubkeyToAddress(walletSelf["pubkey"]), address_to=contractAddress,
                                value=walletSelf["deposit"],contract_hash=TNC)
    op_dataOther = create_opdata(address_from=pubkeyToAddress(walletOther["pubkey"]), address_to=contractAddress,
                                 value=walletOther["deposit"],contract_hash=TNC)

    tx = InvocationTransaction()
    tx.Version = 1
    tx.Attributes = txAttributes
    tx.Script = binascii.unhexlify(op_dataSelf + op_dataOther)
    return {
        "txData":tx.get_tx_data(),
        "addressFunding":contractAddress,
        "txId": createTxid(tx.get_tx_data()),
        "scriptFunding":multi_contract["script"],
        "witness":"024140{signOther}2321"+walletOther["pubkey"]+"ac"+"4140{signSelf}2321"+walletSelf["pubkey"]+"ac"
    }



def createCTX(addressFunding,balanceSelf,balanceOther,pubkeySelf,pubkeyOther,fundingScript):
    RSMCContract=createRSMCContract(hashSelf=pubkeyToAddressHash(pubkeySelf),pubkeySelf=pubkeySelf,
                       hashOther=pubkeyToAddressHash(pubkeyOther),pubkeyOther=pubkeyOther,magicTimestamp=time.time())
    time_stamp = TransactionAttribute(usage=TransactionAttributeUsage.Remark,
                                      data=bytearray.fromhex(hex(int(time.time()))[2:]))
    address_hash_funding = TransactionAttribute(usage=TransactionAttributeUsage.Script,
                                         data=ToAddresstHash(addressFunding).Data)
    txAttributes = [address_hash_funding, time_stamp]

    op_data_to_RSMC = create_opdata(address_from=addressFunding, address_to=RSMCContract["address"], value=balanceSelf,contract_hash=TNC)
    op_data_to_other = create_opdata(address_from=addressFunding, address_to=pubkeyToAddress(pubkeyOther), value=balanceOther,contract_hash=TNC)

    tx = InvocationTransaction()
    tx.Version = 1
    tx.Attributes = txAttributes
    tx.Script = binascii.unhexlify(op_data_to_RSMC+op_data_to_other)

    return {
        "txData":tx.get_tx_data(),
        "addressRSMC":RSMCContract["address"],
        "scriptRSMC":RSMCContract["script"],
        "txId":createTxid(tx.get_tx_data()),
        "witness":"018240{signSelf}40{signOther}47"+fundingScript
    }

def createRDTX(addressRSMC,addressSelf,balanceSelf,CTxId,RSMCScript):

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


    return {
        "txData":tx.get_tx_data(),
        "txId":createTxid(tx.get_tx_data()),
        "witness":"01{blockheight_script}40{signOther}40{signSelf}fd"+createVerifyScript(RSMCScript)
    }

def createBRTX(addressRSMC,addressOther,balanceSelf,RSMCScript):

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


    return {
        "txData":tx.get_tx_data(),
        "txId":createTxid(tx.get_tx_data()),
        "witness": "01{blockheight_script}40{signOther}40{signSelf}fd" + createVerifyScript(RSMCScript)
    }


def createRefundTX(addressFunding,balanceSelf,balanceOther,pubkeySelf,pubkeyOther,fundingScript):

    time_stamp = TransactionAttribute(usage=TransactionAttributeUsage.Remark,
                                      data=bytearray.fromhex(hex(int(time.time()))[2:]))
    address_hash_funding = TransactionAttribute(usage=TransactionAttributeUsage.Script,
                                         data=ToAddresstHash(addressFunding).Data)
    txAttributes = [address_hash_funding, time_stamp]

    op_data_to_self = create_opdata(address_from=addressFunding, address_to=pubkeyToAddress(pubkeySelf), value=balanceSelf,contract_hash=TNC)
    op_data_to_other = create_opdata(address_from=addressFunding, address_to=pubkeyToAddress(pubkeyOther), value=balanceOther,contract_hash=TNC)

    tx = InvocationTransaction()
    tx.Version = 1
    tx.Attributes = txAttributes
    tx.Script = binascii.unhexlify(op_data_to_self+op_data_to_other)

    return {
        "txData":tx.get_tx_data(),
        "txId":createTxid(tx.get_tx_data()),
        "witness":"018240{signSelf}40{signOther}47"+fundingScript
    }


def createSelfHCTX(pubkeySelf, pubkeyOther, HTLCValue, balanceSelf, balanceOther, hashR, addressFunding, fundingScript):
    RSMCContract = createRSMCContract(hashSelf=pubkeyToAddressHash(pubkeySelf), pubkeySelf=pubkeySelf,
                                      hashOther=pubkeyToAddressHash(pubkeyOther), pubkeyOther=pubkeyOther,
                                      magicTimestamp=time.time())

    HTLCContract = createHTLCContract(pubkeySelf=pubkeySelf, pubkeyOther=pubkeyOther,
                                      futureTimestamp=int(time.time()) + 600,
                                      hashR=hashR)
    time_stamp = TransactionAttribute(usage=TransactionAttributeUsage.Remark,
                                      data=bytearray.fromhex(hex(int(time.time()))[2:]))
    address_hash_funding = TransactionAttribute(usage=TransactionAttributeUsage.Script,
                                                data=ToAddresstHash(addressFunding).Data)
    txAttributes = [address_hash_funding, time_stamp]

    op_data_to_HTLC = create_opdata(address_from=addressFunding, address_to=HTLCContract["address"], value=HTLCValue,
                                    contract_hash=TNC)
    op_data_to_RSMC = create_opdata(address_from=addressFunding, address_to=RSMCContract["address"],
                                    value=balanceSelf - HTLCValue, contract_hash=TNC)
    op_data_to_other = create_opdata(address_from=addressFunding, address_to=pubkeyToAddress(pubkeyOther),
                                     value=balanceOther, contract_hash=TNC)

    tx = InvocationTransaction()
    tx.Version = 1
    tx.Attributes = txAttributes
    tx.Script = binascii.unhexlify(op_data_to_RSMC + op_data_to_other + op_data_to_HTLC)

    return {
        "txData": tx.get_tx_data(),
        "addressRSMC": RSMCContract["address"],
        "addressHTLC": HTLCContract["address"],
        "RSMCscript": RSMCContract["script"],
        "HTLCscript": HTLCContract["script"],
        "txId": createTxid(tx.get_tx_data()),
        "witness": "018240{signSelf}40{signOther}47" + fundingScript
    }


def createSelfRDTX(addressRSMC, addressSelf, balanceSelf, selfHCTxId, RSMCScript):
    time_stamp = TransactionAttribute(usage=TransactionAttributeUsage.Remark,
                                      data=bytearray.fromhex(hex(int(time.time()))[2:]))
    address_hash_RSMC = TransactionAttribute(usage=TransactionAttributeUsage.Script,
                                             data=ToAddresstHash(addressRSMC).Data)
    pre_txid = TransactionAttribute(usage=TransactionAttributeUsage.Remark1, data=bytearray.fromhex(
        hex_reverse(selfHCTxId)))

    outputTo = TransactionAttribute(usage=TransactionAttributeUsage.Remark2, data=ToAddresstHash(addressSelf).Data)

    txAttributes = [address_hash_RSMC, time_stamp, pre_txid, outputTo]

    op_data_to_self = create_opdata(address_from=addressRSMC, address_to=addressSelf, value=balanceSelf,
                                    contract_hash=TNC)

    tx = InvocationTransaction()
    tx.Version = 1
    tx.Attributes = txAttributes
    tx.Script = binascii.unhexlify(op_data_to_self)

    return {
        "txData": tx.get_tx_data(),
        "txId": createTxid(tx.get_tx_data()),
        "witness_part1": "01{lengthAll}{lengthOfBlockheight}{blockheight}40{signSelf}40{signOther}",
        "witness_part2": createVerifyScript(RSMCScript)
    }


def createOtherHCTX(pubkeySelf, pubkeyOther, HTLCValue, balanceSelf, balanceOther, hashR, addressFunding,
                    fundingScript):
    RSMCContract = createRSMCContract(hashSelf=pubkeyToAddressHash(pubkeySelf), pubkeySelf=pubkeySelf,
                                      hashOther=pubkeyToAddressHash(pubkeyOther), pubkeyOther=pubkeyOther,
                                      magicTimestamp=time.time())

    HTLCContract = createHTLCContract(pubkeySelf=pubkeySelf, pubkeyOther=pubkeyOther,
                                      futureTimestamp=int(time.time()) + 600,
                                      hashR=hashR)
    time_stamp = TransactionAttribute(usage=TransactionAttributeUsage.Remark,
                                      data=bytearray.fromhex(hex(int(time.time()))[2:]))
    address_hash_funding = TransactionAttribute(usage=TransactionAttributeUsage.Script,
                                                data=ToAddresstHash(addressFunding).Data)
    txAttributes = [address_hash_funding, time_stamp]

    op_data_to_HTLC = create_opdata(address_from=addressFunding, address_to=HTLCContract["address"], value=HTLCValue,
                                    contract_hash=TNC)
    op_data_to_RSMC = create_opdata(address_from=addressFunding, address_to=RSMCContract["address"], value=balanceSelf,
                                    contract_hash=TNC)
    op_data_to_other = create_opdata(address_from=addressFunding, address_to=pubkeyToAddress(pubkeyOther),
                                     value=balanceOther - HTLCValue, contract_hash=TNC)

    tx = InvocationTransaction()
    tx.Version = 1
    tx.Attributes = txAttributes
    tx.Script = binascii.unhexlify(op_data_to_RSMC + op_data_to_other + op_data_to_HTLC)

    return {
        "txData": tx.get_tx_data(),
        "addressRSMC": RSMCContract["address"],
        "addressHTLC": HTLCContract["address"],
        "RSMCscript": RSMCContract["script"],
        "HTLCscript": HTLCContract["script"],
        "txId": createTxid(tx.get_tx_data()),
        "witness": "018240{signSelf}40{signOther}47" + fundingScript
    }


def createHTDTX(addressHTLC, pubkeySelf, pubkeyOther, HTLCValue, HTLCScript):
    RSMCContract = createRSMCContract(hashSelf=pubkeyToAddressHash(pubkeySelf), pubkeySelf=pubkeySelf,
                                      hashOther=pubkeyToAddressHash(pubkeyOther), pubkeyOther=pubkeyOther,
                                      magicTimestamp=time.time())

    time_stamp = TransactionAttribute(usage=TransactionAttributeUsage.Remark,
                                      data=bytearray.fromhex(hex(int(time.time()))[2:]))
    address_hash_HTLC = TransactionAttribute(usage=TransactionAttributeUsage.Script,
                                             data=ToAddresstHash(addressHTLC).Data)
    txAttributes = [address_hash_HTLC, time_stamp]

    op_data_to_self = create_opdata(address_from=addressHTLC, address_to=RSMCContract["address"], value=HTLCValue,
                                    contract_hash=TNC)

    tx = InvocationTransaction()
    tx.Version = 1
    tx.Attributes = txAttributes
    tx.Script = binascii.unhexlify(op_data_to_self)

    return {
        "txData": tx.get_tx_data(),
        "txId": createTxid(tx.get_tx_data()),
        "addressRSMC": RSMCContract["address"],
        "RSMCscript": RSMCContract["script"],
        "witness_part1": "01{lengthAll}{lengthOfR}{R}40{signOther}40{signSelf}",
        "witness_part2": createVerifyScript(HTLCScript)
    }


def createOtherRDTX(addressRSMC, addressSelf, balanceSelf, otherHCTxId, RSMCScript):
    time_stamp = TransactionAttribute(usage=TransactionAttributeUsage.Remark,
                                      data=bytearray.fromhex(hex(int(time.time()))[2:]))
    address_hash_RSMC = TransactionAttribute(usage=TransactionAttributeUsage.Script,
                                             data=ToAddresstHash(addressRSMC).Data)
    pre_txid = TransactionAttribute(usage=TransactionAttributeUsage.Remark1, data=bytearray.fromhex(
        hex_reverse(otherHCTxId)))

    outputTo = TransactionAttribute(usage=TransactionAttributeUsage.Remark2, data=ToAddresstHash(addressSelf).Data)

    txAttributes = [address_hash_RSMC, time_stamp, pre_txid, outputTo]

    op_data_to_self = create_opdata(address_from=addressRSMC, address_to=addressSelf, value=balanceSelf,
                                    contract_hash=TNC)

    tx = InvocationTransaction()
    tx.Version = 1
    tx.Attributes = txAttributes
    tx.Script = binascii.unhexlify(op_data_to_self)

    return {
        "txData": tx.get_tx_data(),
        "txId": createTxid(tx.get_tx_data()),
        "witness_part1": "01{lengthAll}{lengthOfBlockheight}{blockheight}40{signSelf}40{signOther}",
        "witness_part2": createVerifyScript(RSMCScript)
    }


def createHEDTX(addressHTLC, addressOther, HTLCValue, HTLCScript):
    time_stamp = TransactionAttribute(usage=TransactionAttributeUsage.Remark,
                                      data=bytearray.fromhex(hex(int(time.time()))[2:]))
    address_hash_HTLC = TransactionAttribute(usage=TransactionAttributeUsage.Script,
                                             data=ToAddresstHash(addressHTLC).Data)
    txAttributes = [address_hash_HTLC, time_stamp]

    op_data_to_other = create_opdata(address_from=addressHTLC, address_to=addressOther, value=HTLCValue,
                                     contract_hash=TNC)

    tx = InvocationTransaction()
    tx.Version = 1
    tx.Attributes = txAttributes
    tx.Script = binascii.unhexlify(op_data_to_other)

    return {
        "txData": tx.get_tx_data(),
        "txId": createTxid(tx.get_tx_data()),
        "witness_part1": "01{lengthAll}{lengthOfR}{R}40{signOther}40{signSelf}",
        "witness_part2": createVerifyScript(HTLCScript)
    }


def createHTTX(addressHTLC, pubkeySelf, pubkeyOther, HTLCValue, HTLCScript):
    RSMCContract = createRSMCContract(hashSelf=pubkeyToAddressHash(pubkeySelf), pubkeySelf=pubkeySelf,
                                      hashOther=pubkeyToAddressHash(pubkeyOther), pubkeyOther=pubkeyOther,
                                      magicTimestamp=time.time())

    time_stamp = TransactionAttribute(usage=TransactionAttributeUsage.Remark,
                                      data=bytearray.fromhex(hex(int(time.time()))[2:]))
    address_hash_HTLC = TransactionAttribute(usage=TransactionAttributeUsage.Script,
                                             data=ToAddresstHash(addressHTLC).Data)
    txAttributes = [address_hash_HTLC, time_stamp]

    op_data_to_self = create_opdata(address_from=addressHTLC, address_to=RSMCContract["address"], value=HTLCValue,
                                    contract_hash=TNC)

    tx = InvocationTransaction()
    tx.Version = 1
    tx.Attributes = txAttributes
    tx.Script = binascii.unhexlify(op_data_to_self)

    return {
        "txData": tx.get_tx_data(),
        "txId": createTxid(tx.get_tx_data()),
        "addressRSMC": RSMCContract["address"],
        "RSMCscript": RSMCContract["script"],
        "witness_part1": "01{lengthAll}{lengthOfR}{R}40{signOther}40{signSelf}",
        "witness_part2": createVerifyScript(HTLCScript)
    }


def createHTRDTX(addressRSMC, addressSelf, HTLCValue, HTTxId, RSMCScript):
    time_stamp = TransactionAttribute(usage=TransactionAttributeUsage.Remark,
                                      data=bytearray.fromhex(hex(int(time.time()))[2:]))
    address_hash_RSMC = TransactionAttribute(usage=TransactionAttributeUsage.Script,
                                             data=ToAddresstHash(addressRSMC).Data)
    pre_txid = TransactionAttribute(usage=TransactionAttributeUsage.Remark1, data=bytearray.fromhex(
        hex_reverse(HTTxId)))

    outputTo = TransactionAttribute(usage=TransactionAttributeUsage.Remark2, data=ToAddresstHash(addressSelf).Data)

    txAttributes = [address_hash_RSMC, time_stamp, pre_txid, outputTo]

    op_data_to_self = create_opdata(address_from=addressRSMC, address_to=addressSelf, value=HTLCValue,
                                    contract_hash=TNC)

    tx = InvocationTransaction()
    tx.Version = 1
    tx.Attributes = txAttributes
    tx.Script = binascii.unhexlify(op_data_to_self)

    return {
        "txData": tx.get_tx_data(),
        "txId": createTxid(tx.get_tx_data()),
        "witness_part1": "01{lengthAll}{lengthOfBlockheight}{blockheight}40{signSelf}40{signOther}",
        "witness_part2": createVerifyScript(RSMCScript)
    }


def createChannel(walletSelf, walletOther):
    funding_tx = createFundingTx(walletSelf=walletSelf, walletOther=walletOther)

    self_C_tx = createCTX(addressFunding=funding_tx["addressFunding"], balanceSelf=walletSelf["deposit"],
                          balanceOther=walletOther["deposit"], pubkeySelf=walletSelf["pubkey"],
                          pubkeyOther=walletOther["pubkey"], fundingScript=funding_tx["scriptFunding"])

    self_RD_tx = createRDTX(addressRSMC=self_C_tx["addressRSMC"], addressSelf=pubkeyToAddress(walletSelf["pubkey"]),
                            balanceSelf=walletSelf["deposit"], CTxId=self_C_tx["txId"],
                            RSMCScript=self_C_tx["scriptRSMC"])

    other_BR_tx = createBRTX(addressRSMC=self_C_tx["addressRSMC"], addressOther=pubkeyToAddress(walletOther["pubkey"]),
                             balanceSelf=walletSelf["deposit"], RSMCScript=self_C_tx["scriptRSMC"])

    other_C_tx = createCTX(addressFunding=funding_tx["addressFunding"], balanceSelf=walletOther["deposit"],
                           balanceOther=walletSelf["deposit"], pubkeySelf=walletOther["pubkey"],
                           pubkeyOther=walletSelf["pubkey"], fundingScript=funding_tx["scriptFunding"])

    other_RD_tx = createRDTX(addressRSMC=other_C_tx["addressRSMC"], addressSelf=pubkeyToAddress(walletOther["pubkey"]),
                             balanceSelf=walletOther["deposit"], CTxId=other_C_tx["txId"],
                             RSMCScript=other_C_tx["scriptRSMC"])

    self_BR_tx = createBRTX(addressRSMC=other_C_tx["addressRSMC"], addressOther=pubkeyToAddress(walletSelf["pubkey"]),
                            balanceSelf=walletSelf["deposit"], RSMCScript=other_C_tx["scriptRSMC"])

    return {
        "fundingTx": funding_tx,

        "selfTxs": {
            "C_TX": self_C_tx,
            "RD_TX": self_RD_tx,
            "BR_TX": self_BR_tx,
        },

        "otherTxs": {
            "C_TX": other_C_tx,
            "RD_TX": other_RD_tx,
            "BR_TX": other_BR_tx,
        },
    }


def createHTLC_TXS(pubkeySelf, pubkeyOther, HTLCValue, balanceSelf, balanceOther, hashR, addressFunding, fundingScript):
    self_HC_tx = createHCTX(pubkeySelf=pubkeySelf, pubkeyOther=pubkeyOther, HTLCValue=HTLCValue,
                            balanceSelf=balanceSelf,
                            balanceOther=balanceOther, hashR=hashR, addressFunding=addressFunding,
                            fundingScript=fundingScript)

    other_HED_tx = createHEDTX(addressHTLC=self_HC_tx["addressHTLC"], addressOther=pubkeyToAddress(pubkeyOther),
                               HTLCValue=HTLCValue, HTLCScript=self_HC_tx["HTLCscript"])

    self_HTT_tx = createHTTX(addressHTLC=self_HC_tx["addressHTLC"], addressSelf=pubkeyToAddress(pubkeySelf),
                             HTLCValue=HTLCValue, HTLCScript=self_HC_tx["HTLCscript"])

    other_HC_tx = createHCTX(pubkeySelf=pubkeyOther, pubkeyOther=pubkeySelf, HTLCValue=HTLCValue,
                             balanceSelf=balanceSelf,
                             balanceOther=balanceOther, hashR=hashR, addressFunding=addressFunding,
                             fundingScript=fundingScript)