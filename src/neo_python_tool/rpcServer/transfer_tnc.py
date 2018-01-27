
import binascii
import json

import requests
import sys
from base58 import b58decode
from neocore.IO.BinaryWriter import BinaryWriter
from neocore.BigInteger import BigInteger
from neo.Core.TX.InvocationTransaction import InvocationTransaction
from neo.Core.TX.Transaction import TransactionOutput,TransactionInput
from neo.Core.Blockchain import Blockchain
from neocore.Cryptography.Crypto import Crypto
from neocore.Fixed8 import Fixed8
from neocore.UInt160 import UInt160
from neocore.UInt256 import UInt256
from neo.IO.MemoryStream import MemoryStream
from neo.SmartContract.ContractParameterContext import ContractParametersContext
from neo.VM.ScriptBuilder import ScriptBuilder, PACK
from neo.Wallets.NEP5Token import NEP5Token





# address_to = "AbZNDqwCSZj4XJSGHmbQTSoHofE2PRMurT"
# address_from = "AGgZna4kbTXPm16yYZyG6RyrQz2Sqotno6"
# tnc_amount = 7
# gas_change = None
# input_txid = None
# preIndex = None
# contract_hash ="849d095d07950b9e56d0c895ec48ec5100cfdff1"
# private_key = "0d94b060fe4a5f382174f75f3dca384ebc59c729cef92d553084c7c660a4c08f"
# public_key = "023886d5529481223f94d422bb6a1e05b0f831e2628c3200373a986b8208ff1c26"

def get_gas_balance(address):
    url = "http://192.168.203.64:8000/api/getBalance"
    headers = {
        "Content-Type": "application/json"
    }

    data = {
        "address": address
    }
    res = requests.post(url, headers=headers, json=data).json()
    if res:
        return res["gasBalance"]
    return None


def get_gas_vouts(address):

    url = "http://192.168.203.64:8000/api/getGasVout"
    headers = {
        "Content-Type": "application/json"
    }

    data = {
        "address": address
    }
    res = requests.post(url, headers=headers, json=data).json()

    return res



def send_rawtransaction(hexstr):
    url = "http://192.168.203.64:20332"
    headers = {
        "Content-Type": "application/json"
    }

    data = {
        "jsonrpc": "2.0",
        "method": "sendrawtransaction",
        "params": [hexstr],
        "id": 1
    }
    res = requests.post(url, headers=headers, json=data).json()
    if res["result"]:
        return "sucess"
    return "fail"


def amount_from_string(token, amount_str):
    precision_mult = pow(10, token.decimals)
    amount = float(amount_str) * precision_mult

    return int(amount)


def get_nep5token_id(contract_hash):
    hash_ar = bytearray(binascii.unhexlify(contract_hash))
    hash_ar.reverse()
    hash = UInt160(data=hash_ar)
    token = NEP5Token()
    token.SetScriptHash(hash)
    # token.symbol = "TNC"
    token.decimals = 8

    return token


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


def get_asset_id(asset_type):
    assetId = None

    if asset_type.lower() == 'neo':
        assetId = Blockchain.Default().SystemShare().Hash
    elif asset_type.lower() == 'gas':
        assetId = Blockchain.Default().SystemCoin().Hash
    elif Blockchain.Default().GetAssetState(asset_type):
        assetId = Blockchain.Default().GetAssetState(asset_type).AssetId

    return assetId


def hex_reverse(input):
    tmp_list = []
    for i in range(0, len(input), 2):
        tmp_list.append(input[i:i + 2])
    hex_str = "".join(list(reversed(tmp_list)))
    return hex_str


def get_tx_data(tx):
    ms = MemoryStream()
    w = BinaryWriter(ms)
    tx.Serialize(w)
    ms.flush()
    tx_data = ms.ToArray().decode()
    return tx_data


def toArray(obj):
    ms = MemoryStream()
    w = BinaryWriter(ms)
    obj.Serialize(w)
    ms.flush()
    return ms.ToArray().decode()


def create_tx(contract_hash,address_from,address_to,tnc_amount,gas_change,input_txid,preIndex):

    nep5TokenId=get_nep5token_id(contract_hash)
    scripthash_from=ToScriptHash(address_from)
    scripthash_to=ToScriptHash(address_to)
    f8amount=amount_from_string(nep5TokenId,tnc_amount)
    f8amount_change = Fixed8.TryParse(gas_change, require_positive=True)
    assetId=get_asset_id("gas")
    preHash=UInt256(data=binascii.unhexlify(hex_reverse(input_txid)))

    input = TransactionInput(prevHash=preHash, prevIndex=preIndex)
    output = TransactionOutput(AssetId=assetId, Value=f8amount_change, script_hash=scripthash_from)

    tx = InvocationTransaction(outputs=[output], inputs=[input])
    tx.Version = 1
    context = ContractParametersContext(tx)
    tx.scripts = context.GetScripts()




    invoke_args=[nep5TokenId.ScriptHash, 'transfer',[bytearray.fromhex(hex_reverse(scripthash_from.ToString())),
                                                                           bytearray.fromhex(hex_reverse(scripthash_to.ToString())),
                                                                           BigInteger(f8amount)]]
    sb = ScriptBuilder()
    invoke_args.reverse()
    for item in invoke_args[:2]:
        if type(item) is list:
            item.reverse()
            listlength = len(item)
            for listitem in item:
                sb.push(listitem)
            sb.push(listlength)
            sb.Emit(PACK)
        else:
            sb.push(binascii.hexlify(item.encode()))

    sb.EmitAppCall(nep5TokenId.ScriptHash.ToArray())


    op_data = sb.ToArray().decode()
    tx.Script = binascii.unhexlify(op_data)
    tx_data=get_tx_data(tx)[:-2]
    print ("tx_data:",tx_data)
    signstr =binascii.hexlify(Crypto.Sign(message=tx_data, private_key=private_key)).decode()
    rawtx_data = tx_data + "014140" + signstr + "2321" + public_key + "ac"
    return rawtx_data



