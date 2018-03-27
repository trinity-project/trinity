import binascii
import time
from neocore.BigInteger import BigInteger
from neocore.Cryptography.Crypto import Crypto
from TX.MyTransaction import InvocationTransaction
from TX.TransactionAttribute import TransactionAttribute, TransactionAttributeUsage
from TX.config import *
from TX.utils import hex_reverse, ToAddresstHash, int_to_hex, createTxid




def createMultiSigAddress(script):
    scriptHash=Crypto.ToScriptHash(script)
    address=Crypto.ToAddress(scriptHash)
    return address

def create_opdata(address_from, address_to, value, contract_hash):
    op_data = ""
    value = binascii.hexlify(BigInteger(value * pow(10, 8)).ToByteArray()).decode()
    scripthash_from = ToAddresstHash(address_from).ToString2()
    scripthash_to = ToAddresstHash(address_to).ToString2()
    method = binascii.hexlify("transfer".encode()).decode()
    invoke_args = [value, scripthash_to, scripthash_from]
    for item in invoke_args:
        op_data += "".join([int_to_hex(len(item) / 2), item])

    op_data += "53"  # PUSH3
    op_data += "c1"  # PACK
    op_data += int_to_hex(len(method) / 2)
    op_data += method
    op_data += "67"  # APPCALL
    op_data += hex_reverse(contract_hash)
    op_data += "f1"  # maybe THROWIFNOT

    return op_data





def createRSMCContract(hashSelf,pubkeySelf,hashOther,pubkeyOther,magicTimestamp):
    magicTimestamp = binascii.hexlify(str(magicTimestamp).encode()).decode()
    length=hex(int(len(magicTimestamp)/2))[2:]
    magicTimestamp=length+magicTimestamp
    contractTemplate="5dc56b6c766b00527ac46c766b51527ac46c766b52527ac461{magicTimestamp}6c766b53527ac46168295379737" \
                     "4656d2e457865637574696f6e456e67696e652e476574536372697074436f6e7461696e65726c766b54527ac46c766b" \
                     "54c361681d4e656f2e5472616e73616374696f6e2e476574417474726962757465736c766b55527ac4616c766b55c36" \
                     "c766b56527ac4006c766b57527ac46258016c766b56c36c766b57c3c36c766b58527ac4616c766b58c36168154e656f" \
                     "2e4174747269627574652e476574446174616114{hashOther}9c6c766b59527ac46c766b59c3646700616c766b00c36121" \
                     "{pubkeySelf}ac642f006c766b51c36121{pubkeyOther}ac620400006c766b5a527ac462b8006c766b58c36168154e656f2e4" \
                     "174747269627574652e476574446174616114{hashSelf}9c6c766b5b527ac46c766b5bc3644c00616c766b52c36c766b5" \
                     "4c3617c653e016c766b5c527ac46c766b5cc36422006c766b52c36c766b00c36c766b51c3615272654a006c766b5a52" \
                     "7ac4623700006c766b5a527ac4622c00616c766b57c351936c766b57527ac46c766b57c36c766b56c3c09f639ffe006" \
                     "c766b5a527ac46203006c766b5ac3616c756656c56b6c766b00527ac46c766b51527ac46c766b52527ac4616168184e" \
                     "656f2e426c6f636b636861696e2e4765744865696768746c766b53527ac46c766b00c302e803936c766b53c39f6c766" \
                     "b54527ac46c766b54c36466006c766b51c36121{pubkeySelf}ac642f006c766b52c36121{pubkeyOther}ac620400006c766b" \
                     "55527ac4620e00006c766b55527ac46203006c766b55c3616c75665ec56b6c766b00527ac46c766b51527ac4616c766" \
                     "b00c36168174e656f2e426c6f636b636861696e2e476574426c6f636b6c766b52527ac46c766b52c36168194e656f2e" \
                     "426c6f636b2e4765745472616e73616374696f6e736c766b53527ac46c766b51c361681d4e656f2e5472616e7361637" \
                     "4696f6e2e476574417474726962757465736c766b54527ac4616c766b54c36c766b55527ac4006c766b56527ac462d1" \
                     "006c766b55c36c766b56c3c36c766b57527ac4616c766b57c36168154e656f2e4174747269627574652e47657444617" \
                     "4616c766b58527ac4616c766b53c36c766b59527ac4006c766b5a527ac46264006c766b59c36c766b5ac3c36c766b5b" \
                     "527ac4616c766b5bc36168174e656f2e5472616e73616374696f6e2e476574486173686c766b58c39c6c766b5c527ac" \
                     "46c766b5cc3640e00516c766b5d527ac4624a00616c766b5ac351936c766b5a527ac46c766b5ac36c766b59c3c09f63" \
                     "93ff616c766b56c351936c766b56527ac46c766b56c36c766b55c3c09f6326ff006c766b5d527ac46203006c766b5dc" \
                     "3616c7566"
    RSMCContract=contractTemplate.format(hashOther=hashOther,pubkeySelf=pubkeySelf,hashSelf=hashSelf,pubkeyOther=pubkeyOther,\
                                         magicTimestamp=magicTimestamp)

    return  {
        "script":RSMCContract,
        "address":createMultiSigAddress(RSMCContract)
    }

