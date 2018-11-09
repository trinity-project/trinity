import time

from TX.MyTransaction import ContractTransaction
from TX.TransactionAttribute import TransactionAttribute, TransactionAttributeUsage
from TX.utils import hex_reverse, ToAddresstHash, createTxid, createMultiSigContract,  \
    createRSMCContract, createHTLCContract, createVerifyScript, pubkeyToAddress, pubkeyToAddressHash, \
    get_gasvout_by_address


#RSMC

def createFundingTx(walletSelf,walletOther,asset_id):
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

    walletSelf_vouts=get_gasvout_by_address(pubkeyToAddress(walletSelf["pubkey"]),walletSelf["deposit"])
    if not walletSelf_vouts:
        return {"message":"{0} no enough balance".format(pubkeyToAddress(walletSelf["pubkey"]))}

    walletOther_vouts=get_gasvout_by_address(pubkeyToAddress(walletOther["pubkey"]),walletOther["deposit"])
    if not walletOther_vouts:
        return {"message":"{0} no enough balance".format(pubkeyToAddress(walletOther["pubkey"]))}

    self_inputs=[tx.createInput(preHash=item[0], preIndex=item[2]) for item in walletSelf_vouts ]
    other_inputs=[tx.createInput(preHash=item[0], preIndex=item[2]) for item in walletOther_vouts ]

    output_to_fundingaddress = tx.createOutput(assetId=asset_id, amount=walletSelf["deposit"]+walletOther["deposit"],
                              address=contractAddress)
    self_inputs_total=0
    other_inputs_total=0
    for item in walletSelf_vouts:
        self_inputs_total+=item[1]
    for item in walletOther_vouts:
        other_inputs_total+=item[1]

    output_to_self= tx.createOutput(assetId=asset_id, amount=self_inputs_total-walletSelf["deposit"],
                              address=pubkeyToAddress(walletSelf["pubkey"])) if self_inputs_total>walletSelf["deposit"] \
                                else None
    output_to_other= tx.createOutput(assetId=asset_id, amount=other_inputs_total-walletOther["deposit"],
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

def createCTX(balanceSelf,balanceOther,pubkeySelf,pubkeyOther,fundingScript,asset_id,fundingTxId):
    RSMCContract=createRSMCContract(hashSelf=pubkeyToAddressHash(pubkeySelf.strip()),pubkeySelf=pubkeySelf.strip(),
                                    hashOther=pubkeyToAddressHash(pubkeyOther.strip()),
                                    pubkeyOther=pubkeyOther.strip(),magicTimestamp=time.time())
    time_stamp = TransactionAttribute(usage=TransactionAttributeUsage.Remark,
                                      data=bytearray.fromhex(hex(int(time.time()))[2:]))

    txAttributes = [time_stamp]
    tx = ContractTransaction()

    funding_inputs=[tx.createInput(preHash=fundingTxId, preIndex=0)]


    output_to_RSMC= tx.createOutput(assetId=asset_id, amount=balanceSelf,address=RSMCContract["address"])
    output_to_other= tx.createOutput(assetId=asset_id, amount=balanceOther,address=pubkeyToAddress(pubkeyOther))
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

def createRDTX(addressSelf,balanceSelf,CTxId,RSMCScript,asset_id):

    time_stamp = TransactionAttribute(usage=TransactionAttributeUsage.Remark,
                                      data=bytearray.fromhex(hex(int(time.time()))[2:]))

    pre_txid = TransactionAttribute(usage=TransactionAttributeUsage.Remark1, data=bytearray.fromhex(
        hex_reverse(CTxId)))

    outputTo= TransactionAttribute(usage=TransactionAttributeUsage.Remark2, data=ToAddresstHash(addressSelf).Data)

    txAttributes = [time_stamp,pre_txid,outputTo]

    tx = ContractTransaction()

    RSMC_inputs=[tx.createInput(preHash=CTxId, preIndex=0)]


    output_to_self= tx.createOutput(assetId=asset_id, amount=balanceSelf,address=addressSelf)
    tx.inputs = RSMC_inputs

    tx.outputs = [output_to_self]
    tx.Attributes = txAttributes




    return {
        "txData":tx.get_tx_data(),
        "txId":createTxid(tx.get_tx_data()),
        "witness":"01{blockheight_script}40{signOther}40{signSelf}fd"+createVerifyScript(RSMCScript)
    }

def createBRTX(addressOther,balanceSelf,RSMCScript,CTxId,asset_id):

    time_stamp = TransactionAttribute(usage=TransactionAttributeUsage.Remark,
                                      data=bytearray.fromhex(hex(int(time.time()))[2:]))

    outputTo = TransactionAttribute(usage=TransactionAttributeUsage.Remark1, data=ToAddresstHash(addressOther).Data)
    txAttributes = [time_stamp,outputTo]

    tx = ContractTransaction()

    RSMC_inputs=[tx.createInput(preHash=CTxId, preIndex=0)]


    output_to_other= tx.createOutput(assetId=asset_id, amount=balanceSelf,address=addressOther)
    tx.inputs = RSMC_inputs

    tx.outputs = [output_to_other]

    tx.Attributes = txAttributes


    return {
        "txData":tx.get_tx_data(),
        "txId":createTxid(tx.get_tx_data()),
        "witness": "01{blockheight_script}40{signOther}40{signSelf}fd" + createVerifyScript(RSMCScript)
    }

def createRefundTX(addressFunding,balanceSelf,balanceOther,pubkeySelf,pubkeyOther,fundingScript,asset_id):

    time_stamp = TransactionAttribute(usage=TransactionAttributeUsage.Remark,
                                      data=bytearray.fromhex(hex(int(time.time()))[2:]))

    txAttributes = [time_stamp]
    tx = ContractTransaction()

    funding_vouts=get_gasvout_by_address(addressFunding,balanceSelf+balanceOther)
    if not funding_vouts:
        return {"message":"{0} no enough balance".format(addressFunding)}



    funding_inputs=[tx.createInput(preHash=item[0], preIndex=item[2]) for item in funding_vouts ]


    output_to_self= tx.createOutput(assetId=asset_id, amount=balanceSelf,address=pubkeyToAddress(pubkeySelf))
    output_to_other= tx.createOutput(assetId=asset_id, amount=balanceOther,address=pubkeyToAddress(pubkeyOther))
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
                   addressFunding, fundingScript,asset_id):
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

    funding_vouts=get_gasvout_by_address(addressFunding,balanceSender+balanceReceiver+HTLCValue)
    if not funding_vouts:
        return {"message":"{0} no enough balance".format(addressFunding)}

    funding_inputs=[tx.createInput(preHash=item[0], preIndex=item[2]) for item in funding_vouts ]

    output_to_RSMC= tx.createOutput(assetId=asset_id, amount=balanceSender,address=RSMCContract["address"])
    output_to_HTLC= tx.createOutput(assetId=asset_id, amount=HTLCValue,address=HTLCContract["address"])
    output_to_receiver= tx.createOutput(assetId=asset_id,
                                        amount=balanceReceiver,address=pubkeyToAddress(pubkeyReceiver))

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

