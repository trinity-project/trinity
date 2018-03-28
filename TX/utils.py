import binascii

from base58 import b58decode
from neocore.UInt160 import UInt160
from neocore.UInt256 import UInt256
from neocore.BigInteger import BigInteger
from neocore.Cryptography.Crypto import Crypto

def hex_reverse(input):
    tmp=binascii.unhexlify(input[2:])
    be=bytearray(tmp)
    be.reverse()
    output=binascii.hexlify(be).decode()
    return output


def int_to_hex(input):
    return binascii.hexlify(bytes([int(input)])).decode()


def ToAddresstHash(address):

    data = b58decode(address)
    if len(data) != 25:
        raise ValueError('Not correct Address, wrong length.')
    if data[0] != 23:
        raise ValueError('Not correct Coin Version')

    checksum = Crypto.Default().Hash256(data[:21])[:4]
    if checksum != data[21:]:
        raise Exception('Address format error')
    return UInt160(data=data[1:21])


def createVerifyScript(script):
    tmp = hex(int(len(script)/2))[2:]
    if len(tmp) % 2 == 1:
        tmp = "0" + tmp
    be=bytearray (binascii.unhexlify(tmp))
    be.reverse()
    hex_len=binascii.hexlify(be).decode()
    verify_script="".join([hex_len, script])
    return verify_script

def createTxid(txData):
    ba = binascii.unhexlify(txData)
    hash = Crypto.Hash256(ba)
    return "0x"+UInt256(data=hash).ToString()


def createMultiSigAddress(script):
    scriptHash=Crypto.ToScriptHash(script)
    address=Crypto.ToAddress(scriptHash)
    return address

def create_opdata(address_from, address_to, value, contract_hash):
    op_data = ""
    value = binascii.hexlify(BigInteger(value * pow(10, 8)).ToByteArray()).decode()
    scripthash_from = ToAddresstHash(address_from).ToString2()
    scripthash_to = ToAddresstHash(address_to).ToString2()
    method = binascii.hexlify("transfer".encode()).decode()
    invoke_args = [value, scripthash_to, scripthash_from]
    for item in invoke_args:
        op_data += "".join([int_to_hex(len(item) / 2), item])

    op_data += "53"  # PUSH3
    op_data += "c1"  # PACK
    op_data += int_to_hex(len(method) / 2)
    op_data += method
    op_data += "67"  # APPCALL
    op_data += hex_reverse(contract_hash)
    op_data += "f1"  # maybe THROWIFNOT

    return op_data


