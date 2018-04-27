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
import requests
from TX.utils import pubkeyToAddressHash
from wallet.configure import Configure
AssetType=Configure["AssetType"]

TestNetUrl = "http://47.88.35.235:20332"


def get_block_count():
    request = {
  "jsonrpc": "2.0",
  "method": "getblockcount",
  "params": [],
  "id": 1
}

    result = requests.post(url = TestNetUrl, json = request)
    return result.json()["result"]


def send_raw(raw):
    request =  { "jsonrpc": "2.0",
  "method": "sendrawtransaction",
  "params": [raw],
  "id": 1}

    result = requests.post(url=TestNetUrl, json=request)
    if result.json().get("result") is not None:
        return result.json()["result"]
    else:
        return result.json()


def get_bolck(index):
    request = {
  "jsonrpc": "2.0",
  "method": "getblock",
  "params": [int(index), 1],
  "id": 1
}
    result = requests.post(url=TestNetUrl, json=request)
    return result.json()["result"]


def get_balance(pubkey, asset_type):
    asset_script = AssetType.get(asset_type.upper()).replace("0x","")
    address_hash = pubkeyToAddressHash(pubkey)
    def convert_hash(hash):
        t = hash[-2::-2]
        t1 = hash[::-2]
        s = ["".join(i) for i in zip(t, t1)]
        return "".join(s)

    request ={
        "jsonrpc": "2.0",
        "method": "invokefunction",
        "params": [
            asset_script,
            "balanceOf",
            [
                {
                    "type": "Hash160",
                    "value": convert_hash(address_hash)
                }
            ]
        ],
        "id": 3
    }
    result = requests.post(url=TestNetUrl, json=request)
    if result.json().get("result"):
        value = result.json().get("result").get("stack")[0].get("value")
        if value:
            return hex2interger(value)
    return 0



def hex2interger(input):
    tmp_list=[]
    for i in range(0,len(input),2):
        tmp_list.append(input[i:i+2])
    hex_str="".join(list(reversed(tmp_list)))
    output=int(hex_str,16)/100000000

    return output