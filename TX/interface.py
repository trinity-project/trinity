
from TX.adapter import tnc_factory, neo_factory, gas_factory
from TX.config import *




# RSMC

def createFundingTx(walletSelf, walletOther, asset_id):

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

    if asset_id in [TNC, TESTNET_TNC, MAINNET_TNC]:
        return tnc_factory.createFundingTx(walletSelf, walletOther, asset_id)

    elif asset_id == NEO:
        return neo_factory.createFundingTx(walletSelf, walletOther, asset_id)

    elif asset_id == GAS:
        return gas_factory.createFundingTx(walletSelf, walletOther, asset_id)


def createCTX(
        addressFunding,
        balanceSelf,
        balanceOther,
        pubkeySelf,
        pubkeyOther,
        fundingScript,
        asset_id):
    if asset_id in [TNC, TESTNET_TNC, MAINNET_TNC]:
        return tnc_factory.createCTX(
            addressFunding,
            balanceSelf,
            balanceOther,
            pubkeySelf,
            pubkeyOther,
            fundingScript,
            asset_id)

    elif asset_id == NEO:
        return neo_factory.createCTX(
            addressFunding,
            balanceSelf,
            balanceOther,
            pubkeySelf,
            pubkeyOther,
            fundingScript,
            asset_id)

    elif asset_id == GAS:
        return gas_factory.createCTX(
            addressFunding,
            balanceSelf,
            balanceOther,
            pubkeySelf,
            pubkeyOther,
            fundingScript,
            asset_id)


def createRDTX(
        addressRSMC,
        addressSelf,
        balanceSelf,
        CTxId,
        RSMCScript,
        asset_id):

    if asset_id in [TNC, TESTNET_TNC, MAINNET_TNC]:
        return tnc_factory.createRDTX(
            addressRSMC,
            addressSelf,
            balanceSelf,
            CTxId,
            RSMCScript,
            asset_id)

    elif asset_id == NEO:
        return neo_factory.createRDTX(
            addressSelf, balanceSelf, CTxId, RSMCScript, asset_id)

    elif asset_id == GAS:
        return gas_factory.createRDTX(
            addressSelf, balanceSelf, CTxId, RSMCScript, asset_id)


def createBRTX(addressRSMC, addressOther, balanceSelf, RSMCScript, CTxId, asset_id):

    if asset_id in [TNC, TESTNET_TNC, MAINNET_TNC]:
        return tnc_factory.createBRTX(
            addressRSMC,
            addressOther,
            balanceSelf,
            RSMCScript,
            asset_id)

    elif asset_id == NEO:
        return neo_factory.createBRTX(
            addressOther, balanceSelf, RSMCScript, CTxId, asset_id)

    elif asset_id == GAS:
        return gas_factory.createBRTX(
            addressOther, balanceSelf, RSMCScript, CTxId, asset_id)


def createRefundTX(
        addressFunding,
        balanceSelf,
        balanceOther,
        pubkeySelf,
        pubkeyOther,
        fundingScript,
        asset_id):

    if asset_id in [TNC, TESTNET_TNC, MAINNET_TNC]:
        return tnc_factory.createRefundTX(
            addressFunding,
            balanceSelf,
            balanceOther,
            pubkeySelf,
            pubkeyOther,
            fundingScript,
            asset_id)

    elif asset_id == NEO:
        return neo_factory.createRefundTX(
            addressFunding,
            balanceSelf,
            balanceOther,
            pubkeySelf,
            pubkeyOther,
            fundingScript,
            asset_id)

    elif asset_id == GAS:
        return gas_factory.createRefundTX(
            addressFunding,
            balanceSelf,
            balanceOther,
            pubkeySelf,
            pubkeyOther,
            fundingScript,
            asset_id)

# sender HTLC


