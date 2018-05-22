import binascii
import time

from TX.MyTransaction import InvocationTransaction,ContractTransaction
from TX.TransactionAttribute import TransactionAttribute, TransactionAttributeUsage
from TX.config import *
from TX.utils import hex_reverse, ToAddresstHash, createTxid, createMultiSigContract, create_opdata, \
    createRSMCContract, createHTLCContract, createVerifyScript, pubkeyToAddress, pubkeyToAddressHash, privtkey_sign, \
    privtKey_to_publicKey, get_neovout_by_address


#RSMC

def createFundingTx(walletSelf,walletOther): #self sign is behind
    '''

    :param walletSelf: dict {
            "pubkey":"",
            "deposit":0,
            "assetId":"0x00000"
    }
    :param walletOhter: dict {
            "pubkey":"",
            "deposit":0,
            "assetId":"0x00000"
    :return:
    '''

    multi_contract = createMultiSigContract(walletSelf["pubkey"],walletOther["pubkey"])
    contractAddress = multi_contract["address"]
    time_stamp = TransactionAttribute(usage=TransactionAttributeUsage.Remark,
                                      data=bytearray.fromhex(hex(int(time.time()))[2:]))

    txAttributes = [time_stamp]

    tx = ContractTransaction()

    walletSelf_vouts=get_neovout_by_address(pubkeyToAddress(walletSelf["pubkey"]),walletSelf["deposit"])
    if not walletSelf_vouts:
        return {"message":"{0} no enough balance".format(pubkeyToAddress(walletSelf["pubkey"]))}

    walletOther_vouts=get_neovout_by_address(pubkeyToAddress(walletOther["pubkey"]),walletOther["deposit"])
    if not walletOther_vouts:
        return {"message":"{0} no enough balance".format(pubkeyToAddress(walletOther["pubkey"]))}

    self_inputs=[tx.createInput(preHash=item[0], preIndex=item[2]) for item in walletSelf_vouts ]
    other_inputs=[tx.createInput(preHash=item[0], preIndex=item[2]) for item in walletOther_vouts ]

    output_to_fundingaddress = tx.createOutput(assetId=walletSelf["assetId"], amount=walletSelf["deposit"]+walletOther["deposit"],
                              address=contractAddress)
    self_inputs_total=0
    other_inputs_total=0
    for item in walletSelf_vouts:
        self_inputs_total+=item[1]
    for item in walletOther_vouts:
        other_inputs_total+=item[1]

    output_to_self= tx.createOutput(assetId=walletSelf["assetId"], amount=self_inputs_total-walletSelf["deposit"],
                              address=pubkeyToAddress(walletSelf["pubkey"])) if self_inputs_total>walletSelf["deposit"] \
                                else None
    output_to_other= tx.createOutput(assetId=walletSelf["assetId"], amount=other_inputs_total-walletOther["deposit"],
                              address=pubkeyToAddress(walletOther["pubkey"])) if other_inputs_total>walletOther["deposit"] \
                                else None
    tx.inputs = self_inputs+other_inputs

    tx.outputs = [item for item in (output_to_fundingaddress,output_to_self,output_to_other) if item]
    tx.Attributes = txAttributes

    return {
        "txData":tx.get_tx_data(),
        "addressFunding":contractAddress,
        "txId": createTxid(tx.get_tx_data()),
        "scriptFunding":multi_contract["script"],
        "witness":"024140{signOther}2321"+walletOther["pubkey"]+"ac"+"4140{signSelf}2321"+walletSelf["pubkey"]+"ac"
        # "witness":"024140{sign1}2321{pubkey1}ac4140{sign2}2321{pubkey2}ac"
    }

