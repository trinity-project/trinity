import binascii
import time

from TX.MyTransaction import InvocationTransaction
from TX.TransactionAttribute import TransactionAttribute, TransactionAttributeUsage
from TX.utils import hex_reverse, ToAddresstHash, createTxid, createMultiSigContract, create_opdata, \
    createRSMCContract, createHTLCContract, createVerifyScript, pubkeyToAddress, pubkeyToAddressHash, privtkey_sign, \
    privtKey_to_publicKey


#RSMC

def createFundingTx(walletSelf,walletOther,asset_id):
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

    multi_contract = createMultiSigContract(walletSelf["pubkey"],walletOther["pubkey"])
    contractAddress = multi_contract["address"]
    time_stamp = TransactionAttribute(usage=TransactionAttributeUsage.Remark,
                                      data=bytearray.fromhex(hex(int(time.time()))[2:]))
    address_hash_self = TransactionAttribute(usage=TransactionAttributeUsage.Script,
                                         data=ToAddresstHash(pubkeyToAddress(walletSelf["pubkey"])).Data)
    address_hash_other = TransactionAttribute(usage=TransactionAttributeUsage.Script,
                                         data=ToAddresstHash(pubkeyToAddress(walletOther["pubkey"])).Data)
    txAttributes = [address_hash_self, address_hash_other, time_stamp]

    op_dataSelf = create_opdata(address_from=pubkeyToAddress(walletSelf["pubkey"]), address_to=contractAddress,
                                value=walletSelf["deposit"],contract_hash=asset_id)
    op_dataOther = create_opdata(address_from=pubkeyToAddress(walletOther["pubkey"]), address_to=contractAddress,
                                 value=walletOther["deposit"],contract_hash=asset_id)

    tx = InvocationTransaction()
    tx.Version = 1
    tx.Attributes = txAttributes
    tx.Script = binascii.unhexlify(op_dataSelf + op_dataOther)

    hash_self=ToAddresstHash(pubkeyToAddress(walletSelf["pubkey"]))
    hash_other=ToAddresstHash(pubkeyToAddress(walletOther["pubkey"]))
    if hash_self > hash_other:
        witness = "024140{signOther}2321"+walletOther["pubkey"]+"ac"+"4140{signSelf}2321"+walletSelf["pubkey"]+"ac"
    else:
        witness = "024140{signSelf}2321"+walletSelf["pubkey"]+"ac"+"4140{signOther}2321"+walletOther["pubkey"]+"ac"

    return {
        "txData":tx.get_tx_data(),
        "addressFunding":contractAddress,
        "txId": createTxid(tx.get_tx_data()),
        "scriptFunding":multi_contract["script"],
        "witness":witness
    }

def createCTX(addressFunding,balanceSelf,balanceOther,pubkeySelf,pubkeyOther,fundingScript,asset_id):
    RSMCContract=createRSMCContract(hashSelf=pubkeyToAddressHash(pubkeySelf.strip()),pubkeySelf=pubkeySelf.strip(),
                                    hashOther=pubkeyToAddressHash(pubkeyOther.strip()),pubkeyOther=pubkeyOther.strip(),
                                    magicTimestamp=time.time())
    time_stamp = TransactionAttribute(usage=TransactionAttributeUsage.Remark,
                                      data=bytearray.fromhex(hex(int(time.time()))[2:]))
    address_hash_funding = TransactionAttribute(usage=TransactionAttributeUsage.Script,
                                         data=ToAddresstHash(addressFunding).Data)
    txAttributes = [address_hash_funding, time_stamp]

    op_data_to_RSMC = create_opdata(address_from=addressFunding, address_to=RSMCContract["address"],
                                    value=balanceSelf,contract_hash=asset_id)
    op_data_to_other = create_opdata(address_from=addressFunding, address_to=pubkeyToAddress(pubkeyOther),
                                     value=balanceOther,contract_hash=asset_id)

    tx = InvocationTransaction()
    tx.Version = 1
    tx.Attributes = txAttributes
    tx.Script = binascii.unhexlify(op_data_to_RSMC+op_data_to_other)

    return {
        "txData":tx.get_tx_data(),
        "addressRSMC":RSMCContract["address"],
        "scriptRSMC":RSMCContract["script"],
        "txId":createTxid(tx.get_tx_data()),
        "witness":"018240{signSelf}40{signOther}da"+fundingScript
    }