def createRSMCContract(hashSelf,pubkeySelf,hashOther,pubkeyOther,magicTimestamp):
    magicTimestamp = binascii.hexlify(str(magicTimestamp).encode()).decode()
    length=hex(int(len(magicTimestamp)/2))[2:]
    magicTimestamp=length+magicTimestamp
    contractTemplate="5dc56b6c766b00527ac46c766b51527ac46c766b52527ac461{magicTimestamp}6c766b53527ac46168295379737" \
                     "4656d2e457865637574696f6e456e67696e652e476574536372697074436f6e7461696e65726c766b54527ac46c766b" \
                     "54c361681d4e656f2e5472616e73616374696f6e2e476574417474726962757465736c766b55527ac4616c766b55c36" \
                     "c766b56527ac4006c766b57527ac46258016c766b56c36c766b57c3c36c766b58527ac4616c766b58c36168154e656f" \
                     "2e4174747269627574652e476574446174616114{hashOther}9c6c766b59527ac46c766b59c3646700616c766b00c36121" \
                     "{pubkeySelf}ac642f006c766b51c36121{pubkeyOther}ac620400006c766b5a527ac462b8006c766b58c36168154e656f2e4" \
                     "174747269627574652e476574446174616114{hashSelf}9c6c766b5b527ac46c766b5bc3644c00616c766b52c36c766b5" \
                     "4c3617c653e016c766b5c527ac46c766b5cc36422006c766b52c36c766b00c36c766b51c3615272654a006c766b5a52" \
                     "7ac4623700006c766b5a527ac4622c00616c766b57c351936c766b57527ac46c766b57c36c766b56c3c09f639ffe006" \
                     "c766b5a527ac46203006c766b5ac3616c756656c56b6c766b00527ac46c766b51527ac46c766b52527ac4616168184e" \
                     "656f2e426c6f636b636861696e2e4765744865696768746c766b53527ac46c766b00c302e803936c766b53c39f6c766" \
                     "b54527ac46c766b54c36466006c766b51c36121{pubkeySelf}ac642f006c766b52c36121{pubkeyOther}ac620400006c766b" \
                     "55527ac4620e00006c766b55527ac46203006c766b55c3616c75665ec56b6c766b00527ac46c766b51527ac4616c766" \
                     "b00c36168174e656f2e426c6f636b636861696e2e476574426c6f636b6c766b52527ac46c766b52c36168194e656f2e" \
                     "426c6f636b2e4765745472616e73616374696f6e736c766b53527ac46c766b51c361681d4e656f2e5472616e7361637" \
                     "4696f6e2e476574417474726962757465736c766b54527ac4616c766b54c36c766b55527ac4006c766b56527ac462d1" \
                     "006c766b55c36c766b56c3c36c766b57527ac4616c766b57c36168154e656f2e4174747269627574652e47657444617" \
                     "4616c766b58527ac4616c766b53c36c766b59527ac4006c766b5a527ac46264006c766b59c36c766b5ac3c36c766b5b" \
                     "527ac4616c766b5bc36168174e656f2e5472616e73616374696f6e2e476574486173686c766b58c39c6c766b5c527ac" \
                     "46c766b5cc3640e00516c766b5d527ac4624a00616c766b5ac351936c766b5a527ac46c766b5ac36c766b59c3c09f63" \
                     "93ff616c766b56c351936c766b56527ac46c766b56c36c766b55c3c09f6326ff006c766b5d527ac46203006c766b5dc" \
                     "3616c7566"
    RSMCContract=contractTemplate.format(hashOther=hashOther,pubkeySelf=pubkeySelf,hashSelf=hashSelf,pubkeyOther=pubkeyOther,\
                                         magicTimestamp=magicTimestamp)

    return  {
        "script":RSMCContract,
        "address":createMultiSigAddress(RSMCContract)
    }




def createHTLCContract(futureTimestamp,pubkeySelf,pubkeyOther,hashR):
    futureTimestamp=hex_reverse(hex(int(futureTimestamp)))
    contractTemplate="57c56b6c766b00527ac46c766b51527ac46c766b52527ac4616c766b52c3a76c766b53527ac46168184e656f2e426c6" \
                     "f636b636861696e2e4765744865696768746168184e656f2e426c6f636b636861696e2e4765744865616465726c766b" \
                     "54527ac46c766b54c36168174e656f2e4865616465722e47657454696d657374616d7004{futureTimestamp}9f6c76" \
                     "6b55527ac46c766b55c3648600616c766b00c36121{pubkeySelf}ac644e006c766b51c36121{pubkeyOther}ac6422006c766b5" \
                     "3c36114{hashR}9c620400006c766b56527ac46266006c766b00c36121{pubkeySelf}ac642f006c766b51c36121{pubkeyOther}" \
                     "ac620400006c766b56527ac46203006c766b56c3616c7566"

    HTLCContract=contractTemplate.format(futureTimestamp=futureTimestamp,pubkeySelf=pubkeySelf,pubkeyOther=pubkeyOther,hashR=hashR)


    return  {
        "script":HTLCContract,
        "address":createMultiSigAddress(HTLCContract)
    }



def createMultiSigContract(publicKeyList):
    script="52"
    for item in publicKeyList:
        script+="21"
        script+=item
    script+="52"
    script+="ae"


    address=createMultiSigAddress(script)


    return {
        "script":script,
        "address":address
    }