def createCTX(addressFunding,balanceSelf,balanceOther,pubkeySelf,pubkeyOther,fundingScript):
    RSMCContract=createRSMCContract(hashSelf=pubkeyToAddressHash(pubkeySelf.strip()),pubkeySelf=pubkeySelf.strip(),
                       hashOther=pubkeyToAddressHash(pubkeyOther.strip()),pubkeyOther=pubkeyOther.strip(),magicTimestamp=time.time())
    time_stamp = TransactionAttribute(usage=TransactionAttributeUsage.Remark,
                                      data=bytearray.fromhex(hex(int(time.time()))[2:]))

    txAttributes = [time_stamp]
    tx = ContractTransaction()

    funding_vouts=get_neovout_by_address(addressFunding,balanceSelf+balanceOther)
    if not funding_vouts:
        return {"message":"{0} no enough balance".format(addressFunding)}



    funding_inputs=[tx.createInput(preHash=item[0], preIndex=item[2]) for item in funding_vouts ]


    output_to_RSMC= tx.createOutput(assetId=walletSelf["assetId"], amount=balanceSelf,address=RSMCContract["address"])
    output_to_other= tx.createOutput(assetId=walletSelf["assetId"], amount=balanceOther,address=pubkeyToAddress(pubkeyOther))
    tx.inputs = funding_inputs

    tx.outputs = [output_to_RSMC,output_to_other]
    tx.Attributes = txAttributes



    return {
        "txData":tx.get_tx_data(),
        "addressRSMC":RSMCContract["address"],
        "scriptRSMC":RSMCContract["script"],
        "txId":createTxid(tx.get_tx_data()),
        "witness":"018240{signSelf}40{signOther}da"+fundingScript
    }

def createRDTX(addressSelf,balanceSelf,CTxId,RSMCScript):

    time_stamp = TransactionAttribute(usage=TransactionAttributeUsage.Remark,
                                      data=bytearray.fromhex(hex(int(time.time()))[2:]))

    pre_txid = TransactionAttribute(usage=TransactionAttributeUsage.Remark1, data=bytearray.fromhex(
        hex_reverse(CTxId)))

    outputTo= TransactionAttribute(usage=TransactionAttributeUsage.Remark2, data=ToAddresstHash(addressSelf).Data)

    txAttributes = [time_stamp,pre_txid,outputTo]

    tx = ContractTransaction()

    RSMC_inputs=[tx.createInput(preHash=CTxId, preIndex=0)]


    output_to_self= tx.createOutput(assetId=walletSelf["assetId"], amount=balanceSelf,address=addressSelf)
    tx.inputs = RSMC_inputs

    tx.outputs = [output_to_self]
    tx.Attributes = txAttributes




    return {
        "txData":tx.get_tx_data(),
        "txId":createTxid(tx.get_tx_data()),
        "witness":"01{blockheight_script}40{signOther}40{signSelf}fd"+createVerifyScript(RSMCScript)
    }

def createBRTX(addressOther,balanceSelf,RSMCScript,CTxId):

    time_stamp = TransactionAttribute(usage=TransactionAttributeUsage.Remark,
                                      data=bytearray.fromhex(hex(int(time.time()))[2:]))

    outputTo = TransactionAttribute(usage=TransactionAttributeUsage.Remark1, data=ToAddresstHash(addressOther).Data)
    txAttributes = [time_stamp,outputTo]

    tx = ContractTransaction()

    RSMC_inputs=[tx.createInput(preHash=CTxId, preIndex=0)]


    output_to_other= tx.createOutput(assetId=walletSelf["assetId"], amount=balanceSelf,address=addressOther)
    tx.inputs = RSMC_inputs

    tx.outputs = [output_to_other]

    tx.Attributes = txAttributes


    return {
        "txData":tx.get_tx_data(),
        "txId":createTxid(tx.get_tx_data()),
        "witness": "01{blockheight_script}40{signOther}40{signSelf}fd" + createVerifyScript(RSMCScript)
    }

def createRefundTX(addressFunding,balanceSelf,balanceOther,pubkeySelf,pubkeyOther,fundingScript):

    time_stamp = TransactionAttribute(usage=TransactionAttributeUsage.Remark,
                                      data=bytearray.fromhex(hex(int(time.time()))[2:]))

    txAttributes = [time_stamp]
    tx = ContractTransaction()

    funding_vouts=get_neovout_by_address(addressFunding,balanceSelf+balanceOther)
    if not funding_vouts:
        return {"message":"{0} no enough balance".format(addressFunding)}



    funding_inputs=[tx.createInput(preHash=item[0], preIndex=item[2]) for item in funding_vouts ]


    output_to_self= tx.createOutput(assetId=walletSelf["assetId"], amount=balanceSelf,address=pubkeyToAddress(pubkeySelf))
    output_to_other= tx.createOutput(assetId=walletSelf["assetId"], amount=balanceOther,address=pubkeyToAddress(pubkeyOther))
    tx.inputs = funding_inputs

    tx.outputs = [output_to_self,output_to_other]
    tx.Attributes = txAttributes


    return {
        "txData":tx.get_tx_data(),
        "txId":createTxid(tx.get_tx_data()),
        "witness":"018240{signSelf}40{signOther}da"+fundingScript
    }