def createRDTX(addressRSMC,addressSelf,balanceSelf,CTxId,RSMCScript,asset_id):

    time_stamp = TransactionAttribute(usage=TransactionAttributeUsage.Remark,
                                      data=bytearray.fromhex(hex(int(time.time()))[2:]))
    address_hash_RSMC = TransactionAttribute(usage=TransactionAttributeUsage.Script,
                                         data=ToAddresstHash(addressRSMC).Data)
    pre_txid = TransactionAttribute(usage=TransactionAttributeUsage.Remark1,
                                    data=bytearray.fromhex(hex_reverse(CTxId)))

    outputTo= TransactionAttribute(usage=TransactionAttributeUsage.Remark2,
                                   data=ToAddresstHash(addressSelf).Data)

    txAttributes = [address_hash_RSMC, time_stamp,pre_txid,outputTo]

    op_data_to_self = create_opdata(address_from=addressRSMC, address_to=addressSelf,
                                    value=balanceSelf,contract_hash=asset_id)


    tx = InvocationTransaction()
    tx.Version = 1
    tx.Attributes = txAttributes
    tx.Script = binascii.unhexlify(op_data_to_self)


    return {
        "txData":tx.get_tx_data(),
        "txId":createTxid(tx.get_tx_data()),
        "witness":"01{blockheight_script}40{signOther}40{signSelf}fd"+createVerifyScript(RSMCScript)
    }

def createBRTX(addressRSMC,addressOther,balanceSelf,RSMCScript,asset_id):

    time_stamp = TransactionAttribute(usage=TransactionAttributeUsage.Remark,
                                      data=bytearray.fromhex(hex(int(time.time()))[2:]))
    address_hash_RSMC = TransactionAttribute(usage=TransactionAttributeUsage.Script,
                                         data=ToAddresstHash(addressRSMC).Data)
    outputTo = TransactionAttribute(usage=TransactionAttributeUsage.Remark1,
                                    data=ToAddresstHash(addressOther).Data)
    txAttributes = [address_hash_RSMC, time_stamp,outputTo]

    op_data_to_other = create_opdata(address_from=addressRSMC, address_to=addressOther,
                                     value=balanceSelf,contract_hash=asset_id)


    tx = InvocationTransaction()
    tx.Version = 1
    tx.Attributes = txAttributes
    tx.Script = binascii.unhexlify(op_data_to_other)


    return {
        "txData":tx.get_tx_data(),
        "txId":createTxid(tx.get_tx_data()),
        "witness": "01{blockheight_script}40{signOther}40{signSelf}fd" + createVerifyScript(RSMCScript)
    }

def createRefundTX(addressFunding,balanceSelf,balanceOther,pubkeySelf,pubkeyOther,fundingScript,asset_id):

    time_stamp = TransactionAttribute(usage=TransactionAttributeUsage.Remark,
                                      data=bytearray.fromhex(hex(int(time.time()))[2:]))
    address_hash_funding = TransactionAttribute(usage=TransactionAttributeUsage.Script,
                                         data=ToAddresstHash(addressFunding).Data)
    txAttributes = [address_hash_funding, time_stamp]

    op_data_to_self = create_opdata(address_from=addressFunding, address_to=pubkeyToAddress(pubkeySelf),
                                    value=balanceSelf,contract_hash=asset_id)
    op_data_to_other = create_opdata(address_from=addressFunding, address_to=pubkeyToAddress(pubkeyOther),
                                     value=balanceOther,contract_hash=asset_id)

    tx = InvocationTransaction()
    tx.Version = 1
    tx.Attributes = txAttributes
    tx.Script = binascii.unhexlify(op_data_to_self+op_data_to_other)

    return {
        "txData":tx.get_tx_data(),
        "txId":createTxid(tx.get_tx_data()),
        "witness":"018240{signSelf}40{signOther}da"+fundingScript
    }