def createHTLCContract(futureTimestamp,pubkeySelf,pubkeyOther,hashR):
    futureTimestamp=hex_reverse(hex(int(futureTimestamp)))
    contractTemplate="57c56b6c766b00527ac46c766b51527ac46c766b52527ac4616c766b52c3a76c766b53527ac46168184e656f2e426c6" \
                     "f636b636861696e2e4765744865696768746168184e656f2e426c6f636b636861696e2e4765744865616465726c766b" \
                     "54527ac46c766b54c36168174e656f2e4865616465722e47657454696d657374616d7004{futureTimestamp}9f6c76" \
                     "6b55527ac46c766b55c3648600616c766b00c36121{pubkeySelf}ac644e006c766b51c36121{pubkeyOther}ac6422006c766b5" \
                     "3c36114{hashR}9c620400006c766b56527ac46266006c766b00c36121{pubkeySelf}ac642f006c766b51c36121{pubkeyOther}" \
                     "ac620400006c766b56527ac46203006c766b56c3616c7566"

    HTLCContract=contractTemplate.format(futureTimestamp=futureTimestamp,pubkeySelf=pubkeySelf,pubkeyOther=pubkeyOther,hashR=hashR)


    return  {
        "script":HTLCContract,
        "address":createMultiSigAddress(HTLCContract)
    }

def createMultiSigContract(publicKeyList):
    # publicKeyList.sort()
    script="52"
    for item in publicKeyList:
        script+="21"
        script+=item
    script+="52"
    script+="ae"


    address=createMultiSigAddress(script)


    return {
        "script":script,
        "address":address
    }


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


def createHCTX(pubkeySelf,pubkeyOther,addressSelf,addressOther,HTLCValue,balanceSelf,balanceOther,hashR,addressFunding):

    RSMCContract=createRSMCContract(hashSelf=ToAddresstHash(addressSelf).ToString2(),pubkeySelf=pubkeySelf,
                       hashOther=ToAddresstHash(addressOther).ToString2(),pubkeyOther=pubkeyOther,magicTimestamp=time.time())

    HTLCContract=createHTLCContract(pubkeySelf=pubkeySelf,pubkeyOther=pubkeyOther,futureTimestamp=int(time.time())+600,
                                    hashR=hashR)
    time_stamp = TransactionAttribute(usage=TransactionAttributeUsage.Remark,
                                      data=bytearray.fromhex(hex(int(time.time()))[2:]))
    address_hash_funding = TransactionAttribute(usage=TransactionAttributeUsage.Script,
                                         data=ToAddresstHash(addressFunding).Data)
    txAttributes = [address_hash_funding, time_stamp]

    op_data_to_HTLC = create_opdata(address_from=addressFunding, address_to=HTLCContract["address"], value=HTLCValue,contract_hash=TNC)
    op_data_to_RSMC = create_opdata(address_from=addressFunding, address_to=RSMCContract["address"], value=balanceSelf-HTLCValue,contract_hash=TNC)
    op_data_to_other = create_opdata(address_from=addressFunding, address_to=addressOther, value=balanceOther,contract_hash=TNC)

    tx = InvocationTransaction()
    tx.Version = 1
    tx.Attributes = txAttributes
    tx.Script = binascii.unhexlify(op_data_to_RSMC+op_data_to_other+op_data_to_HTLC)

    return {
        "txData":tx.get_tx_data(),
        "addressRSMC":RSMCContract["address"],
        "addressHTLC":HTLCContract["address"],
        "RSMCscript":RSMCContract["script"],
        "HTLCscript":HTLCContract["script"],
        "txId":createTxid(tx.get_tx_data())
    }