#sender HTLC
def create_sender_HCTX(pubkeySender, pubkeyReceiver, HTLCValue, balanceSender, balanceReceiver, hashR,
                   addressFunding, fundingScript):
    RSMCContract = createRSMCContract(hashSelf=pubkeyToAddressHash(pubkeySender), pubkeySelf=pubkeySender,
                                      hashOther=pubkeyToAddressHash(pubkeyReceiver), pubkeyOther=pubkeyReceiver,
                                      magicTimestamp=time.time())

    HTLCContract = createHTLCContract(pubkeySelf=pubkeySender, pubkeyOther=pubkeyReceiver,
                                      futureTimestamp=int(time.time()) + 600,
                                      hashR=hashR)
    time_stamp = TransactionAttribute(usage=TransactionAttributeUsage.Remark,
                                      data=bytearray.fromhex(hex(int(time.time()))[2:]))


    txAttributes = [time_stamp]
    tx = ContractTransaction()

    funding_vouts=get_neovout_by_address(addressFunding,balanceSender+balanceReceiver+HTLCValue)
    if not funding_vouts:
        return {"message":"{0} no enough balance".format(addressFunding)}

    funding_inputs=[tx.createInput(preHash=item[0], preIndex=item[2]) for item in funding_vouts ]

    output_to_RSMC= tx.createOutput(assetId=walletSelf["assetId"], amount=balanceSender,address=RSMCContract["address"])
    output_to_HTLC= tx.createOutput(assetId=walletSelf["assetId"], amount=HTLCValue,address=HTLCContract["address"])
    output_to_receiver= tx.createOutput(assetId=walletSelf["assetId"], amount=balanceReceiver,address=pubkeyToAddress(pubkeyReceiver))

    tx.inputs = funding_inputs
    tx.outputs = [output_to_RSMC,output_to_receiver,output_to_HTLC]
    tx.Attributes = txAttributes



    return {
        "txData": tx.get_tx_data(),
        "addressRSMC": RSMCContract["address"],
        "addressHTLC": HTLCContract["address"],
        "RSMCscript": RSMCContract["script"],
        "HTLCscript": HTLCContract["script"],
        "txId": createTxid(tx.get_tx_data()),
        "witness": "018240{signSelf}40{signOther}da" + fundingScript
    }

def create_sender_RDTX(addressSender, balanceSender, senderHCTxId, RSMCScript):
    time_stamp = TransactionAttribute(usage=TransactionAttributeUsage.Remark,
                                      data=bytearray.fromhex(hex(int(time.time()))[2:]))

    pre_txid = TransactionAttribute(usage=TransactionAttributeUsage.Remark1, data=bytearray.fromhex(
        hex_reverse(senderHCTxId)))

    outputTo = TransactionAttribute(usage=TransactionAttributeUsage.Remark2, data=ToAddresstHash(addressSender).Data)

    txAttributes = [time_stamp,pre_txid,outputTo]

    tx = ContractTransaction()

    output_to_sender= tx.createOutput(assetId=walletSelf["assetId"], amount=balanceSender,address=addressSender)

    RSMC_inputs=[tx.createInput(preHash=senderHCTxId, preIndex=0)]
    tx.inputs = RSMC_inputs
    tx.outputs = [output_to_sender]
    tx.Attributes = txAttributes

    return {
        "txData": tx.get_tx_data(),
        "txId": createTxid(tx.get_tx_data()),
        "witness": "01{blockheight_script}40{signReceiver}40{signSender}fd"+createVerifyScript(RSMCScript)
    }

def createHEDTX(addressReceiver, HTLCValue, HTLCScript,senderHCTxId):
    time_stamp = TransactionAttribute(usage=TransactionAttributeUsage.Remark,
                                      data=bytearray.fromhex(hex(int(time.time()))[2:]))

    txAttributes = [time_stamp]
    tx = ContractTransaction()


    HTLC_inputs = [tx.createInput(preHash=senderHCTxId, preIndex=2)]
    output_to_receiver = tx.createOutput(assetId=walletSelf["assetId"], amount=HTLCValue, address=addressReceiver)

    tx.inputs = HTLC_inputs
    tx.outputs = [output_to_receiver]
    tx.Attributes = txAttributes


    return {
        "txData": tx.get_tx_data(),
        "txId": createTxid(tx.get_tx_data()),
        "witness": "01{R_script}40{signOther}40{signSelf}fd"+createVerifyScript(HTLCScript)
    }