def create_sender_HCTX(
        pubkeySender,
        pubkeyReceiver,
        HTLCValue,
        balanceSender,
        balanceReceiver,
        hashR,
        addressFunding,
        fundingScript,
        asset_id):
    if asset_id in [TNC, TESTNET_TNC, MAINNET_TNC]:
        return tnc_factory.create_sender_HCTX(
            pubkeySender,
            pubkeyReceiver,
            HTLCValue,
            balanceSender,
            balanceReceiver,
            hashR,
            addressFunding,
            fundingScript,
            asset_id)

    elif asset_id == NEO:
        return neo_factory.create_sender_HCTX(
            pubkeySender,
            pubkeyReceiver,
            HTLCValue,
            balanceSender,
            balanceReceiver,
            hashR,
            addressFunding,
            fundingScript,
            asset_id)

    elif asset_id == GAS:
        return gas_factory.create_sender_HCTX(
            pubkeySender,
            pubkeyReceiver,
            HTLCValue,
            balanceSender,
            balanceReceiver,
            hashR,
            addressFunding,
            fundingScript,
            asset_id)


def create_sender_RDTX(
        addressRSMC,
        addressSender,
        balanceSender,
        senderHCTxId,
        RSMCScript,
        asset_id):
    if asset_id in [TNC, TESTNET_TNC, MAINNET_TNC]:
        return tnc_factory.create_sender_RDTX(
            addressRSMC,
            addressSender,
            balanceSender,
            senderHCTxId,
            RSMCScript,
            asset_id)

    elif asset_id == NEO:
        return neo_factory.create_sender_RDTX(
            addressSender, balanceSender, senderHCTxId, RSMCScript, asset_id)

    elif asset_id == GAS:
        return gas_factory.create_sender_RDTX(
            addressSender, balanceSender, senderHCTxId, RSMCScript, asset_id)


def createHEDTX(
        addressHTLC,
        addressReceiver,
        HTLCValue,
        HTLCScript,
        senderHCTxId,
        asset_id):
    if asset_id in [TNC, TESTNET_TNC, MAINNET_TNC]:
        return tnc_factory.createHEDTX(
            addressHTLC,
            addressReceiver,
            HTLCValue,
            HTLCScript,
            asset_id)

    elif asset_id == NEO:
        return neo_factory.createHEDTX(
            addressReceiver,
            HTLCValue,
            HTLCScript,
            senderHCTxId,
            asset_id)

    elif asset_id == GAS:
        return gas_factory.createHEDTX(
            addressReceiver,
            HTLCValue,
            HTLCScript,
            senderHCTxId,
            asset_id)


def createHTTX(
        addressHTLC,
        pubkeySender,
        pubkeyReceiver,
        HTLCValue,
        HTLCScript,
        senderHCTxId,
        asset_id):
    if asset_id in [TNC, TESTNET_TNC, MAINNET_TNC]:
        return tnc_factory.createHTTX(
            addressHTLC,
            pubkeySender,
            pubkeyReceiver,
            HTLCValue,
            HTLCScript,
            asset_id)

    elif asset_id == NEO:
        return neo_factory.createHTTX(
            pubkeySender,
            pubkeyReceiver,
            HTLCValue,
            HTLCScript,
            senderHCTxId,
            asset_id)

    elif asset_id == GAS:
        return gas_factory.createHTTX(
            pubkeySender,
            pubkeyReceiver,
            HTLCValue,
            HTLCScript,
            senderHCTxId,
            asset_id)


def createHTRDTX(
        addressRSMC,
        addressSender,
        HTLCValue,
        HTTxId,
        RSMCScript,
        asset_id):
    if asset_id in [TNC, TESTNET_TNC, MAINNET_TNC]:
        return tnc_factory.createHTRDTX(
            addressRSMC,
            addressSender,
            HTLCValue,
            HTTxId,
            RSMCScript,
            asset_id)

    elif asset_id == NEO:
        return neo_factory.createHTRDTX(
            addressSender, HTLCValue, HTTxId, RSMCScript, asset_id)

    elif asset_id == GAS:
        return gas_factory.createHTRDTX(
            addressSender, HTLCValue, HTTxId, RSMCScript, asset_id)