def createHEDTX(addressHTLC,addressOther,HTLCValue):

    time_stamp = TransactionAttribute(usage=TransactionAttributeUsage.Remark,
                                      data=bytearray.fromhex(hex(int(time.time()))[2:]))
    address_hash_HTLC = TransactionAttribute(usage=TransactionAttributeUsage.Script,
                                         data=ToAddresstHash(addressHTLC).Data)
    txAttributes = [address_hash_HTLC, time_stamp]

    op_data_to_other = create_opdata(address_from=addressHTLC, address_to=addressOther, value=HTLCValue,contract_hash=TNC)


    tx = InvocationTransaction()
    tx.Version = 1
    tx.Attributes = txAttributes
    tx.Script = binascii.unhexlify(op_data_to_other)

    return tx.get_tx_data()


def createHTTX(addressHTLC, addressSelf, HTLCValue):
    time_stamp = TransactionAttribute(usage=TransactionAttributeUsage.Remark,
                                      data=bytearray.fromhex(hex(int(time.time()))[2:]))
    address_hash_HTLC = TransactionAttribute(usage=TransactionAttributeUsage.Script,
                                             data=ToAddresstHash(addressHTLC).Data)
    txAttributes = [address_hash_HTLC, time_stamp]

    op_data_to_self = create_opdata(address_from=addressHTLC, address_to=addressSelf, value=HTLCValue,
                                     contract_hash=TNC)

    tx = InvocationTransaction()
    tx.Version = 1
    tx.Attributes = txAttributes
    tx.Script = binascii.unhexlify(op_data_to_self)

    return tx.get_tx_data()



HT_tx = createHTTX(addressHTLC="Aa39qp1dKx2cwqHyi4KULotprPfdeCpdJ4", addressSelf="ASm37KDVtgNQRqd4eefYGKCGn8fQH3mHw2", HTLCValue=5)



# walletSelf= {
#     "pubkey":"03ed45d1fdf6dbd5a6e5567b50d2b36b8ae5c1cd0123f26aba000fd3a72d6fbd28",
#     "address":"ASm37KDVtgNQRqd4eefYGKCGn8fQH3mHw2",
#     "deposit":10
# }
# walletOther= {
#     "pubkey":"03d8f667ff2068751e117cd6dbe3ebe286dbbc7fbb7b1ef0fbf5eb068e8b783a94",
#     "address":"AJAd9ZaZCwLvdktHc1Rs7w3hmpVSBuTKzs",
#     "deposit":10
# }






#
# HC_tx =createHCTX(pubkeySelf="03ed45d1fdf6dbd5a6e5567b50d2b36b8ae5c1cd0123f26aba000fd3a72d6fbd28",
#                   pubkeyOther="03d8f667ff2068751e117cd6dbe3ebe286dbbc7fbb7b1ef0fbf5eb068e8b783a94",
#                   addressSelf="ASm37KDVtgNQRqd4eefYGKCGn8fQH3mHw2",addressOther="AJAd9ZaZCwLvdktHc1Rs7w3hmpVSBuTKzs",
#                   HTLCValue=5,balanceSelf=10,
#                   balanceOther=10,hashR="7c4a8d09ca3762af61e59520943dc26494f8941b",
#                   addressFunding="AQmhy9TH8jVjz8YyBzFSQ2yhGcPAKUd96N")





# funding_tx = createFundingTx(walletSelf=walletSelf,walletOther=walletOther)

# C_tx = createCTX(addressFunding=funding_tx["addressFunding"],addressSelf=walletSelf["address"],
#                  balanceSelf=walletSelf["deposit"],addressOther=walletOther["address"],
#                  balanceOther=walletOther["deposit"],pubkeySelf=walletSelf["pubkey"],pubkeyOther=walletOther["pubkey"])
#
# RD_tx = createRDTX(addressRSMC= C_tx["addressRSMC"],addressSelf=walletSelf["address"],
#                    balanceSelf=walletSelf["deposit"],CTxId=C_tx["txId"])
#
# BR_tx = createBRTX(addressRSMC=C_tx["addressRSMC"],addressOther=walletOther["address"],balanceSelf=walletSelf["deposit"])
# BR_tx = createBRTX(addressRSMC="AJJFzQuAtFaLjW2bLEiuDdY682USNswKhC",addressOther=walletOther["address"],balanceSelf=walletSelf["deposit"])



