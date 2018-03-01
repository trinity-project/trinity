import binascii
from base58 import b58decode
from neocore.Cryptography.Crypto import Crypto
from neocore.UInt160 import UInt160
from neocore.BigInteger import BigInteger
from neocore.KeyPair import KeyPair
from neocore.UInt256 import UInt256
import time


def createMultiSigAddress(script):
    scriptHash=Crypto.ToScriptHash(script)
    address=Crypto.ToAddress(scriptHash)
    return address


def ToScriptHash(address):
    data = b58decode(address)
    if len(data) != 25:
        raise ValueError('Not correct Address, wrong length.')
    if data[0] != 23:
        raise ValueError('Not correct Coin Version')

    checksum = Crypto.Default().Hash256(data[:21])[:4]
    if checksum != data[21:]:
        raise Exception('Address format error')
    return UInt160(data=data[1:21])


def hex_reverse(input):
    tmp_list = []
    for i in range(0, len(input), 2):
        tmp_list.append(input[i:i + 2])
    hex_str = "".join(list(reversed(tmp_list)))
    return hex_str


def int_to_hex(input):
    return binascii.hexlify(bytes([int(input)])).decode()


def privtkey_sign(txData,privteKey):
    return binascii.hexlify(Crypto.Sign(message=txData, private_key=privteKey)).decode()



def construct_opdata(addressFrom,addressTo,value,assetId):
    op_data=""
    value=binascii.hexlify(BigInteger(value*pow(10,8)).ToByteArray()).decode()
    scripthash_from=ToScriptHash(addressFrom).ToString2()
    scripthash_to=ToScriptHash(addressTo).ToString2()
    method=binascii.hexlify("transfer".encode()).decode()
    invoke_args=[value,scripthash_to,scripthash_from]
    for item in invoke_args:
        op_data+="".join([int_to_hex(len(item)/2),item])

    op_data+="53"     #PUSH3
    op_data+="c1"     #PACK
    op_data+=int_to_hex(len(method)/2)
    op_data+=method
    op_data+="67"                      #APPCALL
    op_data+=hex_reverse(assetId)
    op_data+= "f1"                      # maybe THROWIFNOT

    return op_data







def privtKey_to_publicKey(privtKey):

    pk=binascii.unhexlify(privtKey)
    keypair = KeyPair(pk)
    vk=keypair.PublicKey.encode_point(True).decode()
    return vk


def createTxid(txData):
    ba = binascii.unhexlify(txData)
    hash = Crypto.Hash256(ba)
    return UInt256(data=hash).ToString()


def createMultiSigContract(publicKey1,publicKey2,publicKey3):

    script1="52"+"21"+publicKey1+"21"+publicKey2+"21"+publicKey3+"53ae"
    script2="52"+"21"+publicKey2+"21"+publicKey1+"21"+publicKey3+"53ae"
    address1=createMultiSigAddress(script1)
    address2=createMultiSigAddress(script2)

    return {
        "contractForPublicKey1":{"script":script1,"address":address1},
        "contractForPublicKey2":{"script":script2,"address":address2}
    }



def construct_tx(addressFrom,addressTo,value,assetId):
    print("construct_tx", addressFrom, addressTo, value, assetId)
    scripthash_from=ToScriptHash(addressFrom).ToString2()
    timestamp = hex(int(time.time()))[2:]
    op_data=construct_opdata(addressFrom,addressTo,value,assetId)
    tx_data=""
    contract_type="d1"
    version="01"
    tx_data+=contract_type
    tx_data+=version
    tx_data+=int_to_hex(len(op_data)/2)
    tx_data+=op_data
    tx_data+="0000000000000000"
    tx_data+="02"       #attribute length
    tx_data+="20"       #AttributeType.Script
    tx_data+=scripthash_from
    tx_data+="f0"            #AttributeType.Remark
    tx_data+=int_to_hex(len(timestamp)/2)
    tx_data+=timestamp
    tx_data+="00"            #input length
    tx_data+="00"            #output length
    tx_id=createTxid(tx_data)
    return {
        "txid":tx_id,
        "txData":tx_data
    }



def construct_deposit_tx(assetId,addressFrom,addressTo1,value1,addressTo2,value2):
    scripthash_from=ToScriptHash(addressFrom).ToString2()
    timestamp = hex(int(time.time()))[2:]
    op_data=construct_opdata(addressFrom,addressTo1,value1,assetId)+construct_opdata(addressFrom,addressTo2,value2,assetId)
    tx_data=""
    contract_type="d1"
    version="01"
    tx_data+=contract_type
    tx_data+=version
    tx_data+=int_to_hex(len(op_data)/2)
    tx_data+=op_data
    tx_data+="0000000000000000"
    tx_data+="02"       #attribute length
    tx_data+="20"       #AttributeType.Script
    tx_data+=scripthash_from
    tx_data+="f0"            #AttributeType.Remark
    tx_data+=int_to_hex(len(timestamp)/2)
    tx_data+=timestamp
    tx_data+="00"            #input length
    tx_data+="00"            #output length
    tx_id=createTxid(tx_data)
    return {
        "txid":tx_id,
        "txData":tx_data
    }




def construct_raw_tx(txData,signature,publicKey):
    rawData=txData+"01"+"41"+"40"+signature+"23"+"21"+publicKey+"ac"
    return rawData


def construct_deposit_raw_tx(txData,signature1,signature2,verificationScript):
    invoke_script = int_to_hex(len(signature1) / 2) + signature1 + int_to_hex(len(signature2) / 2) + signature2
    txData+="01"         #witness length
    txData+=int_to_hex(len(invoke_script)/2)
    txData+=invoke_script
    txData+=int_to_hex(len(verificationScript)/2)
    txData+=verificationScript
    raw_data=txData
    return raw_data

