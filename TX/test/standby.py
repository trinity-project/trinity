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