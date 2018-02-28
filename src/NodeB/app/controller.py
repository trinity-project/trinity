

from NodeB.app.app import jsonrpc
from NodeB import service


@jsonrpc.method("createMultiSigAddress")
def create_multisig_address(publicKey1,publicKey2,publicKey3):
    return service.createMultiSigContract(publicKey1, publicKey2, publicKey3)




@jsonrpc.method("constructTx")
def construct_tx(addressFrom,addressTo,value,assetId):
    return service.construct_tx(addressFrom, addressTo, value, assetId)

@jsonrpc.method("constructDepositTx")
def construct_deposit_tx(assetId,addressFrom,addressTo1,value1,addressTo2,value2):
    return service.construct_deposit_tx(assetId, addressFrom, addressTo1, value1, addressTo2, value2)


@jsonrpc.method("constructRawTx")
def construct_raw_tx(txData,signature,publicKey):
    return service.construct_raw_tx(txData, signature, publicKey)


@jsonrpc.method("constructDepositRawTx")
def construct_deposit_raw_tx(txData,signature1,signature2,verificationScript):
    return service.construct_deposit_raw_tx(txData, signature1, signature2, verificationScript)


@jsonrpc.method("sign")
def sign(txData,privtKey):
    return service.sign(txData, privtKey)


@jsonrpc.method("multiSign")
def multi_sign(txData,privtKey1,privtKey2,verificationScript):
    return service.multi_sign(txData, privtKey1, privtKey2, verificationScript)


@jsonrpc.method("sendRawTx")
def send_raw_tx(rawTx):
    return service.send_raw_tx(rawTx)


@jsonrpc.method("getBalance")
def get_balance(address):
    return service.get_balance(address)


@jsonrpc.method("confirmTx")
def confirm_tx(txList):
    return service.confirm_tx(txList)

@jsonrpc.method("transferTnc")
def transfer_tnc(addressFrom,addressTo):
    return service.transfer_tnc(addressFrom, addressTo)





@jsonrpc.method("constructDepositTx")
def construct_deposit_tx(assetId,addressFrom,addressTo1,value1,addressTo2,value2):
    return service.construct_deposit_tx(assetId, addressFrom, addressTo1, value1, addressTo2, value2)



@jsonrpc.method("constructDepositRawTx")
def construct_deposit_raw_tx(txData,signature1,signature2,verificationScript):
    return service.construct_deposit_raw_tx(txData, signature1, signature2, verificationScript)