def createHTTX(pubkeySender, pubkeyReceiver, HTLCValue, HTLCScript,senderHCTxId):
    RSMCContract = createRSMCContract(hashSelf=pubkeyToAddressHash(pubkeySender), pubkeySelf=pubkeySender,
                                      hashOther=pubkeyToAddressHash(pubkeyReceiver), pubkeyOther=pubkeyReceiver,
                                      magicTimestamp=time.time())

    time_stamp = TransactionAttribute(usage=TransactionAttributeUsage.Remark,
                                      data=bytearray.fromhex(hex(int(time.time()))[2:]))

    txAttributes = [time_stamp]
    tx = ContractTransaction()

    HTLC_inputs = [tx.createInput(preHash=senderHCTxId, preIndex=2)]
    output_to_RSMC = tx.createOutput(assetId=walletSelf["assetId"], amount=HTLCValue, address=RSMCContract["address"])

    tx.inputs = HTLC_inputs
    tx.outputs = [output_to_RSMC]
    tx.Attributes = txAttributes

    return {
        "txData": tx.get_tx_data(),
        "txId": createTxid(tx.get_tx_data()),
        "addressRSMC": RSMCContract["address"],
        "RSMCscript": RSMCContract["script"],
        "witness": "01830040{signOther}40{signSelf}fd"+createVerifyScript(HTLCScript) #R is empty
    }

def createHTRDTX(addressSender, HTLCValue, HTTxId, RSMCScript):
    time_stamp = TransactionAttribute(usage=TransactionAttributeUsage.Remark,
                                      data=bytearray.fromhex(hex(int(time.time()))[2:]))

    pre_txid = TransactionAttribute(usage=TransactionAttributeUsage.Remark1, data=bytearray.fromhex(
        hex_reverse(HTTxId)))

    outputTo = TransactionAttribute(usage=TransactionAttributeUsage.Remark2, data=ToAddresstHash(addressSender).Data)


    txAttributes = [time_stamp, pre_txid, outputTo]

    tx = ContractTransaction()

    RSMC_inputs = [tx.createInput(preHash=HTTxId, preIndex=0)]
    output_to_sender = tx.createOutput(assetId=walletSelf["assetId"], amount=HTLCValue, address=addressSender)

    tx.inputs = RSMC_inputs
    tx.outputs = [output_to_sender]
    tx.Attributes = txAttributes

    return {
        "txData": tx.get_tx_data(),
        "txId": createTxid(tx.get_tx_data()),
        "witness": "01{blockheight_script}40{signReceiver}40{signSender}fd"+createVerifyScript(RSMCScript)
    }


#receiver HTLC
def create_receiver_HCTX(pubkeySender, pubkeyReceiver, HTLCValue, balanceSender, balanceReceiver, hashR, addressFunding,
                    fundingScript):
    RSMCContract = createRSMCContract(hashSelf=pubkeyToAddressHash(pubkeyReceiver), pubkeySelf=pubkeyReceiver,
                                      hashOther=pubkeyToAddressHash(pubkeySender), pubkeyOther=pubkeySender,
                                      magicTimestamp=time.time())

    HTLCContract = createHTLCContract(pubkeySelf=pubkeyReceiver, pubkeyOther=pubkeySender,
                                      futureTimestamp=int(time.time()) + 600,
                                      hashR=hashR)
    time_stamp = TransactionAttribute(usage=TransactionAttributeUsage.Remark,
                                      data=bytearray.fromhex(hex(int(time.time()))[2:]))

    txAttributes = [time_stamp]
    tx = ContractTransaction()

    funding_vouts = get_neovout_by_address(addressFunding, balanceSender + balanceReceiver + HTLCValue)
    if not funding_vouts:
        return {"message": "{0} no enough balance".format(addressFunding)}

    funding_inputs = [tx.createInput(preHash=item[0], preIndex=item[2]) for item in funding_vouts]

    output_to_RSMC = tx.createOutput(assetId=walletSelf["assetId"], amount=balanceReceiver, address=RSMCContract["address"])
    output_to_HTLC = tx.createOutput(assetId=walletSelf["assetId"], amount=HTLCValue, address=HTLCContract["address"])
    output_to_sender = tx.createOutput(assetId=walletSelf["assetId"], amount=balanceSender, address=pubkeyToAddress(pubkeySender))

    tx.inputs = funding_inputs
    tx.outputs = [output_to_RSMC, output_to_sender, output_to_HTLC]
    tx.Attributes = txAttributes


    return {
        "txData": tx.get_tx_data(),
        "addressRSMC": RSMCContract["address"],
        "addressHTLC": HTLCContract["address"],
        "RSMCscript": RSMCContract["script"],
        "HTLCscript": HTLCContract["script"],
        "txId": createTxid(tx.get_tx_data()),
        "witness": "018240{signSelf}40{signOther}da" + fundingScript
    }

