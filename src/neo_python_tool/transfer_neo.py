"""
Minimal NEO node with custom code in a background thread.

It will log events from all smart contracts on the blockchain
as they are seen in the received blocks.
"""
import json
import threading
import time

import binascii
from base58 import b58decode
from decimal import Decimal
from logzero import logger
from twisted.internet import reactor, task

from neo.Core.Helper import Helper
from neo.Core.TX.Transaction import TransactionOutput, ContractTransaction,TransactionInput
from neo.Core.TX.TransactionAttribute import TransactionAttribute, TransactionAttributeUsage
from neo.IO.MemoryStream import MemoryStream
from neo.Network.NodeLeader import NodeLeader
from neo.Core.Blockchain import Blockchain
from neo.Implementations.Blockchains.LevelDB.LevelDBBlockchain import LevelDBBlockchain
from neo.Prompt.Utils import lookup_addr_str, parse_param
from neo.Settings import settings
from neocore.Cryptography.Crypto import Crypto
from neocore.Fixed8 import Fixed8
from neocore.UInt160 import UInt160
from neocore.UInt256 import UInt256
from neocore.KeyPair import KeyPair
from neo.Implementations.Wallets.peewee.Models import NEP5Token as Nep5TokenModel
from neocore.IO.BinaryWriter import BinaryWriter
from neo.SmartContract.ContractParameterContext import ContractParametersContext
from neo.VM.ScriptBuilder import ScriptBuilder
from neo.Wallets.NEP5Token import NEP5Token
from neo.SmartContract.Contract import Contract
from neocore.Cryptography.Crypto import Crypto
import binascii


asset_type = "neo"
address_from="AV2hTUE7q8tT3ECJnuccHeB6AU2C4CvKi3"
address_to = "ALcC96eesqb9pQTWSDCQ8afqdyR4woUzhW"
amount =1
change=9
preIndex=0
input_txid="2b0cadf194b9f176ba51a6abc13f490ab49fafba4fc1753319d29ba212c151f7"
private_key="c23e3dd5f88591a6b5be66c3c68e8f3e6969d9c67fd2d5f585e577071581e760"
public_key="034e9d2751e1fec65a6a42bc097bdf55c7a79762df7d6e970277f46405c376683a"

def get_asset_id(asset_type):
    assetId = None

    if asset_type.lower() == 'neo':
        assetId = Blockchain.Default().SystemShare().Hash
    elif asset_type.lower() == 'gas':
        assetId = Blockchain.Default().SystemCoin().Hash
    elif Blockchain.Default().GetAssetState(asset_type):
        assetId = Blockchain.Default().GetAssetState(asset_type).AssetId

    return assetId

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

def get_tx_data(tx):
    ms = MemoryStream()
    w = BinaryWriter(ms)
    tx.SerializeUnsigned(w)
    ms.flush()
    tx_data = ms.ToArray().decode()
    return tx_data

def construct_tx():
    assetId=get_asset_id(asset_type)
    scripthash_to=ToScriptHash(address_to)
    scripthash_from=ToScriptHash(address_from)
    f8amount_change = Fixed8.TryParse(change, require_positive=True)
    f8amount = Fixed8.TryParse(amount, require_positive=True)
    preHash=UInt256(data=binascii.unhexlify(hex_reverse(input_txid)))
    input_0=TransactionInput(prevHash=preHash,prevIndex=preIndex)

    output_0 = TransactionOutput(AssetId=assetId, Value=f8amount_change, script_hash=scripthash_from)
    output_1 = TransactionOutput(AssetId=assetId, Value=f8amount, script_hash=scripthash_to)
    data=hex_reverse(scripthash_from.ToString())
    tx = ContractTransaction(outputs=[output_0,output_1],inputs=[input_0])
    tx.Attributes=[TransactionAttribute(usage=TransactionAttributeUsage.Script, data=bytearray.fromhex(data))]
    return tx



def main():
    tx = construct_tx()
    print (tx.ToJson())
    tx_data = get_tx_data(tx)

    signstr =binascii.hexlify(Crypto.Sign(message=tx_data, private_key=private_key)).decode()

    rawtx_data = tx_data + "014140" + signstr + "2321" + public_key + "ac"
    print (rawtx_data)  #waiting for relay
if __name__ == "__main__":
    main()


    # def hex2interger(input):
    #     tmp_list = []
    #     for i in range(0, len(input), 2):
    #         tmp_list.append(input[i:i + 2])
    #     hex_str = "".join(list(reversed(tmp_list)))
    #     output = int(hex_str, 16)
    #
    #     return output
    #
    # print (hex2interger("bfc469dd56932409677278f6b7422f3e1f34481d"))