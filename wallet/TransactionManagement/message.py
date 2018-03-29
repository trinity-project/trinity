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
from wallet.TransactionManagement.transaction import TrinityTransaction
from neo.Core.Helper import Helper
from wallet.utils import pubkey_to_address
from TX.interface import *
from wallet.ChannelManagement import channel as ch
from sserver.model.channel_model import APIChannel

from wallet.configure import Configure
GateWayIP = Configure["GatewayIP"]
def register_monitor(*args):
    pass


class Message(object):
    """

    """

    def __init__(self, message):
        self.message = message
        self.message_type = message.get("MessageType")
        self.receiver = message.get("Receiver")
        self.sender = message.get("Sender")
        self.message_body = message.get("MessageBody")
        self.error = message.get("Error")

    @staticmethod
    def send(message):
        print(message)


class RegisterMessage(Message):
    """
    transaction massage：
    { "MessageType":"RegisterMessage",
    "Sender": "9090909090909090909090909@127.0.0.1:20553",
    "Receiver":"101010101001001010100101@127.0.0.1:20552",
    "ChannelName":"090A8E08E0358305035709403",
    "MessageBody": {
            ""
            "AssetType": "",
            "Deposit":"",
        }
    }
    """

    def __init__(self, message, wallet):
        super().__init__(message)
        self.deposit = self.message_body.get("Deposit")
        self.wallet = wallet

    def handle_message(self):
        if not self.wallet:
            print("No Wallet Open")
            return
        founder_pubkey = self.sender.split("@")[0]
        partner_pubkey = self.receiver.split("@")[0]
        founder_address = pubkey_to_address(founder_pubkey)
        partner_address = pubkey_to_address(partner_pubkey)

        FounderMessage.create(founder_address,founder_pubkey, partner_address, partner_pubkey, self.deposit)

class TransactionMessage(Message):
    """

    """

    def __init__(self, message, wallet):
        super().__init__(message)
        self.wallet = wallet
        self.tx_nonce = message.get("TxNonce")

    def verify(self,**kwargs):
        pass

    def sign_message(self, context):
        """
        ToDo
        :param context:
        :return:
        """
        keypair = self.wallet.LoadKeyPairs()[0]
        res = Helper.Sign(context, keypair)
        return res


