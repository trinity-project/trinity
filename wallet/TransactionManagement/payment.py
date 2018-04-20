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
import base58
from wallet.configure import Configure
from log import LOG
import json
import binascii
import hashlib
from Crypto import Random



class Payment(object):
    """

    """
    HashR={}

    def __init__(self, wallet):
        self.wallet = wallet

    def generate_payment_code(self,asset_type, value, comments):
        if len(asset_type) == 40:
            asset_type = asset_type
        elif len(asset_type) == 42:
            asset_type = asset_type.replace("0x","")
        else:
            asset_type = Configure.get("AssetType").get(asset_type.upper())
        hr = self.create_hr()

        code = "{uri}&{hr}&{asset_type}&{value}&{comments}".format(uri=self.wallet.url,
                                                                   hr=hr, asset_type=asset_type,
                                                                   value=str(value),comments=comments)
        base58_code = base58.b58encode(code.encode())
        return "TN{}".format(base58_code)

    @staticmethod
    def decode_payment_code(payment_code):
        if not payment_code.startswith("TN"):
            LOG.error("payment code is not trinity payment")
            return False, None
        base58_code = payment_code[2:]
        code = base58.b58decode(base58_code).decode()
        info = code.split("&",5)
        print(info)
        if len(info) !=5:
            return False, None
        keys=["uri","hr","asset_type","count","comments"]
        result = dict(zip(keys, info))
        return True, json.dumps(result)

    def create_hr(self):
        key = Random.get_random_bytes(32)
        key_string = binascii.b2a_hex(key).decode()
        hr = hash_r(key_string)
        self.HashR[hr] = key_string
        return hr

    @staticmethod
    def verify_hr(hr,r):
        if Payment.HashR.get(hr):
            return True if hash_r(r) == hr else False
        else:
            return False

    def delete_hr(self, hr):
        return self.HashR.pop(hr)


def hash_r(r):
    return hashlib.sha1(r.encode()).hexdigest()

if __name__ == "__main__":
    result = Payment.decode_payment_code("TNJ2dZc36Z4eRSMELP7Bp445PghkEbuRR4yhCcpAa2mTWSRPzzcXJKzu4rJdT7Lp2g5mA"
                                         "8WtUqBCE2wcRJrL9dPvVfWPAKc3Wh9WEyv7YXhm4Jr47Nnqi4nmY2rPaoypr7kzGKHTRb"
                                         "vBQJxF4p65K9p5UqXcfK768gvRHwYxaj9YQYSesSPzeF78JF2XHCBhesw5Kn4z8RyviVg"
                                         "TVhUV2hbozdMETvwx7yvTb6i5R9Kaa8LUyoe1iiZ1SqiMCjKEWUtq")

    print(result)