# receiver HTLC
def create_receiver_HCTX(
        pubkeySender,
        pubkeyReceiver,
        HTLCValue,
        balanceSender,
        balanceReceiver,
        hashR,
        addressFunding,
        fundingScript,
        asset_id):
    if asset_id in [TNC, TESTNET_TNC, MAINNET_TNC]:
        return tnc_factory.create_receiver_HCTX(
            pubkeySender,
            pubkeyReceiver,
            HTLCValue,
            balanceSender,
            balanceReceiver,
            hashR,
            addressFunding,
            fundingScript,
            asset_id)

    elif asset_id == NEO:
        return neo_factory.create_receiver_HCTX(
            pubkeySender,
            pubkeyReceiver,
            HTLCValue,
            balanceSender,
            balanceReceiver,
            hashR,
            addressFunding,
            fundingScript,
            asset_id)

    elif asset_id == GAS:
        return gas_factory.create_receiver_HCTX(
            pubkeySender,
            pubkeyReceiver,
            HTLCValue,
            balanceSender,
            balanceReceiver,
            hashR,
            addressFunding,
            fundingScript,
            asset_id)


def create_receiver_RDTX(
        addressRSMC,
        addressReceiver,
        balanceReceiver,
        receiver_HCTxId,
        RSMCScript,
        asset_id):
    if asset_id in [TNC, TESTNET_TNC, MAINNET_TNC]:
        return tnc_factory.create_receiver_RDTX(
            addressRSMC,
            addressReceiver,
            balanceReceiver,
            receiver_HCTxId,
            RSMCScript,
            asset_id)

    elif asset_id == NEO:
        return neo_factory.create_receiver_RDTX(
            addressReceiver,
            balanceReceiver,
            receiver_HCTxId,
            RSMCScript,
            asset_id)

    elif asset_id == GAS:
        return gas_factory.create_receiver_RDTX(
            addressReceiver,
            balanceReceiver,
            receiver_HCTxId,
            RSMCScript,
            asset_id)


def createHTDTX(
        addressHTLC,
        pubkeySender,
        HTLCValue,
        HTLCScript,
        receiver_HCTxId,
        asset_id):

    if asset_id in [TNC, TESTNET_TNC, MAINNET_TNC]:
        return tnc_factory.createHTDTX(
            addressHTLC,
            pubkeySender,
            HTLCValue,
            HTLCScript,
            asset_id)

    elif asset_id == NEO:
        return neo_factory.createHTDTX(
            pubkeySender,
            HTLCValue,
            HTLCScript,
            receiver_HCTxId,
            asset_id)

    elif asset_id == GAS:
        return gas_factory.createHTDTX(
            pubkeySender,
            HTLCValue,
            HTLCScript,
            receiver_HCTxId,
            asset_id)


def createHETX(
        addressHTLC,
        pubkeySender,
        pubkeyReceiver,
        HTLCValue,
        HTLCScript,
        receiver_HCTxId,
        asset_id):
    if asset_id in [TNC, TESTNET_TNC, MAINNET_TNC]:
        return tnc_factory.createHETX(
            addressHTLC,
            pubkeySender,
            pubkeyReceiver,
            HTLCValue,
            HTLCScript,
            asset_id)

    elif asset_id == NEO:
        return neo_factory.createHETX(
            pubkeySender,
            pubkeyReceiver,
            HTLCValue,
            HTLCScript,
            receiver_HCTxId,
            asset_id)

    elif asset_id == GAS:
        return gas_factory.createHETX(
            pubkeySender,
            pubkeyReceiver,
            HTLCValue,
            HTLCScript,
            receiver_HCTxId,
            asset_id)


def createHERDTX(
        addressRSMC,
        addressReceiver,
        HTLCValue,
        HETxId,
        RSMCScript,
        asset_id):
    if asset_id in [TNC, TESTNET_TNC, MAINNET_TNC]:
        return tnc_factory.createHERDTX(
            addressRSMC,
            addressReceiver,
            HTLCValue,
            HETxId,
            RSMCScript,
            asset_id)

    elif asset_id == NEO:
        return neo_factory.createHERDTX(
            addressReceiver, HTLCValue, HETxId, RSMCScript, asset_id)

    elif asset_id == GAS:
        return gas_factory.createHERDTX(
            addressReceiver, HTLCValue, HETxId, RSMCScript, asset_id)