#sender HTLC
def create_sender_HCTX(pubkeySender, pubkeyReceiver, HTLCValue, balanceSender, balanceReceiver, hashR,
                   addressFunding, fundingScript,asset_id):
    RSMCContract = createRSMCContract(hashSelf=pubkeyToAddressHash(pubkeySender), pubkeySelf=pubkeySender,
                                      hashOther=pubkeyToAddressHash(pubkeyReceiver), pubkeyOther=pubkeyReceiver,
                                      magicTimestamp=time.time())

    HTLCContract = createHTLCContract(pubkeySelf=pubkeySender, pubkeyOther=pubkeyReceiver,
                                      futureTimestamp=int(time.time()) + 600,
                                      hashR=hashR)
    time_stamp = TransactionAttribute(usage=TransactionAttributeUsage.Remark,
                                      data=bytearray.fromhex(hex(int(time.time()))[2:]))
    address_hash_funding = TransactionAttribute(usage=TransactionAttributeUsage.Script,
                                                data=ToAddresstHash(addressFunding).Data)
    txAttributes = [address_hash_funding, time_stamp]

    op_data_to_HTLC = create_opdata(address_from=addressFunding, address_to=HTLCContract["address"], value=HTLCValue,
                                    contract_hash=asset_id)
    op_data_to_RSMC = create_opdata(address_from=addressFunding, address_to=RSMCContract["address"],
                                    value=balanceSender, contract_hash=asset_id)
    op_data_to_receiver = create_opdata(address_from=addressFunding, address_to=pubkeyToAddress(pubkeyReceiver),
                                     value=balanceReceiver, contract_hash=asset_id)

    tx = InvocationTransaction()
    tx.Version = 1
    tx.Attributes = txAttributes
    tx.Script = binascii.unhexlify(op_data_to_RSMC + op_data_to_receiver + op_data_to_HTLC)

    return {
        "txData": tx.get_tx_data(),
        "addressRSMC": RSMCContract["address"],
        "addressHTLC": HTLCContract["address"],
        "RSMCscript": RSMCContract["script"],
        "HTLCscript": HTLCContract["script"],
        "txId": createTxid(tx.get_tx_data()),
        "witness": "018240{signSelf}40{signOther}da" + fundingScript
    }

def create_sender_RDTX(addressRSMC, addressSender, balanceSender, senderHCTxId, RSMCScript,asset_id):
    time_stamp = TransactionAttribute(usage=TransactionAttributeUsage.Remark,
                                      data=bytearray.fromhex(hex(int(time.time()))[2:]))
    address_hash_RSMC = TransactionAttribute(usage=TransactionAttributeUsage.Script,
                                             data=ToAddresstHash(addressRSMC).Data)
    pre_txid = TransactionAttribute(usage=TransactionAttributeUsage.Remark1, data=bytearray.fromhex(
        hex_reverse(senderHCTxId)))

    outputTo = TransactionAttribute(usage=TransactionAttributeUsage.Remark2, data=ToAddresstHash(addressSender).Data)

    txAttributes = [address_hash_RSMC, time_stamp, pre_txid, outputTo]

    op_data_to_sender = create_opdata(address_from=addressRSMC, address_to=addressSender, value=balanceSender,
                                    contract_hash=asset_id)

    tx = InvocationTransaction()
    tx.Version = 1
    tx.Attributes = txAttributes
    tx.Script = binascii.unhexlify(op_data_to_sender)

    return {
        "txData": tx.get_tx_data(),
        "txId": createTxid(tx.get_tx_data()),
        "witness": "01{blockheight_script}40{signReceiver}40{signSender}fd"+createVerifyScript(RSMCScript)
    }

def createHEDTX(addressHTLC, addressReceiver, HTLCValue, HTLCScript,asset_id):
    time_stamp = TransactionAttribute(usage=TransactionAttributeUsage.Remark,
                                      data=bytearray.fromhex(hex(int(time.time()))[2:]))
    address_hash_HTLC = TransactionAttribute(usage=TransactionAttributeUsage.Script,
                                             data=ToAddresstHash(addressHTLC).Data)
    txAttributes = [address_hash_HTLC, time_stamp]

    op_data_to_receiver = create_opdata(address_from=addressHTLC, address_to=addressReceiver, value=HTLCValue,
                                     contract_hash=asset_id)

    tx = InvocationTransaction()
    tx.Version = 1
    tx.Attributes = txAttributes
    tx.Script = binascii.unhexlify(op_data_to_receiver)

    return {
        "txData": tx.get_tx_data(),
        "txId": createTxid(tx.get_tx_data()),
        "witness": "01{R_script}40{signOther}40{signSelf}fd"+createVerifyScript(HTLCScript)
    }