def create_sender_RDTX(addressSender, balanceSender, senderHCTxId, RSMCScript,asset_id):
    time_stamp = TransactionAttribute(usage=TransactionAttributeUsage.Remark,
                                      data=bytearray.fromhex(hex(int(time.time()))[2:]))

    pre_txid = TransactionAttribute(usage=TransactionAttributeUsage.Remark1, data=bytearray.fromhex(
        hex_reverse(senderHCTxId)))

    outputTo = TransactionAttribute(usage=TransactionAttributeUsage.Remark2, data=ToAddresstHash(addressSender).Data)

    txAttributes = [time_stamp,pre_txid,outputTo]

    tx = ContractTransaction()

    output_to_sender= tx.createOutput(assetId=asset_id, amount=balanceSender,address=addressSender)

    RSMC_inputs=[tx.createInput(preHash=senderHCTxId, preIndex=0)]
    tx.inputs = RSMC_inputs
    tx.outputs = [output_to_sender]
    tx.Attributes = txAttributes

    return {
        "txData": tx.get_tx_data(),
        "txId": createTxid(tx.get_tx_data()),
        "witness": "01{blockheight_script}40{signReceiver}40{signSender}fd"+createVerifyScript(RSMCScript)
    }

def createHEDTX(addressReceiver, HTLCValue, HTLCScript,senderHCTxId,asset_id):
    time_stamp = TransactionAttribute(usage=TransactionAttributeUsage.Remark,
                                      data=bytearray.fromhex(hex(int(time.time()))[2:]))

    txAttributes = [time_stamp]
    tx = ContractTransaction()


    HTLC_inputs = [tx.createInput(preHash=senderHCTxId, preIndex=2)]
    output_to_receiver = tx.createOutput(assetId=asset_id, amount=HTLCValue, address=addressReceiver)

    tx.inputs = HTLC_inputs
    tx.outputs = [output_to_receiver]
    tx.Attributes = txAttributes


    return {
        "txData": tx.get_tx_data(),
        "txId": createTxid(tx.get_tx_data()),
        "witness": "01{R_script}40{signOther}40{signSelf}fd"+createVerifyScript(HTLCScript)
    }

