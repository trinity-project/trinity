import binascii
import requests
from base58 import b58decode
from neocore.BigInteger import BigInteger
from neocore.Cryptography.Crypto import Crypto
from neocore.Fixed8 import Fixed8
from neocore.KeyPair import KeyPair
from neocore.UInt160 import UInt160

from Settings import *


def get_asset_attachments(params):

    to_remove = []
    neo_to_attach = None
    gas_to_attach = None

    for item in params:

        if type(item) is str:
            if '--attach-neo=' in item:
                to_remove.append(item)
                try:
                    neo_to_attach = Fixed8.TryParse(int(item.replace('--attach-neo=', '')))
                except Exception as e:
                    pass
            if '--attach-gas=' in item:
                to_remove.append(item)
                try:
                    gas_to_attach = Fixed8.FromDecimal(float(item.replace('--attach-gas=', '')))
                except Exception as e:
                    pass
    for item in to_remove:
        params.remove(item)

    return params, neo_to_attach, gas_to_attach


def get_asset_id(asset_str):

    assetId =None
    if asset_str.lower() == 'neo':
        assetId = NEO
    elif asset_str.lower() == 'gas':
        assetId = GAS
    elif asset_str.lower() == 'tnc':
        assetId = TNC

    return assetId

def get_from_addr(params):
    to_remove = []
    from_addr = None
    for item in params:
        if '--from-addr=' in item:
            to_remove.append(item)
            try:
                from_addr = item.replace('--from-addr=', '')
            except Exception as e:
                pass
    for item in to_remove:
        params.remove(item)

    return params, from_addr

def addrStrToScriptHash(address):

    data = b58decode(address)
    if len(data) != 25:
        raise ValueError('Not correct Address, wrong length.')
    if data[0] != ADDRESS_VERSION:
        raise ValueError('Not correct Coin Version')

    checksum = Crypto.Default().Hash256(data[:21])[:4]
    if checksum != data[21:]:
        raise Exception('Address format error')
    return UInt160(data=data[1:21])

def parse_param(p, wallet=None, ignore_int=False, prefer_hex=True):

    # first, we'll try to parse an array

    try:
        items = eval(p)
        if len(items) > 0 and type(items) is list:

            parsed = []
            for item in items:
                parsed.append(parse_param(item, wallet))
            return parsed

    except Exception as e:
        pass

    if not ignore_int:
        try:
            val = int(p)
            out = BigInteger(val)
            return out
        except Exception as e:
            pass

    try:
        val = eval(p)

        if type(val) is bytearray:
            return val.hex()

        return val
    except Exception as e:
        pass

    if type(p) is str:

        if wallet is not None:
            for na in wallet.NamedAddr:
                if na.Title == p:
                    return bytearray(na.ScriptHash)

        if len(p) == 34 and p[0] == 'A':
            addr = addrStrToScriptHash(p).Data
            return addr

        if prefer_hex:
            return binascii.hexlify(p.encode('utf-8'))
        else:
            return p.encode('utf-8')

    return p

def get_arg(arguments, index=0, convert_to_int=False, do_parse=False):
    try:
        arg = arguments[index]
        if convert_to_int:
            return int(arg)
        if do_parse:
            return parse_param(arg)
        return arg
    except Exception as e:
        pass
    return None

def get_balance(address):
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "jsonrpc": "2.0",
        "method": "getBalance",
        "params": [address],
        "id": 1
    }
    res = requests.post(NODEURL, headers=headers, json=data).json()
    return res

def construct_tx(addressFrom,addressTo,amount,assetId):

    data = {
        "jsonrpc": "2.0",
        "method": "constructTx",
        "params": [addressFrom,addressTo,float(amount),assetId],
        "id": 1
    }
    res = requests.post(NODEURL, headers=headers, json=data).json()
    return res

def send_raw_tx(rawTx):

    data = {
        "jsonrpc": "2.0",
        "method": "sendRawTx",
        "params": [rawTx],
        "id": 1
    }
    res = requests.post(NODEURL, headers=headers, json=data).json()
    if res["result"]:
        return True
    return False

def privtkey_sign(txData,privteKey):
    return binascii.hexlify(Crypto.Sign(message=txData, private_key=privteKey)).decode()

def privtKey_to_publicKey(privtKey):

    pk=binascii.unhexlify(privtKey)
    keypair = KeyPair(pk)
    vk=keypair.PublicKey.encode_point(True).decode()
    return vk