def createHTTX(addressHTLC, pubkeySender, pubkeyReceiver, HTLCValue, HTLCScript,asset_id):
    RSMCContract = createRSMCContract(hashSelf=pubkeyToAddressHash(pubkeySender), pubkeySelf=pubkeySender,
                                      hashOther=pubkeyToAddressHash(pubkeyReceiver), pubkeyOther=pubkeyReceiver,
                                      magicTimestamp=time.time())

    time_stamp = TransactionAttribute(usage=TransactionAttributeUsage.Remark,
                                      data=bytearray.fromhex(hex(int(time.time()))[2:]))
    address_hash_HTLC = TransactionAttribute(usage=TransactionAttributeUsage.Script,
                                             data=ToAddresstHash(addressHTLC).Data)
    txAttributes = [address_hash_HTLC, time_stamp]

    op_data_to_RSMC = create_opdata(address_from=addressHTLC, address_to=RSMCContract["address"], value=HTLCValue,
                                    contract_hash=asset_id)

    tx = InvocationTransaction()
    tx.Version = 1
    tx.Attributes = txAttributes
    tx.Script = binascii.unhexlify(op_data_to_RSMC)

    return {
        "txData": tx.get_tx_data(),
        "txId": createTxid(tx.get_tx_data()),
        "addressRSMC": RSMCContract["address"],
        "RSMCscript": RSMCContract["script"],
        "witness": "01{R_script}40{signOther}40{signSelf}fd"+createVerifyScript(HTLCScript)
    }

def createHTRDTX(addressRSMC, addressSender, HTLCValue, HTTxId, RSMCScript,asset_id):
    time_stamp = TransactionAttribute(usage=TransactionAttributeUsage.Remark,
                                      data=bytearray.fromhex(hex(int(time.time()))[2:]))
    address_hash_RSMC = TransactionAttribute(usage=TransactionAttributeUsage.Script,
                                             data=ToAddresstHash(addressRSMC).Data)
    pre_txid = TransactionAttribute(usage=TransactionAttributeUsage.Remark1, data=bytearray.fromhex(
        hex_reverse(HTTxId)))

    outputTo = TransactionAttribute(usage=TransactionAttributeUsage.Remark2, data=ToAddresstHash(addressSender).Data)

    txAttributes = [address_hash_RSMC, time_stamp, pre_txid, outputTo]

    op_data_to_sender = create_opdata(address_from=addressRSMC, address_to=addressSender, value=HTLCValue,
                                    contract_hash=asset_id)

    tx = InvocationTransaction()
    tx.Version = 1
    tx.Attributes = txAttributes
    tx.Script = binascii.unhexlify(op_data_to_sender)

    return {
        "txData": tx.get_tx_data(),
        "txId": createTxid(tx.get_tx_data()),
        "witness": "01{blockheight_script}40{signReceiver}40{signSender}fd"+createVerifyScript(RSMCScript)
    }