def createHTTX(pubkeySender, pubkeyReceiver, HTLCValue, HTLCScript,senderHCTxId,asset_id):
    RSMCContract = createRSMCContract(hashSelf=pubkeyToAddressHash(pubkeySender), pubkeySelf=pubkeySender,
                                      hashOther=pubkeyToAddressHash(pubkeyReceiver), pubkeyOther=pubkeyReceiver,
                                      magicTimestamp=time.time())

    time_stamp = TransactionAttribute(usage=TransactionAttributeUsage.Remark,
                                      data=bytearray.fromhex(hex(int(time.time()))[2:]))

    txAttributes = [time_stamp]
    tx = ContractTransaction()

    HTLC_inputs = [tx.createInput(preHash=senderHCTxId, preIndex=2)]
    output_to_RSMC = tx.createOutput(assetId=asset_id, amount=HTLCValue, address=RSMCContract["address"])

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

def createHTRDTX(addressSender, HTLCValue, HTTxId, RSMCScript,asset_id):
    time_stamp = TransactionAttribute(usage=TransactionAttributeUsage.Remark,
                                      data=bytearray.fromhex(hex(int(time.time()))[2:]))

    pre_txid = TransactionAttribute(usage=TransactionAttributeUsage.Remark1, data=bytearray.fromhex(
        hex_reverse(HTTxId)))

    outputTo = TransactionAttribute(usage=TransactionAttributeUsage.Remark2, data=ToAddresstHash(addressSender).Data)


    txAttributes = [time_stamp, pre_txid, outputTo]

    tx = ContractTransaction()

    RSMC_inputs = [tx.createInput(preHash=HTTxId, preIndex=0)]
    output_to_sender = tx.createOutput(assetId=asset_id, amount=HTLCValue, address=addressSender)

    tx.inputs = RSMC_inputs
    tx.outputs = [output_to_sender]
    tx.Attributes = txAttributes

    return {
        "txData": tx.get_tx_data(),
        "txId": createTxid(tx.get_tx_data()),
        "witness": "01{blockheight_script}40{signReceiver}40{signSender}fd"+createVerifyScript(RSMCScript)
    }


#receiver HTLC
def create_receiver_HCTX(pubkeySender, pubkeyReceiver, HTLCValue, balanceSender,
                         balanceReceiver, hashR, addressFunding,fundingScript,asset_id):
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

    funding_vouts = get_gasvout_by_address(addressFunding, balanceSender + balanceReceiver + HTLCValue)
    if not funding_vouts:
        return {"message": "{0} no enough balance".format(addressFunding)}

    funding_inputs = [tx.createInput(preHash=item[0], preIndex=item[2]) for item in funding_vouts]

    output_to_RSMC = tx.createOutput(assetId=asset_id, amount=balanceReceiver, address=RSMCContract["address"])
    output_to_HTLC = tx.createOutput(assetId=asset_id, amount=HTLCValue, address=HTLCContract["address"])
    output_to_sender = tx.createOutput(assetId=asset_id, amount=balanceSender, address=pubkeyToAddress(pubkeySender))

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

def create_receiver_RDTX(addressReceiver, balanceReceiver, receiver_HCTxId, RSMCScript,asset_id):
    time_stamp = TransactionAttribute(usage=TransactionAttributeUsage.Remark,
                                      data=bytearray.fromhex(hex(int(time.time()))[2:]))

    pre_txid = TransactionAttribute(usage=TransactionAttributeUsage.Remark1, data=bytearray.fromhex(
        hex_reverse(receiver_HCTxId)))

    outputTo = TransactionAttribute(usage=TransactionAttributeUsage.Remark2,
                                    data=ToAddresstHash(addressReceiver).Data)

    txAttributes = [time_stamp, pre_txid, outputTo]

    tx = ContractTransaction()

    RSMC_inputs = [tx.createInput(preHash=receiver_HCTxId, preIndex=0)]
    output_to_receiver = tx.createOutput(assetId=asset_id, amount=balanceReceiver, address=addressReceiver)

    tx.inputs = RSMC_inputs
    tx.outputs = [output_to_receiver]
    tx.Attributes = txAttributes

    return {
        "txData": tx.get_tx_data(),
        "txId": createTxid(tx.get_tx_data()),
        "witness": "01{blockheight_script}40{signOther}40{signSelf}fd"+createVerifyScript(RSMCScript)
    }

def createHTDTX(pubkeySender,HTLCValue, HTLCScript,receiver_HCTxId,asset_id):

    time_stamp = TransactionAttribute(usage=TransactionAttributeUsage.Remark,
                                      data=bytearray.fromhex(hex(int(time.time()))[2:]))

    txAttributes = [time_stamp]
    tx = ContractTransaction()

    HTLC_inputs = [tx.createInput(preHash=receiver_HCTxId, preIndex=2)]
    output_to_sender = tx.createOutput(assetId=asset_id, amount=HTLCValue, address=pubkeyToAddress(pubkeySender))

    tx.inputs = HTLC_inputs
    tx.outputs = [output_to_sender]
    tx.Attributes = txAttributes

    return {
        "txData": tx.get_tx_data(),
        "txId": createTxid(tx.get_tx_data()),
        "witness": "01830040{signOther}40{signSelf}fd"+createVerifyScript(HTLCScript) #R is empty
    }