class FounderMessage(TransactionMessage):
    """
    transaction massage：
    { "MessageType":"Founder",
    "Sender": "9090909090909090909090909@127.0.0.1:20553",
    "Receiver":"101010101001001010100101@127.0.0.1:20552",
    "TxNonce": 0,
    "ChannelName":"090A8E08E0358305035709403",
    "MessageBody": {
            "Founder": "",
            "Commitment":"",
            "RevocableDelivery":""
        }
    }
    """

    def __init__(self, message, wallet=None):
        super().__init__(message,wallet)
        self.channel_name = message.get("ChannelName")
        self.founder = self.message_body.get("Founder")
        self.commitment = self.message_body.get("Commitment")
        self.revocable_delivery = self.message_body.get("RevocableDelivery")
        self.transaction = TrinityTransaction(self.channel_name, self.wallet)
        self.sender_pubkey = self.sender.split("@")[0]
        self.receiver_pubkey = self.receiver.split("@")[0]
        self.sender_address = pubkey_to_address(self.sender_pubkey)
        self.receiver_address = pubkey_to_address(self.receiver_pubkey)
        self.transaction = TrinityTransaction(self.channel_name, self.wallet)

    def handle_message(self):
        verify, error = self.verify()
        rdtxid= self.revocable_delivery.get("txId")
        if verify:
            self.send_responses()
            tx = self.transaction.read_transaction()
            for t in tx:
                if t.get("MessageType") == "Founder":
                    break
            else:
                FounderMessage.create(self.channel_name, self.receiver_pubkey,
                                      self.sender_pubkey, self.wallet)


        else:
            self.send_responses(error = error)

    @staticmethod
    def create(channel_name, self_pubkey, partner_pubkey, deposit, partner_ip):
        walletfounder = {
            "pubkey":self_pubkey,
            "deposit":deposit
    }
        walletpartner = {
            "pubkey":partner_pubkey,
            "deposit":deposit
    }
        founder = createFundingTx(walletpartner, walletfounder)

        commitment = createCTX(founder.get("addressFunding"), deposit, deposit, self_pubkey,
                               partner_pubkey, founder.get("scriptFunding"))
        address_self = pubkey_to_address(self_pubkey)
        revocabledelivery = createRDTX(commitment.get("addressRSMC"),address_self, deposit, commitment.get("txId"),
                                       commitment.get("scriptRSMC"))
        message = { "MessageType":"Founder",
                    "Sender": "{}@{}".format(self_pubkey, GateWayIP),
                    "Receiver":"{}@{}".format(partner_pubkey, partner_ip),
                    "TxNonce": 0,
                    "ChannelName":channel_name,
                    "MessageBody": {
                                      "Founder": founder,
                                      "Commitment":commitment,
                                       "RevocableDelivery":revocabledelivery
                                      }
                 }
        FounderMessage.send(message)


    def verify(self):
        return True, None

    def send_responses(self, error = None):
        founder_sig = {"txDataSing": self.sign_message(self.founder.get("txData")),
                        "orginalData": self.founder}
        commitment_sig = {"txDataSing": self.sign_message(self.commitment.get("txData")),
                       "orginalData": self.commitment}
        rd_sig = {"txDataSing": self.sign_message(self.revocable_delivery.get("txData")),
                       "orginalData": self.revocable_delivery}
        if error:
            message_response = { "MessageType":"FounderSign",
                                "Sender": self.receiver,
                                "Receiver":self.sender,
                                 "ChannelName":self.channel_name,
                                "TxNonce": 0,
                                "MessageBody": {"Founder": self.founder,
                                                  "Commitment":self.commitment,
                                                  "RevocableDelivery":self.revocable_delivery
                                                },
                                 "Error":error
                                }
        else:
            message_response = { "MessageType":"FounderFail",
                                "Sender": self.receiver,
                                "Receiver":self.sender,
                                 "ChannelName":self.channel_name,
                                "TxNonce": 0,
                                "MessageBody": {"Founder": founder_sig,
                                                  "Commitment":commitment_sig,
                                                  "RevocableDelivery":rd_sig
                                                },
                                }

        FounderMessage.send(message_response)



class FounderResponsesMessage(TransactionMessage):
    """
    { "MessageType":"FounderSign",
      "Sender": self.receiver,
      "Receiver":self.sender,
      "TxNonce": 0,
      "ChannelName":"090A8E08E0358305035709403",
      "MessageBody": {"founder": self.founder,
                   "Commitment":self.commitment,
                   "RevocableDelivery":self.revocabledelivery
                    }
    }
    """
    def __init__(self, message, wallet):
        super().__init__(message, wallet)
        self.channel_name = message.get("ChannelName")
        self.founder = self.message_body.get("Founder")
        self.commitment = self.message_body.get("Commitment")
        self.revocable_delivery = self.message_body.get("RevocableDelivery")
        self.transaction = TrinityTransaction(self.channel_name, self.wallet)

    def handle_message(self):
        if self.error:
            return "{} message error"
        verify, error = self.verify()
        if verify:
            self.transaction.update_transaction("0", Founder=self.founder, Commitment=self.commitment,
                                                RD = self.revocable_delivery)
            if ch.Channel.channel(self.channel_name).src_addr == self.wallet.address:
                signdata = self.founder.get("txDataSing")
                txdata = self.founder.get("orginalData").get("txData")
                txid = self.founder.get("orginalData").get("txId")
                signdata_self = self.sign_message(signdata)
                witnes = self.founder.get("orginalData").get("witness").format(signOther=signdata,
                                                                               signSelf=signdata_self)
                TrinityTransaction.sendrawtransaction(TrinityTransaction.genarate_raw_data(txdata, witnes))
                register_monitor(txid, "monitor_founding", self.channel_name)

    def verify(self):
        return True, None