# xx=createRD1ATX(addressA1B="AQfnZ3euLYqaEhdeTEqqqeQVtWYTtFHzFx",addressA="ALcC96eesqb9pQTWSDCQ8afqdyR4woUzhW",balanceA=2)
#
# address_from="ALcC96eesqb9pQTWSDCQ8afqdyR4woUzhW"
# multi_contract=createMultiSigContract(["0299dc85df93fee8ff2230af0418cf8c5000296f0aed514fcc0ab0dd969ce0bdb0","034e9d2751e1fec65a6a42bc097bdf55c7a79762df7d6e970277f46405c376683a"])
pass
# address_from=multi_contract["address"]
# verify_script=createVerifyScript("5221034e9d2751e1fec65a6a42bc097bdf55c7a79762df7d6e970277f46405c376683a2103eb0881d1d64754d50255bf16079ed6cbc3982463a8904cb919422b39178bef3f52ae")
# print ("verify script:",verify_script)
# time_stamp = TransactionAttribute(usage=TransactionAttributeUsage.Remark, data=bytearray.fromhex(hex(int(time.time()))[2:]))
# pre_txid= TransactionAttribute(usage=TransactionAttributeUsage.Remark1, data=bytearray.fromhex(hex_reverse("0xf95bc0f9682df5c74c35c64f9079c9498cc6f1004d72e016bb03c4e419578b8a")))
# outputTo= TransactionAttribute(usage=TransactionAttributeUsage.Remark2, data=bytearray.fromhex("d904f61978b83b706445d2c418e336de4d6261d2"))
# address_hash1=TransactionAttribute(usage=TransactionAttributeUsage.Script, data=ToAddresstHash("AZH8KcoZsgyzbYze6CMYsNdM1UJDQRxGdK").Data)
# address_hash2=TransactionAttribute(usage=TransactionAttributeUsage.Script, data=ToAddresstHash("AdoHFZV8fxnVQBZ881mdGhynjGC3156Skv").Data)
# txAttributes=[address_hash1,time_stamp,pre_txid,outputTo]
#
#
#
# op_data1= create_opdata(address_from="AZH8KcoZsgyzbYze6CMYsNdM1UJDQRxGdK",address_to="AbZNDqwCSZj4XJSGHmbQTSoHofE2PRMurT",value=1,contract_hash=TNC)
# op_data2= create_opdata(address_from="AdoHFZV8fxnVQBZ881mdGhynjGC3156Skv",address_to=address_from,value=1,contract_hash=TNC)
# print (op_data)
# tx=InvocationTransaction()
# tx.Version=1
# tx.Attributes=txAttributes
# tx.Script=binascii.unhexlify(op_data1)
#
# print(tx.get_tx_data())


# time_stamp = TransactionAttribute(usage=TransactionAttributeUsage.Remark, data=bytearray.fromhex(hex(int(time.time()))[2:]))
# address_hash=TransactionAttribute(usage=TransactionAttributeUsage.Script, data=ToAddresstHash("AJAd9ZaZCwLvdktHc1Rs7w3hmpVSBuTKzs").Data)
# outputTo= TransactionAttribute(usage=TransactionAttributeUsage.Remark2, data=ToAddresstHash("AJAd9ZaZCwLvdktHc1Rs7w3hmpVSBuTKzs").Data)
# txAttributes=[address_hash,time_stamp,outputTo]
#
#
#
# op_data= create_opdata(address_from="AJAd9ZaZCwLvdktHc1Rs7w3hmpVSBuTKzs",address_to="ALcC96eesqb9pQTWSDCQ8afqdyR4woUzhW",value=13,contract_hash=TNC)
# tx=InvocationTransaction()
# tx.Version=1
# tx.Attributes=txAttributes
# tx.Script=binascii.unhexlify(op_data)
#
# print(tx.get_tx_data())


# sadf=createRSMCContract(hashSelf="7880ddceb5101a29e05ea09da1ad310539dc8e69",hashOther="1a3db733023a855ac2077926c60e4c1fb4d5af00",pubkeyOther="03d8f667ff2068751e117cd6dbe3ebe286dbbc7fbb7b1ef0fbf5eb068e8b783a94",pubkeySelf="03ed45d1fdf6dbd5a6e5567b50d2b36b8ae5c1cd0123f26aba000fd3a72d6fbd28",magicTimestamp=time.time())
# print (sadf)