def create_sender_HTLC_TXS(
        pubkeySender,
        pubkeyReceiver,
        HTLCValue,
        balanceSender,
        balanceReceiver,
        hashR,
        addressFunding,
        fundingScript,
        asset_id):
    if asset_id in [TNC, TESTNET_TNC, MAINNET_TNC]:
        return tnc_factory.create_sender_HTLC_TXS(
            pubkeySender,
            pubkeyReceiver,
            HTLCValue,
            balanceSender,
            balanceReceiver,
            hashR,
            addressFunding,
            fundingScript,
            asset_id)

    elif asset_id == NEO:
        return neo_factory.create_sender_HTLC_TXS(
            pubkeySender,
            pubkeyReceiver,
            HTLCValue,
            balanceSender,
            balanceReceiver,
            hashR,
            addressFunding,
            fundingScript,
            asset_id)

    elif asset_id == GAS:
        return gas_factory.create_sender_HTLC_TXS(
            pubkeySender,
            pubkeyReceiver,
            HTLCValue,
            balanceSender,
            balanceReceiver,
            hashR,
            addressFunding,
            fundingScript,
            asset_id)


def create_receiver_HTLC_TXS(
        pubkeySender,
        pubkeyReceiver,
        HTLCValue,
        balanceSender,
        balanceReceiver,
        hashR,
        addressFunding,
        fundingScript,
        asset_id):
    if asset_id in [TNC, TESTNET_TNC, MAINNET_TNC]:
        return tnc_factory.create_receiver_HTLC_TXS(
            pubkeySender,
            pubkeyReceiver,
            HTLCValue,
            balanceSender,
            balanceReceiver,
            hashR,
            addressFunding,
            fundingScript,
            asset_id)

    elif asset_id == NEO:
        return neo_factory.create_receiver_HTLC_TXS(
            pubkeySender,
            pubkeyReceiver,
            HTLCValue,
            balanceSender,
            balanceReceiver,
            hashR,
            addressFunding,
            fundingScript,
            asset_id)

    elif asset_id == GAS:
        return gas_factory.create_receiver_HTLC_TXS(
            pubkeySender,
            pubkeyReceiver,
            HTLCValue,
            balanceSender,
            balanceReceiver,
            hashR,
            addressFunding,
            fundingScript,
            asset_id)

# 构建给单个地址发tnc的交易

#
# def construct_tx(addressFrom, addressTo, value, assetId):
#
#     time_stamp = TransactionAttribute(usage=TransactionAttributeUsage.Remark,
#                                       data=bytearray.fromhex(hex(int(time.time()))[2:]))
#     address_hash = TransactionAttribute(usage=TransactionAttributeUsage.Script,
#                                         data=ToAddresstHash(addressFrom).Data)
#
#     txAttributes = [address_hash, time_stamp]
#
#     op_data = create_opdata(
#         address_from=addressFrom,
#         address_to=addressTo,
#         value=value,
#         contract_hash=assetId)
#     tx = InvocationTransaction()
#     tx.Version = 1
#     tx.Attributes = txAttributes
#     tx.Script = binascii.unhexlify(op_data)
#
#     return {
#         "txData": tx.get_tx_data(),
#         "txid": createTxid(tx.get_tx_data())
#     }
#
# # 构建给3个地址发tnc的交易
#
#
# def construct_multi_tx(addressFrom, targetList, assetId):
#     time_stamp = TransactionAttribute(usage=TransactionAttributeUsage.Remark,
#                                       data=bytearray.fromhex(hex(int(time.time()))[2:]))
#     address_hash = TransactionAttribute(usage=TransactionAttributeUsage.Script,
#                                         data=ToAddresstHash(addressFrom).Data)
#
#     txAttributes = [address_hash, time_stamp]
#     op_data = ""
#     for item in targetList:
#         op_data += create_opdata(address_from=addressFrom,
#                                  address_to=item[0],
#                                  value=item[1],
#                                  contract_hash=assetId)
#
#     tx = InvocationTransaction()
#     tx.Version = 1
#     tx.Attributes = txAttributes
#     tx.Script = binascii.unhexlify(op_data)
#
#     return {
#         "txData": tx.get_tx_data(),
#         "txid": createTxid(tx.get_tx_data())
#     }
#
#
# def sign(txData, privtKey):
#     signature = privtkey_sign(txData, privtKey)
#     publicKey = privtKey_to_publicKey(privtKey)
#     rawData = txData + "01" + "41" + "40" + \
#         signature + "23" + "21" + publicKey + "ac"
#     return rawData


