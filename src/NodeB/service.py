

import requests
from NodeB.utils import createMultiSigAddress, ToScriptHash, int_to_hex, construct_opdata, privtkey_sign, hex_reverse, \
    privtKey_to_publicKey,createTxid
from NodeB.app.model import Balance,Tx
from NodeB.config import *
from NodeB import utils

def createMultiSigContract(publicKey1,publicKey2,publicKey3):
    utils.createMultiSigContract(publicKey1,publicKey2,publicKey3)


def construct_tx(addressFrom,addressTo,value,assetId):
    utils.construct_tx(addressFrom,addressTo,value,assetId)


def construct_deposit_tx(assetId,addressFrom,addressTo1,value1,addressTo2,value2):
    utils.construct_deposit_tx(assetId,addressFrom,addressTo1,value1,addressTo2,value2)


def construct_raw_tx(txData,signature,publicKey):
    utils.construct_raw_tx(txData,signature,publicKey)


def construct_deposit_raw_tx(txData,signature1,signature2,verificationScript):
    utils.construct_deposit_raw_tx(txData,signature1,signature2,verificationScript)


def send_raw_tx(rawTx):
    data = {
        "jsonrpc": "2.0",
        "method": "sendrawtransaction",
        "params": [rawTx],
        "id": 1
    }
    res = requests.post(NEOCLIURL, headers=headers, json=data).json()
    if res["result"]:
        return "success"
    return "fail"


def sign(txData,privtKey):
    signature = privtkey_sign(txData,privtKey)
    publicKey=privtKey_to_publicKey(privtKey)
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

    data = {
        "jsonrpc": "2.0",
        "method": "invokefunction",
        "params": [
            CONTRACTHASH,
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
    res = requests.post(NEOCLIURL, headers=headers, json=data).json()
    if res["result"]["state"]=="HALT, BREAK":

        value=res["result"]["stack"][0]["value"]
    else:
        value=None

    if balance:
        response={
            "gasBalance":float(balance.gas_balance),
            "neoBalance":float(balance.neo_balance),
            "tncBalance":int(hex_reverse(value),16)/100000000 if value else 0
        }
    else:
        if value:
            response={"tncBalance":int(hex_reverse(value),16)/100000000,"gasBalance":0,"neoBalance":0}
        else:
            response={"tncBalance":0,"gasBalance":0,"neoBalance":0}
    return response


def confirm_tx(txList):
    response={}
    for tx in txList:
        tx_instanse=Tx.query.filter_by(tx_id="0x"+tx).first()
        if tx_instanse:
            response[tx]=True
        else:
            response[tx]=False

    return response


def transfer_tnc(addressFrom,addressTo):
    tx_data=construct_tx(addressFrom=addressFrom,addressTo=addressTo,value=10,assetId="849d095d07950b9e56d0c895ec48ec5100cfdff1")
    tx_id = tx_data["txid"]
    raw_data=sign(txData=tx_data["txData"],privtKey="0d94b060fe4a5f382174f75f3dca384ebc59c729cef92d553084c7c660a4c08f")
    response=send_raw_tx(raw_data)
    if response=="success":
        return tx_id
    else:
        return None