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


class Message(object):
    """

    """

    def __init__(self, message):
        self.message_type = message.get("MessageType")
        self.receiver = message.get("Receiver")
        self.sender = message.get("Sender")
        self.message_body = message.get("MessageBody")
        self.error = message.get("Error")

    def send(self, message):
        pass


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

    def __init__(self, message):
        super().__init__(message)
        self.deposit = self.message_body.get("Deposit")

    def handle_message(self):
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
            ""
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

    def handle_message(self):
        verify, error = self.verify()
        if verify:
            self.send_responses()
        else:
            self.send_responses(error = error)

    @staticmethod
    def create(founder_address,founder_pubkey, partner_address, partner_pubkey, deposit):
        walletfounder = {
            "pubkey":founder_pubkey,
            "address":founder_address,
            "deposit":deposit
    }
        walletpartner = {
            "pubkey":partner_pubkey,
            "address":partner_address,
            "deposit":deposit
    }
        founder = createFundingTx(walletpartner, walletfounder)

        commitment = createCTX(founder.get("addressFunding"),partner_address, deposit, founder_address, deposit,
                               partner_pubkey, founder_pubkey)

        revocabledelivery = createRDTX(commitment.get("addressRSMC"), partner_address, deposit, commitment.get("txId"))
        message = { "MessageType":"Founder",
                    "Sender": "9090909090909090909090909@127.0.0.1:20553",
                    "Receiver":"101010101001001010100101@127.0.0.1:20552",
                    "TxNonce": 0,
                    "ChannelName":"090A8E08E0358305035709403",
                    "MessageBody": {
                                      "Founder": founder,
                                      "Commitment":commitment,
                                       "RevocableDelivery":revocabledelivery
                                      }
                 }
        FounderMessage(message,None).send(message)

    def verify(self):
        return True, None

    def send_responses(self, error = None):
        if not error:
            message_response = { "MessageType":"FounderSign",
                                "Sender": self.receiver,
                                "Receiver":self.sender,
                                 "ChannelName":self.channel_name,
                                "TxNonce": 0,
                                "MessageBody": {"Founder": self.sign_message(self.founder),
                                                  "Commitment":self.sign_message(self.commitment),
                                                  "RevocableDelivery":self.sign_message(self.revocable_delivery)
                                                }
                                }
        else:
            message_response = { "MessageType":"FounderFail",
                                "Sender": self.receiver,
                                "Receiver":self.sender,
                                 "ChannelName":self.channel_name,
                                "TxNonce": 0,
                                "MessageBody": {"Founder": self.founder,
                                                  "Commitment":self.commitment,
                                                  "RevocableDelivery":self.revocable_delivery
                                                },
                                "Error": error
                                }

        self.send(message_response)


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
        if self.verify:
            tx_info = {"Nonce":self.tx_nonce,
                       "Founder":self.founder,
                       "Comitment":self.commitment,
                       "RevocableDelivery":self.revocable_delivery}
            self.transaction.store_transaction(tx_info)

    def verify(self):
        return True, None