#receiver HTLC
def create_receiver_HCTX(pubkeySender, pubkeyReceiver, HTLCValue, balanceSender, balanceReceiver, hashR, addressFunding,
                    fundingScript,asset_id):
    RSMCContract = createRSMCContract(hashSelf=pubkeyToAddressHash(pubkeyReceiver), pubkeySelf=pubkeyReceiver,
                                      hashOther=pubkeyToAddressHash(pubkeySender), pubkeyOther=pubkeySender,
                                      magicTimestamp=time.time())

    HTLCContract = createHTLCContract(pubkeySelf=pubkeyReceiver, pubkeyOther=pubkeySender,
                                      futureTimestamp=int(time.time()) + 600,
                                      hashR=hashR)
    time_stamp = TransactionAttribute(usage=TransactionAttributeUsage.Remark,
                                      data=bytearray.fromhex(hex(int(time.time()))[2:]))
    address_hash_funding = TransactionAttribute(usage=TransactionAttributeUsage.Script,
                                                data=ToAddresstHash(addressFunding).Data)
    txAttributes = [address_hash_funding, time_stamp]

    op_data_to_HTLC = create_opdata(address_from=addressFunding, address_to=HTLCContract["address"], value=HTLCValue,
                                    contract_hash=asset_id)
    op_data_to_RSMC = create_opdata(address_from=addressFunding, address_to=RSMCContract["address"],
                                    value=balanceReceiver,contract_hash=asset_id)
    op_data_to_sender = create_opdata(address_from=addressFunding, address_to=pubkeyToAddress(pubkeySender),
                                     value=balanceSender, contract_hash=asset_id)

    tx = InvocationTransaction()
    tx.Version = 1
    tx.Attributes = txAttributes
    tx.Script = binascii.unhexlify(op_data_to_RSMC + op_data_to_sender + op_data_to_HTLC)

    return {
        "txData": tx.get_tx_data(),
        "addressRSMC": RSMCContract["address"],
        "addressHTLC": HTLCContract["address"],
        "RSMCscript": RSMCContract["script"],
        "HTLCscript": HTLCContract["script"],
        "txId": createTxid(tx.get_tx_data()),
        "witness": "018240{signSelf}40{signOther}da" + fundingScript
    }

def create_receiver_RDTX(addressRSMC, addressReceiver, balanceReceiver, receiver_HCTxId, RSMCScript,asset_id):
    time_stamp = TransactionAttribute(usage=TransactionAttributeUsage.Remark,
                                      data=bytearray.fromhex(hex(int(time.time()))[2:]))
    address_hash_RSMC = TransactionAttribute(usage=TransactionAttributeUsage.Script,
                                             data=ToAddresstHash(addressRSMC).Data)
    pre_txid = TransactionAttribute(usage=TransactionAttributeUsage.Remark1, data=bytearray.fromhex(
        hex_reverse(receiver_HCTxId)))

    outputTo = TransactionAttribute(usage=TransactionAttributeUsage.Remark2, data=ToAddresstHash(addressReceiver).Data)

    txAttributes = [address_hash_RSMC, time_stamp, pre_txid, outputTo]

    op_data_to_receiver = create_opdata(address_from=addressRSMC, address_to=addressReceiver, value=balanceReceiver,
                                    contract_hash=asset_id)

    tx = InvocationTransaction()
    tx.Version = 1
    tx.Attributes = txAttributes
    tx.Script = binascii.unhexlify(op_data_to_receiver)

    return {
        "txData": tx.get_tx_data(),
        "txId": createTxid(tx.get_tx_data()),
        "witness": "01{blockheight_script}40{signOther}40{signSelf}fd"+createVerifyScript(RSMCScript)
    }

def createHTDTX(addressHTLC, pubkeySender,HTLCValue, HTLCScript,asset_id):

    time_stamp = TransactionAttribute(usage=TransactionAttributeUsage.Remark,
                                      data=bytearray.fromhex(hex(int(time.time()))[2:]))
    address_hash_HTLC = TransactionAttribute(usage=TransactionAttributeUsage.Script,
                                             data=ToAddresstHash(addressHTLC).Data)
    txAttributes = [address_hash_HTLC, time_stamp]

    op_data_to_sender = create_opdata(address_from=addressHTLC, address_to=pubkeyToAddress(pubkeySender),
                                      value=HTLCValue,contract_hash=asset_id)

    tx = InvocationTransaction()
    tx.Version = 1
    tx.Attributes = txAttributes
    tx.Script = binascii.unhexlify(op_data_to_sender)

    return {
        "txData": tx.get_tx_data(),
        "txId": createTxid(tx.get_tx_data()),
        "witness": "01{R_script}40{signOther}40{signSelf}fd"+createVerifyScript(HTLCScript)
    }

