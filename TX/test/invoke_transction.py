import binascii
import pprint
import time
from neocore.BigInteger import BigInteger
from neocore.Cryptography.Crypto import Crypto
from TX.MyTransaction import InvocationTransaction
from TX.TransactionAttribute import TransactionAttribute, TransactionAttributeUsage
from TX.config import *
from TX.interface import createFundingTx, createCTX, createRDTX, createBRTX
from TX.utils import hex_reverse, ToAddresstHash, int_to_hex, createTxid, pubkeyToAddress

walletSelf= {
    "pubkey":"03ed45d1fdf6dbd5a6e5567b50d2b36b8ae5c1cd0123f26aba000fd3a72d6fbd28",
    "deposit":5
}
walletOther= {
    "pubkey":"03d8f667ff2068751e117cd6dbe3ebe286dbbc7fbb7b1ef0fbf5eb068e8b783a94",
    "deposit":5
}



# funding_tx = createFundingTx(walletSelf=walletSelf, walletOther=walletOther)
#
# self_C_tx = createCTX(addressFunding=funding_tx["addressFunding"], balanceSelf=walletSelf["deposit"],
#                       balanceOther=walletOther["deposit"], pubkeySelf=walletSelf["pubkey"],
#                       pubkeyOther=walletOther["pubkey"], fundingScript=funding_tx["scriptFunding"])
#
# self_RD_tx = createRDTX(addressRSMC=self_C_tx["addressRSMC"], addressSelf=pubkeyToAddress(walletSelf["pubkey"]),
#                         balanceSelf=walletSelf["deposit"], CTxId=self_C_tx["txId"],
#                         RSMCScript=self_C_tx["scriptRSMC"])

# self_BR_tx = createBRTX(addressRSMC=other_C_tx["addressRSMC"], addressOther=pubkeyToAddress(walletSelf["pubkey"]),
#                         balanceSelf=walletSelf["deposit"], RSMCScript=other_C_tx["scriptRSMC"])


# self_BR_tx = createBRTX(addressRSMC="AeLBqqZom1EQpcuPSJn4wLtzJCVZ7azjgF", addressOther=pubkeyToAddress(walletOther["pubkey"]),
#                         balanceSelf=walletSelf["deposit"], RSMCScript="5dc56b6c766b00527ac46c766b51527ac46c766b52527ac46111313532323333313837352e3835373539376c766b53527ac461682953797374656d2e457865637574696f6e456e67696e652e476574536372697074436f6e7461696e65726c766b54527ac46c766b54c361681d4e656f2e5472616e73616374696f6e2e476574417474726962757465736c766b55527ac4616c766b55c36c766b56527ac4006c766b57527ac46258016c766b56c36c766b57c3c36c766b58527ac4616c766b58c36168154e656f2e4174747269627574652e4765744461746161141a3db733023a855ac2077926c60e4c1fb4d5af009c6c766b59527ac46c766b59c3646700616c766b00c3612103ed45d1fdf6dbd5a6e5567b50d2b36b8ae5c1cd0123f26aba000fd3a72d6fbd28ac642f006c766b51c3612103d8f667ff2068751e117cd6dbe3ebe286dbbc7fbb7b1ef0fbf5eb068e8b783a94ac620400006c766b5a527ac462b8006c766b58c36168154e656f2e4174747269627574652e4765744461746161147880ddceb5101a29e05ea09da1ad310539dc8e699c6c766b5b527ac46c766b5bc3644c00616c766b52c36c766b54c3617c653e016c766b5c527ac46c766b5cc36422006c766b52c36c766b00c36c766b51c3615272654a006c766b5a527ac4623700006c766b5a527ac4622c00616c766b57c351936c766b57527ac46c766b57c36c766b56c3c09f639ffe006c766b5a527ac46203006c766b5ac3616c756656c56b6c766b00527ac46c766b51527ac46c766b52527ac4616168184e656f2e426c6f636b636861696e2e4765744865696768746c766b53527ac46c766b00c302e803936c766b53c39f6c766b54527ac46c766b54c36466006c766b51c3612103ed45d1fdf6dbd5a6e5567b50d2b36b8ae5c1cd0123f26aba000fd3a72d6fbd28ac642f006c766b52c3612103d8f667ff2068751e117cd6dbe3ebe286dbbc7fbb7b1ef0fbf5eb068e8b783a94ac620400006c766b55527ac4620e00006c766b55527ac46203006c766b55c3616c75665ec56b6c766b00527ac46c766b51527ac4616c766b00c36168174e656f2e426c6f636b636861696e2e476574426c6f636b6c766b52527ac46c766b52c36168194e656f2e426c6f636b2e4765745472616e73616374696f6e736c766b53527ac46c766b51c361681d4e656f2e5472616e73616374696f6e2e476574417474726962757465736c766b54527ac4616c766b54c36c766b55527ac4006c766b56527ac462d1006c766b55c36c766b56c3c36c766b57527ac4616c766b57c36168154e656f2e4174747269627574652e476574446174616c766b58527ac4616c766b53c36c766b59527ac4006c766b5a527ac46264006c766b59c36c766b5ac3c36c766b5b527ac4616c766b5bc36168174e656f2e5472616e73616374696f6e2e476574486173686c766b58c39c6c766b5c527ac46c766b5cc3640e00516c766b5d527ac4624a00616c766b5ac351936c766b5a527ac46c766b5ac36c766b59c3c09f6393ff616c766b56c351936c766b56527ac46c766b56c36c766b55c3c09f6326ff006c766b5d527ac46203006c766b5dc3616c7566")