class RsmcMessage(TransactionMessage):
    """
    { "MessageType":"Rsmc",
    "Sender": "9090909090909090909090909@127.0.0.1:20553",
    "Receiver":"101010101001001010100101@127.0.0.1:20552",
    "TxNonce": 1,
    "MessageBody": {
            "Commitment":"",
            "RevocableDelivery":"",
            "BreachRemedy":""
        }
    }
    """

    def __init__(self, message, wallet):
        super().__init__(message,wallet)
        self.commitment = self.message_body.get("Commitment")
        self.revocable_delivery = self.message_body.get("RevocableDelivery")
        self.breach_remedy = self.message_body.get("BreachRemedy")

    def handle_message(self):
        verify, error = self.verify()
        if verify:
            self.send_responses()
        else:
            self.send_responses(error = error)

    @staticmethod
    def create(founder_address,founder_pubkey, partner_address, partner_pubkey, deposit):
        walletfounder = {
            "pubkey":founder_pubkey,
            "address":founder_address,
            "deposit":deposit
    }
        walletpartner = {
            "pubkey":partner_pubkey,
            "address":partner_address,
            "deposit":deposit
    }
        founder = createFundingTx(walletpartner, walletfounder)

        commitment = createCTX(founder.get("addressFunding"),partner_address, deposit, founder_address, deposit,
                               partner_pubkey, founder_pubkey)

        revocabledelivery = createRDTX(commitment.get("addressRSMC"), partner_address, deposit, commitment.get("txId"))
        message = { "MessageType":"Founder",
                    "Sender": "9090909090909090909090909@127.0.0.1:20553",
                    "Receiver":"101010101001001010100101@127.0.0.1:20552",
                    "TxNonce": 0,
                    "ChannelName":"090A8E08E0358305035709403",
                    "MessageBody": {
                                      "Founder": founder,
                                      "Commitment":commitment,
                                       "RevocableDelivery":revocabledelivery
                                      }
                 }
        FounderMessage(message,None).send(message)


    def verify(self):
        return True, None

    def send_responses(self, error = None):
        if not error:
            message_response = { "MessageType":"RsmcSign",
                                "Sender": self.receiver,
                                "Receiver":self.sender,
                                "TxNonce": self.tx_nonce,
                                "MessageBody": { "Commitment":self.sign_message(self.commitment),
                                                  "RevocableDelivery":self.sign_message(self.revocable_delivery),
                                                 "BreachRemedy":self.sign_message(self.breach_remedy),
                                                }
                                }
        else:
            message_response = { "MessageType":"FounderFail",
                                "Sender": self.receiver,
                                "Receiver":self.sender,
                                "TxNonce": self.tx_nonce,
                                "MessageBody": { "Commitment":self.commitment,
                                                  "RevocableDelivery":self.revocable_delivery,
                                                 "BreachRemedy":self.breach_remedy,
                                                },
                                "Error": error
                                }

        self.send(message_response)


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
        if self.verify:
            tx_info = {"Nonce":self.tx_nonce,
                       "BreachRemedy":self.breach_remedy,
                       "Commitment":self.commitment,
                       "RevocableDelivery": self.revocable_delivery}
            self.transaction.store_transaction(tx_info)

    def verify(self):
        return True, None

class HtlcMessage(TransactionMessage):
    """
    { "MessageType":"Htlc",
    "Sender": "9090909090909090909090909@127.0.0.1:20553",
    "Receiver":"101010101001001010100101@127.0.0.1:20552",
    "TxNonce": 0,
    "MessageBody": {
            "Commitment":"",
            "RevocableDelivery":"",
            "BreachRemedy":""
        }
    }
    """

    def __init__(self, message, wallet):
        super().__init__(message,wallet)
        self.commitment = self.message_body.get("Commitment")
        self.revocable_delivery = self.message_body.get("RevocableDelivery")
        self.breach_remedy = self.message_body.get("BreachRemedy")

    def handle_message(self):
        verify, error = self.verify()
        if verify:
            self.send_responses()
        else:
            self.send_responses(error = error)

    def verify(self):
        return True, None

    def send_responses(self, error = None):
        if not error:
            message_response = { "MessageType":"RsmcSign",
                                "Sender": self.receiver,
                                "Receiver":self.sender,
                                "TxNonce": self.tx_nonce,
                                "MessageBody": { "Commitment":self.commitment,
                                                  "RevocableDelivery":self.revocable_delivery,
                                                 "BreachRemedy":self.breach_remedy,
                                                }
                                }
        else:
            message_response = { "MessageType":"FounderFail",
                                "Sender": self.receiver,
                                "Receiver":self.sender,
                                "TxNonce": 0,
                                "MessageBody": { "Commitment":self.commitment,
                                                  "RevocableDelivery":self.revocable_delivery,
                                                 "BreachRemedy":self.breach_remedy,
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
        self.breach_remedy = self.message_body.get("BreachRemedy")
        self.commitment = self.message_body.get("Commitment")
        self.revocable_delivery = self.message_body.get("RevocableDelivery")
        self.transaction = TrinityTransaction(self.channel_name, self.wallet)

    def handle_message(self):
        if self.error:
            return "{} message error"
        if self.verify:
            tx_info = {"Nonce":self.tx_nonce,
                       "BreachRemedy":self.breach_remedy,
                       "Commitment":self.commitment,
                       "RevocableDelivery": self.revocable_delivery}
            self.transaction.store_transaction(tx_info)

    def verify(self):
        return True, None



