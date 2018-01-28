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

from .neo_api import neo_api
from configure import Configure
from neo_python_tool import query
from functools import reduce
from neo_python_tool.rpcServer.transfer_tnc import ToScriptHash
from crypto.Cryptography.Helper import hex2interger


NeoServer = neo_api.NeoApi(Configure["BlockNet"])

def add_to_channel(address, type, public_key, signature, channel_name, deposit=0, open_block_number=10 ):
    return True


def setting_transection(sender, receiver, channel_name):
    return True


def send_raw_transection(hax):
    return neo_api.send_raw_tx(hax)


def NewTransection(asset_type,from_addr, to_addr, count):
    tx_data= neo_api.invocate_contract_tx(from_addr, to_addr, Configure["AssetList"].get(asset_type.upper()), count)
    return tx_data["tx_data"]


def get_balance(address, asset_type):
    if asset_type.upper() == "NEO" or asset_type.upper() == "NEOGAS":
        return get_Neoasset_balance(address, asset_type.upper())
    else:
        scripthash =  Configure["AssetList"].get(asset_type.upper)
        operation = "balanceOf"
        params = [{
                        "type": "Hash160",
                        "value": ToScriptHash(address).ToString()
                    }]
        result = NeoServer.invokefunction(scripthash, operation *params)
        balance = result.value
        return hex2interger(balance)


def get_asset_id(asset_type):
    asset = filter(lambda x: asset_type in x , Configure["AssetList"])
    if asset:
        return asset[0].getdefault(asset_type, None)
    else:
        return None


def get_Neoasset_balance(address, asset_type):
    asset_id = get_asset_id(asset_type)
    if asset_id:
        balancelist = [ float(i.value) for i in query.get_utxo_by_address(address,asset_id.replace("0x",""))]
        balance = reduce(lambda x,y:x+y, balancelist)
        return {"AssetType": asset_type,
            "Balance":balance}
    else:
        return None



def distribute_balance(address, asset_type, value):
    asset_id = get_asset_id(asset_type.upper())
    return NeoServer.sendtoaddress(asset_id, address, value)


def allocate_address():
    return neo_api.allocate_address()


def tx_onchain(from_addr, to_addr, asset_type, value):
    return neo_api.tx_onchain(from_addr, to_addr,Configure["AssetList"].get(asset_type), value)