def create_receiver_RDTX(addressReceiver, balanceReceiver, receiver_HCTxId, RSMCScript):
    time_stamp = TransactionAttribute(usage=TransactionAttributeUsage.Remark,
                                      data=bytearray.fromhex(hex(int(time.time()))[2:]))

    pre_txid = TransactionAttribute(usage=TransactionAttributeUsage.Remark1, data=bytearray.fromhex(
        hex_reverse(receiver_HCTxId)))

    outputTo = TransactionAttribute(usage=TransactionAttributeUsage.Remark2, data=ToAddresstHash(addressReceiver).Data)

    txAttributes = [time_stamp, pre_txid, outputTo]

    tx = ContractTransaction()

    RSMC_inputs = [tx.createInput(preHash=receiver_HCTxId, preIndex=0)]
    output_to_receiver = tx.createOutput(assetId=walletSelf["assetId"], amount=balanceReceiver, address=addressReceiver)

    tx.inputs = RSMC_inputs
    tx.outputs = [output_to_receiver]
    tx.Attributes = txAttributes

    return {
        "txData": tx.get_tx_data(),
        "txId": createTxid(tx.get_tx_data()),
        "witness": "01{blockheight_script}40{signOther}40{signSelf}fd"+createVerifyScript(RSMCScript)
    }

def createHTDTX(pubkeySender,HTLCValue, HTLCScript,receiver_HCTxId):

    time_stamp = TransactionAttribute(usage=TransactionAttributeUsage.Remark,
                                      data=bytearray.fromhex(hex(int(time.time()))[2:]))

    txAttributes = [time_stamp]
    tx = ContractTransaction()

    HTLC_inputs = [tx.createInput(preHash=receiver_HCTxId, preIndex=2)]
    output_to_sender = tx.createOutput(assetId=walletSelf["assetId"], amount=HTLCValue, address=pubkeyToAddress(pubkeySender))

    tx.inputs = HTLC_inputs
    tx.outputs = [output_to_sender]
    tx.Attributes = txAttributes

    return {
        "txData": tx.get_tx_data(),
        "txId": createTxid(tx.get_tx_data()),
        "witness": "01830040{signOther}40{signSelf}fd"+createVerifyScript(HTLCScript) #R is empty
    }

def createHETX(pubkeySender,pubkeyReceiver,HTLCValue, HTLCScript,receiver_HCTxId):
    RSMCContract = createRSMCContract(hashSelf=pubkeyToAddressHash(pubkeyReceiver), pubkeySelf=pubkeyReceiver,
                                      hashOther=pubkeyToAddressHash(pubkeySender), pubkeyOther=pubkeySender,
                                      magicTimestamp=time.time())

    time_stamp = TransactionAttribute(usage=TransactionAttributeUsage.Remark,
                                      data=bytearray.fromhex(hex(int(time.time()))[2:]))
    txAttributes = [time_stamp]
    tx = ContractTransaction()

    HTLC_inputs = [tx.createInput(preHash=receiver_HCTxId, preIndex=2)]
    output_to_RSMC = tx.createOutput(assetId=walletSelf["assetId"], amount=HTLCValue, address=RSMCContract["address"])

    tx.inputs = HTLC_inputs
    tx.outputs = [output_to_RSMC]
    tx.Attributes = txAttributes



    return {
        "txData": tx.get_tx_data(),
        "txId": createTxid(tx.get_tx_data()),
        "addressRSMC": RSMCContract["address"],
        "RSMCscript": RSMCContract["script"],
        "witness": "01{R_script}40{signOther}40{signSelf}fd"+createVerifyScript(HTLCScript)
    }

