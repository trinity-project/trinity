"""Author: Trinity Core Team 

MIT License

Copyright (c) 2018 Trinity

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE."""


from neocore.Cryptography.Crypto import Crypto
import binascii
from wallet.configure import Configure

import hashlib


def to_aes_key(password):
    """

    :param password:
    :return:
    """

    password_hash = hashlib.sha256(password.encode('utf-8')).digest()
    return hashlib.sha256(password_hash).digest()


def pubkey_to_address(publickey: str):
    """

    :param publickey:
    :return:
    """
    script = b'21' + publickey.encode() + b'ac'
    script_hash = Crypto.ToScriptHash(script)
    address = Crypto.ToAddress(script_hash)
    return address


def sign(wallet, context):
    """

    :param wallet:
    :param context:
    :return:
    """
    res = wallet.SignContent(context)
    return res

def get_arg(arguments, index=0, convert_to_int=False):
    """

    :param arguments:
    :param index:
    :param convert_to_int:
    :param do_parse:
    :return:
    """

    try:
        arg = arguments[index]
        if convert_to_int:
            return int(arg)
        return arg
    except Exception as e:
        pass
    return None


def get_asset_type_name(asset_type):
    for key, value in Configure.get("AssetType"):
        if value.replace("0x","") == asset_type.replace("0x",""):
            return key
        else:
            continue
    return None

def get_asset_type_id(asset_name):
    return Configure.get("AssetType").get(asset_name.upper())


if __name__ == "__main__":
    print(pubkey_to_address("03a6fcaac0e13dfbd1dd48a964f92b8450c0c81c28ce508107bc47ddc511d60e75"))
    print(Crypto.Hash160("02cebf1fbde4786f031d6aa0eaca2f5acd9627f54ff1c0510a18839946397d3633".encode()))