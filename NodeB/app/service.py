import time

import requests
from app.utils import createMultiSigAddress,ToScriptHash,int_to_hex,construct_opdata,privtkey_sign,hex_reverse

from app.model import Balance


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
    return tx_data


def send_raw_tx(rawTx):
    url = "http://192.168.138.128:10332"
    headers = {
        "Content-Type": "application/json"
    }

    data = {
        "jsonrpc": "2.0",
        "method": "sendrawtransaction",
        "params": [rawTx],
        "id": 1
    }
    res = requests.post(url, headers=headers, json=data).json()
    if res["result"]:
        return "success"
    return "fail"


def sign(txData,privtKey,publicKey):
    signature = privtkey_sign(txData,privtKey)
    rawData=txData+"01"+"41"+"40"+signature+"23"+"21"+publicKey+"ac"
    return rawData




def multi_sign(txData,privtKey1,privtKey2,verificationScript):
    signature1 = privtkey_sign(txData, privtKey1)
    signature2 = privtkey_sign(txData, privtKey2)
    invoke_script = int_to_hex(len(signature1) / 2) + signature1 + int_to_hex(len(signature2) / 2) + signature2

    txData+="01"         #witness length
    txData+=int_to_hex(len(invoke_script)/2)
    txData+=invoke_script
    txData+=int_to_hex(len(verificationScript)/2)
    txData+=verificationScript
    raw_data=txData
    return raw_data

def get_balance(address):
    balance=Balance.query.filter_by(address=address).first()
    url = "http://192.168.138.128:10332"
    headers = {
        "Content-Type": "application/json"
    }

    data = {
        "jsonrpc": "2.0",
        "method": "invokefunction",
        "params": [
            "0c34a8fd0109df360c7cf7ca454404901db77f5e",
            "balanceOf",
            [
                {
                    "type":"Hash160",
                    "value":ToScriptHash(address).ToString()
                }
            ]
        ],
        "id": 1
    }
    res = requests.post(url, headers=headers, json=data).json()
    value=res["result"]["stack"][0]["value"]
    if balance:
        response={
            "gasBalance":float(balance.gas_balance),
            "neoBalance":float(balance.neo_balance),
            "tncBalance":int(hex_reverse(value),16)/100000000 if value else 0
        }
    else:
        if value:
            response={"tncBalance":int(hex_reverse(value),16)/100000000}
        else:
            response={}
    return response