def createHERDTX(addressReceiver, HTLCValue, HETxId, RSMCScript):
    time_stamp = TransactionAttribute(usage=TransactionAttributeUsage.Remark,
                                      data=bytearray.fromhex(hex(int(time.time()))[2:]))

    pre_txid = TransactionAttribute(usage=TransactionAttributeUsage.Remark1, data=bytearray.fromhex(
        hex_reverse(HETxId)))

    outputTo = TransactionAttribute(usage=TransactionAttributeUsage.Remark2, data=ToAddresstHash(addressReceiver).Data)

    txAttributes = [time_stamp, pre_txid, outputTo]


    tx = ContractTransaction()



    RSMC_inputs = [tx.createInput(preHash=HETxId, preIndex=0)]
    output_to_receiver = tx.createOutput(assetId=walletSelf["assetId"], amount=HTLCValue, address=addressReceiver)

    tx.inputs = RSMC_inputs
    tx.outputs = [output_to_receiver]
    tx.Attributes = txAttributes

    return {
        "txData": tx.get_tx_data(),
        "txId": createTxid(tx.get_tx_data()),
        "witness": "01{blockheight_script}40{signReceiver}40{signSender}fd"+createVerifyScript(RSMCScript)
    }



def create_sender_HTLC_TXS(pubkeySender, pubkeyReceiver, HTLCValue, balanceSender,
                           balanceReceiver, hashR, addressFunding, fundingScript):
    sender_HCTX = create_sender_HCTX(pubkeySender=pubkeySender, pubkeyReceiver=pubkeyReceiver,
                                     HTLCValue=HTLCValue, balanceSender=balanceSender,
                                     balanceReceiver=balanceReceiver, hashR=hashR,
                                     addressFunding=addressFunding, fundingScript=fundingScript)

    sender_RDTX = create_sender_RDTX(addressRSMC=sender_HCTX["addressRSMC"], addressSender=pubkeyToAddress(pubkeySender),
                                     balanceSender=balanceSender, senderHCTxId=sender_HCTX["txId"],
                                     RSMCScript=sender_HCTX["RSMCscript"])

    HEDTX = createHEDTX(addressReceiver=pubkeyToAddress(pubkeyReceiver),
                        HTLCValue=HTLCValue, HTLCScript=sender_HCTX["HTLCscript"],senderHCTxId=sender_HCTX["txId"])

    HTTX = createHTTX(pubkeySender=pubkeySender,
                      pubkeyReceiver=pubkeyReceiver, HTLCValue=HTLCValue,
                      HTLCScript=sender_HCTX["HTLCscript"],senderHCTxId=sender_HCTX["txId"])

    HTRDTX = createHTRDTX(addressSender=pubkeyToAddress(pubkeySender),
                          HTLCValue=HTLCValue, HTTxId=HTTX["txId"], RSMCScript=HTTX["RSMCscript"])

    return {
        "HCTX":sender_HCTX,
        "RDTX":sender_RDTX,
        "HEDTX":HEDTX,
        "HTTX":HTTX,
        "HTRDTX":HTRDTX
    }


def create_receiver_HTLC_TXS(pubkeySender, pubkeyReceiver, HTLCValue, balanceSender,
                           balanceReceiver, hashR, addressFunding, fundingScript):
    receiver_HCTX = create_receiver_HCTX(pubkeySender=pubkeySender, pubkeyReceiver=pubkeyReceiver,
                                     HTLCValue=HTLCValue, balanceSender=balanceSender,
                                     balanceReceiver=balanceReceiver, hashR=hashR,
                                     addressFunding=addressFunding, fundingScript=fundingScript)

    receiver_RDTX = create_receiver_RDTX(addressReceiver=pubkeyToAddress(pubkeyReceiver),
                                         balanceReceiver=balanceReceiver, receiver_HCTxId=receiver_HCTX["txId"],
                                         RSMCScript=receiver_HCTX["RSMCscript"])

    HTDTX = createHTDTX(pubkeySender=pubkeySender,HTLCValue=HTLCValue, HTLCScript=receiver_HCTX["HTLCscript"],
                        receiver_HCTxId=receiver_HCTX["txId"])

    HETX = createHETX(pubkeySender=pubkeySender,
                      pubkeyReceiver=pubkeyReceiver, HTLCValue=HTLCValue,
                      HTLCScript=receiver_HCTX["HTLCscript"],receiver_HCTxId=receiver_HCTX["txId"])

    HERDTX = createHERDTX(addressReceiver=pubkeyToAddress(pubkeyReceiver),
                          HTLCValue=HTLCValue, HETxId=HETX["txId"], RSMCScript=HETX["RSMCscript"])

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