def createHETX(addressHTLC, pubkeySender,pubkeyReceiver,HTLCValue, HTLCScript,asset_id):
    RSMCContract = createRSMCContract(hashSelf=pubkeyToAddressHash(pubkeyReceiver), pubkeySelf=pubkeyReceiver,
                                      hashOther=pubkeyToAddressHash(pubkeySender), pubkeyOther=pubkeySender,
                                      magicTimestamp=time.time())

    time_stamp = TransactionAttribute(usage=TransactionAttributeUsage.Remark,
                                      data=bytearray.fromhex(hex(int(time.time()))[2:]))
    address_hash_HTLC = TransactionAttribute(usage=TransactionAttributeUsage.Script,
                                             data=ToAddresstHash(addressHTLC).Data)
    txAttributes = [address_hash_HTLC, time_stamp]

    op_data_to_RSMC = create_opdata(address_from=addressHTLC, address_to=RSMCContract["address"], value=HTLCValue,
                                    contract_hash=asset_id)

    tx = InvocationTransaction()
    tx.Version = 1
    tx.Attributes = txAttributes
    tx.Script = binascii.unhexlify(op_data_to_RSMC)

    return {
        "txData": tx.get_tx_data(),
        "txId": createTxid(tx.get_tx_data()),
        "addressRSMC": RSMCContract["address"],
        "RSMCscript": RSMCContract["script"],
        "witness": "01{R_script}40{signOther}40{signSelf}fd"+createVerifyScript(HTLCScript)
    }

def createHERDTX(addressRSMC, addressReceiver, HTLCValue, HETxId, RSMCScript,asset_id):
    time_stamp = TransactionAttribute(usage=TransactionAttributeUsage.Remark,
                                      data=bytearray.fromhex(hex(int(time.time()))[2:]))
    address_hash_RSMC = TransactionAttribute(usage=TransactionAttributeUsage.Script,
                                             data=ToAddresstHash(addressRSMC).Data)
    pre_txid = TransactionAttribute(usage=TransactionAttributeUsage.Remark1, data=bytearray.fromhex(
        hex_reverse(HETxId)))

    outputTo = TransactionAttribute(usage=TransactionAttributeUsage.Remark2,
                                    data=ToAddresstHash(addressReceiver).Data)

    txAttributes = [address_hash_RSMC, time_stamp, pre_txid, outputTo]

    op_data_to_receiver = create_opdata(address_from=addressRSMC, address_to=addressReceiver, value=HTLCValue,
                                    contract_hash=asset_id)

    tx = InvocationTransaction()
    tx.Version = 1
    tx.Attributes = txAttributes
    tx.Script = binascii.unhexlify(op_data_to_receiver)

    return {
        "txData": tx.get_tx_data(),
        "txId": createTxid(tx.get_tx_data()),
        "witness": "01{blockheight_script}40{signReceiver}40{signSender}fd"+createVerifyScript(RSMCScript)
    }



def create_sender_HTLC_TXS(pubkeySender, pubkeyReceiver, HTLCValue, balanceSender,
                           balanceReceiver, hashR, addressFunding, fundingScript,asset_id):
    sender_HCTX = create_sender_HCTX(pubkeySender=pubkeySender, pubkeyReceiver=pubkeyReceiver,
                                     HTLCValue=HTLCValue, balanceSender=balanceSender,
                                     balanceReceiver=balanceReceiver, hashR=hashR,
                                     addressFunding=addressFunding, fundingScript=fundingScript,
                                     asset_id=asset_id)

    sender_RDTX = create_sender_RDTX(addressRSMC=sender_HCTX["addressRSMC"], addressSender=pubkeyToAddress(pubkeySender),
                                     balanceSender=balanceSender, senderHCTxId=sender_HCTX["txId"],
                                     RSMCScript=sender_HCTX["RSMCscript"],asset_id=asset_id)

    HEDTX = createHEDTX(addressHTLC=sender_HCTX["addressHTLC"], addressReceiver=pubkeyToAddress(pubkeyReceiver),
                        HTLCValue=HTLCValue, HTLCScript=sender_HCTX["HTLCscript"],asset_id=asset_id)

    HTTX = createHTTX(addressHTLC=sender_HCTX["addressHTLC"], pubkeySender=pubkeySender,
                      pubkeyReceiver=pubkeyReceiver, HTLCValue=HTLCValue,
                      HTLCScript=sender_HCTX["HTLCscript"],asset_id=asset_id)

    HTRDTX = createHTRDTX(addressRSMC=HTTX["addressRSMC"], addressSender=pubkeyToAddress(pubkeySender),
                          HTLCValue=HTLCValue, HTTxId=HTTX["txId"], RSMCScript=HTTX["RSMCscript"],asset_id=asset_id)

    return {
        "HCTX":sender_HCTX,
        "RDTX":sender_RDTX,
        "HEDTX":HEDTX,
        "HTTX":HTTX,
        "HTRDTX":HTRDTX
    }