# channelInfo=createChannel(walletSelf=walletSelf,walletOther=walletOther)

# pprint.pprint(channelInfo)
# print (channelInfo)
# xx=createRD1ATX(addressA1B="AQfnZ3euLYqaEhdeTEqqqeQVtWYTtFHzFx",addressA="ALcC96eesqb9pQTWSDCQ8afqdyR4woUzhW",balanceA=2)
#
# address_from="ALcC96eesqb9pQTWSDCQ8afqdyR4woUzhW"
# multi_contract=createMultiSigContract(["0299dc85df93fee8ff2230af0418cf8c5000296f0aed514fcc0ab0dd969ce0bdb0","034e9d2751e1fec65a6a42bc097bdf55c7a79762df7d6e970277f46405c376683a"])
pass
# address_from=multi_contract["address"]
# verify_script=createVerifyScript("5221034e9d2751e1fec65a6a42bc097bdf55c7a79762df7d6e970277f46405c376683a2103eb0881d1d64754d50255bf16079ed6cbc3982463a8904cb919422b39178bef3f52ae")
# print ("verify script:",verify_script)
# time_stamp = TransactionAttribute(usage=TransactionAttributeUsage.Remark, data=bytearray.fromhex(hex(int(time.time()))[2:]))
# pre_txid= TransactionAttribute(usage=TransactionAttributeUsage.Remark1, data=bytearray.fromhex(hex_reverse("0xf95bc0f9682df5c74c35c64f9079c9498cc6f1004d72e016bb03c4e419578b8a")))
# outputTo= TransactionAttribute(usage=TransactionAttributeUsage.Remark2, data=bytearray.fromhex("d904f61978b83b706445d2c418e336de4d6261d2"))
# address_hash1=TransactionAttribute(usage=TransactionAttributeUsage.Script, data=ToAddresstHash("AZH8KcoZsgyzbYze6CMYsNdM1UJDQRxGdK").Data)
# address_hash2=TransactionAttribute(usage=TransactionAttributeUsage.Script, data=ToAddresstHash("AdoHFZV8fxnVQBZ881mdGhynjGC3156Skv").Data)
# txAttributes=[address_hash1,time_stamp,pre_txid,outputTo]
#
#
#
# op_data1= create_opdata(address_from="AZH8KcoZsgyzbYze6CMYsNdM1UJDQRxGdK",address_to="AbZNDqwCSZj4XJSGHmbQTSoHofE2PRMurT",value=1,contract_hash=TNC)
# op_data2= create_opdata(address_from="AdoHFZV8fxnVQBZ881mdGhynjGC3156Skv",address_to=address_from,value=1,contract_hash=TNC)
# print (op_data)
# tx=InvocationTransaction()
# tx.Version=1
# tx.Attributes=txAttributes
# tx.Script=binascii.unhexlify(op_data1)
#
# print(tx.get_tx_data())


# time_stamp = TransactionAttribute(usage=TransactionAttributeUsage.Remark, data=bytearray.fromhex(hex(int(time.time()))[2:]))
# address_hash=TransactionAttribute(usage=TransactionAttributeUsage.Script, data=ToAddresstHash("AJAd9ZaZCwLvdktHc1Rs7w3hmpVSBuTKzs").Data)
# outputTo= TransactionAttribute(usage=TransactionAttributeUsage.Remark2, data=ToAddresstHash("AJAd9ZaZCwLvdktHc1Rs7w3hmpVSBuTKzs").Data)
# txAttributes=[address_hash,time_stamp,outputTo]
#
#
#
# op_data= create_opdata(address_from="AJAd9ZaZCwLvdktHc1Rs7w3hmpVSBuTKzs",address_to="ALcC96eesqb9pQTWSDCQ8afqdyR4woUzhW",value=13,contract_hash=TNC)
# tx=InvocationTransaction()
# tx.Version=1
# tx.Attributes=txAttributes
# tx.Script=binascii.unhexlify(op_data)
#
# print(tx.get_tx_data())


# sadf=createRSMCContract(hashSelf="7880ddceb5101a29e05ea09da1ad310539dc8e69",hashOther="1a3db733023a855ac2077926c60e4c1fb4d5af00",pubkeyOther="03d8f667ff2068751e117cd6dbe3ebe286dbbc7fbb7b1ef0fbf5eb068e8b783a94",pubkeySelf="03ed45d1fdf6dbd5a6e5567b50d2b36b8ae5c1cd0123f26aba000fd3a72d6fbd28",magicTimestamp=time.time())
# print (sadf)