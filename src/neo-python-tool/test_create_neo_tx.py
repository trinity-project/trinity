from base58 import b58decode
from neo.Core.TX.Transaction import TransactionOutput, ContractTransaction,TransactionInput
from neo.Core.TX.TransactionAttribute import TransactionAttribute, TransactionAttributeUsage
from neo.IO.MemoryStream import MemoryStream
from neo.Core.Blockchain import Blockchain
from neocore.Fixed8 import Fixed8
from neocore.UInt160 import UInt160
from neocore.UInt256 import UInt256
from neocore.IO.BinaryWriter import BinaryWriter
from neocore.Cryptography.Crypto import Crypto
import binascii


asset_type = "neo"
address_from="Aco5Kx36gFHuHZphM32PhLpgQi9iyo3iak"
address_to = "AS3ZbQpDbsNRhXqo4WchMfK7iCoA2ADpvh"
amount =10
change=970
preIndex=0
input_txid="2b1977d5ef8410a278f501eda598ae07e50bf933d58ef2b56d4157cd2ac430ad"
private_key="918cdce5458aaac7b8b444b1940855c435f364b99a15755fea031f44d6fa8d36"
public_key="021a3a1a0f298c32fce1d7fdd3246acd29407b4e49d70bedc6ad97be836c4e7b88"

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
    tx_data = get_tx_data(tx)

    signstr =binascii.hexlify(Crypto.Sign(message=tx_data, private_key=private_key)).decode()

    rawtx_data = tx_data + "014140" + signstr + "2321" + public_key + "ac"
    print (rawtx_data)  #waiting for relay




if __name__ == "__main__":
    main()