def create_receiver_HTLC_TXS(pubkeySender, pubkeyReceiver, HTLCValue, balanceSender,
                           balanceReceiver, hashR, addressFunding, fundingScript,asset_id):
    receiver_HCTX = create_receiver_HCTX(pubkeySender=pubkeySender, pubkeyReceiver=pubkeyReceiver,
                                     HTLCValue=HTLCValue, balanceSender=balanceSender,
                                     balanceReceiver=balanceReceiver, hashR=hashR,
                                     addressFunding=addressFunding, fundingScript=fundingScript,asset_id=asset_id)

    receiver_RDTX = create_receiver_RDTX(addressRSMC=receiver_HCTX["addressRSMC"],
                                         addressReceiver=pubkeyToAddress(pubkeyReceiver),
                                         balanceReceiver=balanceReceiver, receiver_HCTxId=receiver_HCTX["txId"],
                                         RSMCScript=receiver_HCTX["RSMCscript"],asset_id=asset_id)

    HTDTX = createHTDTX(addressHTLC=receiver_HCTX["addressHTLC"], pubkeySender=pubkeySender,
                        HTLCValue=HTLCValue, HTLCScript=receiver_HCTX["HTLCscript"],asset_id=asset_id)

    HETX = createHETX(addressHTLC=receiver_HCTX["addressHTLC"], pubkeySender=pubkeySender,
                      pubkeyReceiver=pubkeyReceiver, HTLCValue=HTLCValue,
                      HTLCScript=receiver_HCTX["HTLCscript"],asset_id=asset_id)

    HERDTX = createHERDTX(addressRSMC=HETX["addressRSMC"], addressReceiver=pubkeyToAddress(pubkeyReceiver),
                          HTLCValue=HTLCValue, HETxId=HETX["txId"], RSMCScript=HETX["RSMCscript"],asset_id=asset_id)

    return {
        "HCTX": receiver_HCTX,
        "RDTX": receiver_RDTX,
        "HTDTX": HTDTX,
        "HETX": HETX,
        "HERDTX": HERDTX
    }

#构建给单个地址发tnc的交易
def construct_tx(addressFrom,addressTo,value,assetId):

    time_stamp = TransactionAttribute(usage=TransactionAttributeUsage.Remark,
                                      data=bytearray.fromhex(hex(int(time.time()))[2:]))
    address_hash = TransactionAttribute(usage=TransactionAttributeUsage.Script,
                                        data=ToAddresstHash(addressFrom).Data)

    txAttributes = [address_hash, time_stamp]

    op_data = create_opdata(address_from=addressFrom, address_to=addressTo, value=value,
                            contract_hash=assetId)
    tx = InvocationTransaction()
    tx.Version = 1
    tx.Attributes = txAttributes
    tx.Script = binascii.unhexlify(op_data)

    return {
        "txData": tx.get_tx_data(),
        "txid": createTxid(tx.get_tx_data())
    }

#构建给3个地址发tnc的交易
def construct_multi_tx(addressFrom, targetList, assetId):
    time_stamp = TransactionAttribute(usage=TransactionAttributeUsage.Remark,
                                      data=bytearray.fromhex(hex(int(time.time()))[2:]))
    address_hash = TransactionAttribute(usage=TransactionAttributeUsage.Script,
                                        data=ToAddresstHash(addressFrom).Data)

    txAttributes = [address_hash, time_stamp]
    op_data=""
    for item in targetList:
        op_data += create_opdata(address_from=addressFrom, address_to=item[0], value=item[1],
                            contract_hash=assetId)

    tx = InvocationTransaction()
    tx.Version = 1
    tx.Attributes = txAttributes
    tx.Script = binascii.unhexlify(op_data)

    return {
        "txData": tx.get_tx_data(),
        "txid": createTxid(tx.get_tx_data())
    }


def sign(txData,privtKey):
    signature = privtkey_sign(txData,privtKey)
    publicKey=privtKey_to_publicKey(privtKey)
    rawData=txData+"01"+"41"+"40"+signature+"23"+"21"+publicKey+"ac"
    return rawData