class RsmcMessage(TransactionMessage):
    """
    { "MessageType":"Rsmc",
    "Sender": "9090909090909090909090909@127.0.0.1:20553",
    "Receiver":"101010101001001010100101@127.0.0.1:20552",
    "TxNonce": 1,
    "ChannelName":"902ae9090232048575",
    "MessageBody": {
            "Commitment":"",
            "RevocableDelivery":"",
            "BreachRemedy":""
        }
    }
    """

    def __init__(self, message, wallet):
        super().__init__(message,wallet)
        self.channel_name = message.get("ChannelName")
        self.commitment = self.message_body.get("Commitment")
        self.revocable_delivery = self.message_body.get("RevocableDelivery")
        self.breach_remedy = self.message_body.get("BreachRemedy")
        self.transaction = TrinityTransaction(self.channel_name, self.wallet)
        self.sender_pubkey, self.sender_ip= self.sender.split("@")
        self.receiver_pubkey, self.receiver_ip = self.receiver.split("@")
        self.sender_address = pubkey_to_address(self.sender_pubkey)
        self.receiver_address = pubkey_to_address(self.receiver_pubkey)
        self.value = self.message_body.get("value")
        self.transaction = TrinityTransaction(self.channel_name, self.wallet)

    def handle_message(self):
        verify, error = self.verify()
        if verify:
            self.send_responses()
            ctxid = self.commitment.get("txID")
            self.transaction.update_transaction(self.tx_nonce, MonitorTxId=ctxid)
        else:
            self.send_responses(error = error)

    @staticmethod
    def create(channel_name, wallet, sender_pubkey, receiver_pubkey, value, partner_ip, tx_nonce,breachremedy=False,):
        transaction = TrinityTransaction(channel_name, wallet)
        founder = transaction.get_founder()
        balance = transaction.get_balance()
        sender_address = pubkey_to_address(sender_pubkey)
        receiver_address = pubkey_to_address(receiver_pubkey)
        sender_balance = int(balance.get(sender_address)) - value
        receiver_balance = int(balance.get(receiver_address)) -value
        commitment = createCTX(founder["addressFunding"], sender_balance, receiver_balance,
                               sender_pubkey, receiver_pubkey, founder["scriptRSMC"])
        revocabledelivery = createRDTX(commitment.get("addressRSMC"), sender_address, sender_balance,
                                       commitment.get("txId"),
                                       commitment.get("scriptRSMC"))

        if not breachremedy:
            message = { "MessageType":"Founder",
                    "Sender": "{}@{}".format(sender_pubkey, GateWayIP),
                    "Receiver":"{}@{}".format(receiver_pubkey, partner_ip),
                    "TxNonce": tx_nonce,
                    "ChannelName":channel_name,
                    "MessageBody": {
                                      "Commitment":commitment,
                                       "RevocableDelivery":revocabledelivery,
                                       "value": value
                                      }
                 }
        else:
            founder = transaction.get_tx_nonce(tx_nonce=str(int(tx_nonce)-1))
            breachremedy = createBRTX(founder["addressFunding"], receiver_address, sender_balance,
                                      commitment["scriptRSMC"])
            message = {"MessageType": "Founder",
                       "Sender": "{}@{}".format(sender_pubkey, GateWayIP),
                       "Receiver": "{}@{}".format(receiver_pubkey, partner_ip),
                       "TxNonce": tx_nonce,
                       "ChannelName": channel_name,
                       "MessageBody": {
                           "BreachRemedy": breachremedy
                           }
                       }
            if not transaction.get_tx_nonce(tx_nonce).get("BR"):
                transaction.update_transaction(tx_nonce, BR="waiting")
        RsmcMessage.send(message)


    def verify(self):
        return True, None

    def send_responses(self, error = None):
        if not error:
            if self.breach_remedy:
                tx = self.transaction.get_tx_nonce(self.tx_nonce)
                if tx.get("BR") == "waiting":
                    self.transaction.update_transaction(self.tx_nonce, BR=self.breach_remedy)
                    #Todo register_monitor(self.breach_remedy.get("orginalData").get("txId"), "send_rawtrans", )
                else:
                    self.transaction.update_transaction(self.tx_nonce, BR=self.breach_remedy)
                    RsmcMessage.create(self.channel_name,self.wallet,self.receiver_pubkey,self.sender_pubkey,
                                       self.value,self.sender_ip, breachremedy=True)

            elif self.commitment and self.revocable_delivery:
                commitment_sig = {"txDataSing": self.sign_message(self.commitment.get("txData")),
                              "orginalData": self.commitment}
                rd_sig = {"txDataSing": self.sign_message(self.revocable_delivery.get("txData")),
                      "orginalData": self.revocable_delivery}

                message_response = { "MessageType":"RsmcSign",
                                "Sender": self.receiver,
                                "Receiver":self.sender,
                                "TxNonce": self.tx_nonce,
                                 "ChannelName":self.channel_name,
                                "MessageBody": { "Commitment":commitment_sig,
                                                  "RevocableDelivery":rd_sig,
                                                }
                                }
                self.send(message_response)
        else:
            message_response = { "MessageType":"FounderFail",
                                "Sender": self.receiver,
                                "Receiver":self.sender,
                                "TxNonce": self.tx_nonce,
                                 "ChannelName":self.channel_name,
                                "MessageBody": { "Commitment":self.commitment,
                                                  "RevocableDelivery":self.revocable_delivery,
                                                 "BreachRemedy":self.breach_remedy,
                                                },
                                "Error": error
                                }
            self.send(message_response)

        if not self.transaction.get_tx_nonce(self.tx_nonce):
            RsmcMessage.create(self.channel_name,self.wallet,
                               self.receiver_pubkey,self.sender_address,
                               self.value,self.tx_nonce,self.sender_ip)


