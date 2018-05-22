import binascii

import time
from neocore.Fixed8 import Fixed8
from neocore.UInt256 import UInt256

from TX.MyTransaction import TransactionInput, TransactionOutput,ContractTransaction
from TX.TransactionAttribute import TransactionAttribute, TransactionAttributeUsage
from TX.config import *
from TX.utils import hex_reverse, ToAddresstHash






def createInput(preHash,preIndex):
    pre_hash = UInt256(data=binascii.unhexlify(hex_reverse(preHash)))
    return TransactionInput(prevHash=pre_hash, prevIndex=preIndex)

def createOutput(assetId,amount,address):
    if amount==0:
        f8amount=Fixed8.Zero()
    else:
        f8amount = Fixed8.TryParse(amount, require_positive=True)
    assetId = UInt256(data=binascii.unhexlify(hex_reverse(assetId)))
    address_hash=ToAddresstHash(address)
    return TransactionOutput(AssetId=assetId, Value=f8amount, script_hash=address_hash)


address_from="AbZNDqwCSZj4XJSGHmbQTSoHofE2PRMurT"


time_stamp = TransactionAttribute(usage=TransactionAttributeUsage.Remark, data=bytearray.fromhex(hex(int(time.time()))[2:]))
# pre_txid= TransactionAttribute(usage=TransactionAttributeUsage.Remark1, data=bytearray.fromhex(hex_reverse("0x0514e231f7dda3156b626e6b7c6c164fe2cb82398b90364a56c93d53557c2c3f")))
address_hash=TransactionAttribute(usage=TransactionAttributeUsage.Script, data=ToAddresstHash(address_from).Data)
txAttributes=[address_hash,time_stamp]

input0=createInput(preHash="0xc034f207914ce3921a48540fac7a95832223345aab321ced697eb21ba90f4150",preIndex=0)

output0=createOutput(assetId=NEO,amount=1,address="AWJ8pMDHntMoDuqS1ZccxU6XVYvDcPH3J8")
output1=createOutput(assetId=NEO,amount=9,address="AbZNDqwCSZj4XJSGHmbQTSoHofE2PRMurT")

tx = ContractTransaction()
tx.inputs=[input0]
tx.outputs=[output0,output1]
tx.Attributes=txAttributes

print(tx.get_tx_data())