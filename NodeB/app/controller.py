

from app import  jsonrpc
from app import service



@jsonrpc.method("createMultiSigAddress")
def create_multisig_address(publicKey1,publicKey2,publicKey3):
    return service.createMultiSigContract(publicKey1,publicKey2,publicKey3)




@jsonrpc.method("constructTx")
def construct_tx(addressFrom,addressTo,value,assetId):
    return service.construct_tx(addressFrom,addressTo,value,assetId)



@jsonrpc.method("sign")
def sign(txData,privtKey,publicKey):
    return service.sign(txData,privtKey,publicKey)


@jsonrpc.method("multiSign")
def multi_sign(txData,privtKey1,privtKey2,verificationScript):
    return service.multi_sign(txData,privtKey1,privtKey2,verificationScript)


@jsonrpc.method("sendRawTx")
def send_raw_tx(rawTx):
    return service.send_raw_tx(rawTx)


@jsonrpc.method("getBalance")
def get_balance(address):
    return service.get_balance(address)