class RsmcResponsesMessage(TransactionMessage):
    """
    { "MessageType":"RsmcSign",
      "Sender": self.receiver,
      "Receiver":self.sender,
      "TxNonce": 0,
      "ChannelName":"090A8E08E0358305035709403",
      "MessageBody": {
                   "Commitment":{}
                   "RevocableDelivery":"
                   "BreachRemedy":""
                    }
    }
    """
    def __init__(self, message, wallet):
        super().__init__(message, wallet)
        self.channel_name = message.get("ChannelName")
        self.breach_remedy = self.message_body.get("BreachRemedy")
        self.commitment = self.message_body.get("Commitment")
        self.revocable_delivery = self.message_body.get("RevocableDelivery")
        self.transaction = TrinityTransaction(self.channel_name, self.wallet)

    def handle_message(self):
        if self.error:
            return "{} message error"
        verify, error = self.verify()
        if verify:
            self.transaction.update_transaction(self.tx_nonce, Commitment=self.commitment,
                                                RD=self.revocable_delivery, BR = self.breach_remedy)

    def verify(self):
        return True, None

class HtlcMessage(TransactionMessage):
    """
    { "MessageType":"Htlc",
    "Sender": "9090909090909090909090909@127.0.0.1:20553",
    "Receiver":"101010101001001010100101@127.0.0.1:20552",
    "TxNonce": 0,
    "ChannelName":"3333333333333333333333333333",
    "MessageBody": {
            "HCTX":"",
            "HEDTX":"",
            "HTTX":""
        }
    }
    """

    def __init__(self, message, wallet):
        super().__init__(message,wallet)
        self.hctx = self.message_body.get("HCTX")
        self.hedtx = self.message_body.get("HEDTX")
        self.httx = self.message_body.get("HTTX")
        self.channel_name = message.get("ChannelName")

    def handle_message(self):
        verify, error = self.verify()
        if verify:
            self.send_responses()
        else:
            self.send_responses(error = error)

    def verify(self):
        return True, None

    @staticmethod
    def create(channel_name, wallet,senderpubkey, receiverpubkey, HTLCvalue, hashR,tx_nonce,partner_ip):
        founder = TrinityTransaction(channel_name, wallet)
        balance = ch.Channel.channel(channel_name).get_balance()
        sender_address = pubkey_to_address(senderpubkey)
        receiver_address = pubkey_to_address(receiverpubkey)
        sender_balance = balance.get(sender_address)
        receiver_balance = balance.get(receiver_address)
        hctx = createHCTX(senderpubkey,receiverpubkey,HTLCvalue,sender_balance,
                          receiver_balance,hashR,founder["addressFunding"],founder["scriptFunding"])
        hedtx = createHEDTX(hctx["addressHTLC"], receiver_address, HTLCvalue, hctx["HTLCscript"])
        httx = createHTTX(hctx["addressHTLC"], sender_address, HTLCvalue, hctx["HTLCscript"])
        message = {"MessageType": "Founder",
                   "Sender": "{}@{}".format(senderpubkey, GateWayIP),
                   "Receiver": "{}@{}".format(receiverpubkey, partner_ip),
                   "TxNonce":tx_nonce ,
                   "ChannelName": channel_name,
                   "MessageBody": {
                       "HCTX": hctx,
                       "HEDTX": hedtx,
                       "HTTX": httx
                        }
                   }
        HtlcMessage.send(message)



    def send_responses(self, error = None):
        if not error:
            hctx_sig = {"txDataSing": self.sign_message(self.hctx.get("txData")),
                                "orginalData": self.hctx}
            hedtx_sig = {"txDataSing": self.sign_message(self.hedtx.get("txData")),
                              "orginalData": self.hedtx}
            httx_sig = {"txDataSing": self.sign_message(self.httx.get("txData")),
                      "orginalData": self.httx}

            message_response = { "MessageType":"HtlcSign",
                                "Sender": self.receiver,
                                "Receiver":self.sender,
                                "TxNonce": self.tx_nonce,
                                 "ChannelName": self.channel_name,
                                "MessageBody": {
                                                 "HCTX": hctx_sig,
                                                 "HEDTX": hedtx_sig,
                                                 "HTTX": httx_sig
                                                  }
                                }
        else:
            message_response = { "MessageType":"FounderFail",
                                "Sender": self.receiver,
                                "Receiver":self.sender,
                                "TxNonce": self.tx_nonce,
                                 "ChannelName": self.channel_name,
                                "MessageBody": {
                                                 "HCTX": self.hctx,
                                                 "HEDTX": self.hedtx,
                                                 "HTTX": self.httx
                                                  },
                                "Error": error
                                }
        self.send(message_response)


class HtlcResponsesMessage(TransactionMessage):
    """
    { "MessageType":"RsmcSign",
      "Sender": self.receiver,
      "Receiver":self.sender,
      "TxNonce": 0,
      "ChannelName":"090A8E08E0358305035709403",
      "MessageBody": {
                   "Commitment":{}
                   "RevocableDelivery":"
                   "BreachRemedy":""
                    }
    }
    """
    def __init__(self, message, wallet):
        super().__init__(message, wallet)
        self.channel_name = message.get("ChannelName")
        self.hctx = self.message_body.get("HCTX")
        self.hedtx = self.message_body.get("HEDTX")
        self.httx = self.message_body.get("HTTX")
        self.transaction = TrinityTransaction(self.channel_name, self.wallet)

    def handle_message(self):
        if self.error:
            return "{} message error"
        verify, error = self.verify()
        if verify:
            self.transaction.update_transaction(self.tx_nonce, HCTX = self.hctx, HEDTX=self.hedtx, HTTX= self.httx)


    def verify(self):
        return True, None