def createHETX(pubkeySender,pubkeyReceiver,HTLCValue, HTLCScript,receiver_HCTxId,asset_id):
    RSMCContract = createRSMCContract(hashSelf=pubkeyToAddressHash(pubkeyReceiver), pubkeySelf=pubkeyReceiver,
                                      hashOther=pubkeyToAddressHash(pubkeySender), pubkeyOther=pubkeySender,
                                      magicTimestamp=time.time())

    time_stamp = TransactionAttribute(usage=TransactionAttributeUsage.Remark,
                                      data=bytearray.fromhex(hex(int(time.time()))[2:]))
    txAttributes = [time_stamp]
    tx = ContractTransaction()

    HTLC_inputs = [tx.createInput(preHash=receiver_HCTxId, preIndex=2)]
    output_to_RSMC = tx.createOutput(assetId=asset_id, amount=HTLCValue, address=RSMCContract["address"])

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

def createHERDTX(addressReceiver, HTLCValue, HETxId, RSMCScript,asset_id):
    time_stamp = TransactionAttribute(usage=TransactionAttributeUsage.Remark,
                                      data=bytearray.fromhex(hex(int(time.time()))[2:]))

    pre_txid = TransactionAttribute(usage=TransactionAttributeUsage.Remark1, data=bytearray.fromhex(
        hex_reverse(HETxId)))

    outputTo = TransactionAttribute(usage=TransactionAttributeUsage.Remark2,
                                    data=ToAddresstHash(addressReceiver).Data)

    txAttributes = [time_stamp, pre_txid, outputTo]


    tx = ContractTransaction()



    RSMC_inputs = [tx.createInput(preHash=HETxId, preIndex=0)]
    output_to_receiver = tx.createOutput(assetId=asset_id, amount=HTLCValue, address=addressReceiver)

    tx.inputs = RSMC_inputs
    tx.outputs = [output_to_receiver]
    tx.Attributes = txAttributes

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
                                     addressFunding=addressFunding, fundingScript=fundingScript,asset_id=asset_id)

    sender_RDTX = create_sender_RDTX(addressSender=pubkeyToAddress(pubkeySender),
                                     balanceSender=balanceSender, senderHCTxId=sender_HCTX["txId"],
                                     RSMCScript=sender_HCTX["RSMCscript"],asset_id=asset_id)

    HEDTX = createHEDTX(addressReceiver=pubkeyToAddress(pubkeyReceiver),
                        HTLCValue=HTLCValue, HTLCScript=sender_HCTX["HTLCscript"],
                        senderHCTxId=sender_HCTX["txId"],asset_id=asset_id)

    HTTX = createHTTX(pubkeySender=pubkeySender,
                      pubkeyReceiver=pubkeyReceiver, HTLCValue=HTLCValue,
                      HTLCScript=sender_HCTX["HTLCscript"],senderHCTxId=sender_HCTX["txId"],asset_id=asset_id)

    HTRDTX = createHTRDTX(addressSender=pubkeyToAddress(pubkeySender),
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

    receiver_RDTX = create_receiver_RDTX(addressReceiver=pubkeyToAddress(pubkeyReceiver),
                                         balanceReceiver=balanceReceiver, receiver_HCTxId=receiver_HCTX["txId"],
                                         RSMCScript=receiver_HCTX["RSMCscript"],asset_id=asset_id)

    HTDTX = createHTDTX(pubkeySender=pubkeySender,HTLCValue=HTLCValue, HTLCScript=receiver_HCTX["HTLCscript"],
                        receiver_HCTxId=receiver_HCTX["txId"],asset_id=asset_id)

    HETX = createHETX(pubkeySender=pubkeySender,
                      pubkeyReceiver=pubkeyReceiver, HTLCValue=HTLCValue,
                      HTLCScript=receiver_HCTX["HTLCscript"],receiver_HCTxId=receiver_HCTX["txId"],asset_id=asset_id)

    HERDTX = createHERDTX(addressReceiver=pubkeyToAddress(pubkeyReceiver),
                          HTLCValue=HTLCValue, HETxId=HETX["txId"], RSMCScript=HETX["RSMCscript"],asset_id=asset_id)

    return {
        "HCTX": receiver_HCTX,
        "RDTX": receiver_RDTX,
        "HTDTX": HTDTX,
        "HETX": HETX,
        "HERDTX": HERDTX
    }






