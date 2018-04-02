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
from wallet.utils import pubkey_to_address
from TX.interface import *
from wallet.ChannelManagement import channel as ch
from sserver.model.base_enum import EnumChannelState
from wallet.Interface.gate_way import send_message
from wallet.utils import sign
from TX.utils import blockheight_to_script
from wallet.BlockChain.monior import register_block, register_monitor
from sserver.model import APIChannel


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
        print("Message Send:  ", message)
        send_message(message)


class RegisterMessage(Message):
    """
    transaction massage：
    { "MessageType":"RegisterChannel",
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
        self.asset_type = self.message_body.get("AssetType")
        self.channel_name = self.message.get("ChannelName")
        self.wallet = wallet

    def handle_message(self):
        # TOdo check deposit
        print("Handle RegisterMessage:   ", self.message)
        founder_pubkey, founder_ip = self.sender.split("@")
        partner_pubkey, partner_ip = self.receiver.split("@")
        founder_address = pubkey_to_address(founder_pubkey)
        partner_address = pubkey_to_address(partner_pubkey)
        APIChannel.add_channel(self.channel_name, founder_pubkey, partner_pubkey,
                               EnumChannelState.INIT.name, 0, self.deposit, 0)
        ch.sync_channel_info_to_gateway(self.channel_name,"AddChannel") # Just For Test

        FounderMessage.create(self.channel_name,partner_pubkey,founder_pubkey,
                              self.asset_type,self.deposit,founder_ip,partner_ip)

class TestMessage(Message):

    def __init__(self, message, wallet):
        super().__init__(message)
        self.wallet= wallet

    def handle_message(self):
        founder = "{}@{}".format(self.wallet.url)
        ch.create_channel(founder, "292929929292929292@10.10.12.1:20332", "TNC", 10)


class CreateTranscation(Message):
    """
    { "MessageType":"CreateTranscation",
    "Receiver":"101010101001001010100101@127.0.0.1:20552",
    "ChannelName":"090A8E08E0358305035709403",
    "MessageBody": {
            "AssetType":"TNC",
            "Value": 20
        }
    }
    """
    def __init__(self, message, wallet):
        super().__init__(message)
        self.wallet= wallet
        self.receiver_pubkey, self.receiver_ip = self.message.get("Receiver").split("@")
        self.channel_name = self.message.get("ChannelName")
        self.asset_type = self.message_body.get("AssetType")
        self.value = self.message_body.get("Value")

    def handle_message(self):
        tx_nonce = TrinityTransaction(self.channel_name, self.wallet).get_latest_nonceid()
        RsmcMessage.create(self.channel_name, self.wallet, self.wallet.pubkey,
                           self.receiver_pubkey, self.value, self.receiver_ip, str(tx_nonce))


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
        res = sign(self.wallet, context)
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
            "RevocableDelivery":"",
            "AssetType":"TNC",
            "Deposit": 10
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
        self.sender_pubkey, self.sender_ip = self.sender.split("@")
        self.receiver_pubkey, self.receiver_ip= self.receiver.split("@")
        self.sender_address = pubkey_to_address(self.sender_pubkey)
        self.receiver_address = pubkey_to_address(self.receiver_pubkey)
        self.asset_type = self.message_body.get("AssetType")
        self.deposit = self.message_body.get("Deposit")

    def handle_message(self):
        print("Handle FounderMessage: ", self.message)
        verify, error = self.verify()
        if verify:
            rdtxid = self.revocable_delivery.get("txId")
            if not self.wallet.LoadStoredData(self.channel_name):
                self.wallet.SaveStoredData(self.channel_name, "{}.data".format(self.channel_name))
                self.transaction.create_tx_file(self.channel_name)
            self.send_responses()
            self.transaction.update_transaction(self.tx_nonce, MonitorTxId=rdtxid)
            if self.transaction.get_tx_nonce("0"):
                txid = self.founder.get("txId")
                ch.Channel.channel(self.channel_name).update_channel(state=EnumChannelState.OPENING.name)
                register_monitor(txid, monitor_founding, self.channel_name, EnumChannelState.OPENED.name)
            if ch.Channel.channel(self.channel_name).src_addr == self.wallet.pubkey:
                deposit = ch.Channel.channel(self.channel_name).get_deposit().get()
                FounderMessage.create(self.channel_name, self.receiver_pubkey,
                                      self.sender_pubkey,self.asset_type, self.deposit, self.receiver_ip)
        else:
            self.send_responses(error = error)

    @staticmethod
    def create(channel_name, self_pubkey, partner_pubkey,asset_type, deposit, partner_ip, gateway_ip):
        print("Channel Create:",channel_name, self_pubkey, partner_pubkey,asset_type, deposit, partner_ip, gateway_ip )
        walletfounder = {
            "pubkey":self_pubkey,
            "deposit":float(deposit)
    }
        walletpartner = {
            "pubkey":partner_pubkey,
            "deposit":float(deposit)
    }

        founder = createFundingTx(walletpartner, walletfounder)

        commitment = createCTX(founder.get("addressFunding"), deposit, deposit, self_pubkey,
                               partner_pubkey, founder.get("scriptFunding"))

        address_self = pubkey_to_address(self_pubkey)

        revocabledelivery = createRDTX(commitment.get("addressRSMC"),address_self, deposit, commitment.get("txId"),
                                       commitment.get("scriptRSMC"))

        message = { "MessageType":"Founder",
                    "Sender": "{}@{}".format(self_pubkey, gateway_ip),
                    "Receiver":"{}@{}".format(partner_pubkey, partner_ip),
                    "TxNonce": 0,
                    "ChannelName":channel_name,
                    "MessageBody": {
                                      "Founder": founder,
                                      "Commitment":commitment,
                                       "RevocableDelivery":revocabledelivery,
                                       "AssetType":asset_type,
                                       "Deposit": deposit
                                      }
                 }
        FounderMessage.send(message)


    def verify(self):
        #Todo verify public key if self
        return True, None

    def send_responses(self, error = None):


        founder_sig = {"txDataSing": self.sign_message(self.founder.get("txData")),
                        "orginalData": self.founder}
        commitment_sig = {"txDataSing": self.sign_message(self.commitment.get("txData")),
                       "orginalData": self.commitment}
        rd_sig = {"txDataSing": self.sign_message(self.revocable_delivery.get("txData")),
                       "orginalData": self.revocable_delivery}
        if not error:
            message_response = { "MessageType":"FounderSign",
                                "Sender": self.receiver,
                                "Receiver":self.sender,
                                 "ChannelName":self.channel_name,
                                "TxNonce": 0,
                                "MessageBody": {"Founder": self.founder,
                                                  "Commitment":self.commitment,
                                                  "RevocableDelivery":self.revocable_delivery,
                                                "AssetType":self.asset_type,
                                                "Deposit":self.deposit
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
                                                  "RevocableDelivery":rd_sig,
                                                "AssetType": self.asset_type,
                                                "Deposit": self.deposit
                                                },
                                }

        FounderMessage.send(message_response)
        print("Send FounderMessage Response",message_response )
        return None



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
        self.asset_type = self.message_body.get("AssetType")
        self.deposit = self.message_body.get("Deposit")
        self.transaction = TrinityTransaction(self.channel_name, self.wallet)

    def handle_message(self):
        print("Handle FounderResponsesMessage:", self.message)
        if self.error:
            return "{} message error"
        verify, error = self.verify()
        if verify:
            if not self.wallet.LoadStoredData(self.channel_name):
                self.wallet.SaveStoredData(self.channel_name, "{}.data".format(self.channel_name))
                self.transaction.create_tx_file(self.channel_name)
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
                ch.Channel.channel(self.channel_name).update_channel(state=EnumChannelState.OPENING.name)
                sender_pubkey, sender_ip = self.sender.split("@")
                receiver_pubkey, receiver_ip = self.receiver.split("@")
                balance = {}.setdefault(sender_pubkey, {}.setdefault(self.asset_type, self.deposit))
                balance.setdefault(receiver_pubkey, {}.setdefault(self.asset_type, self.deposit))
                self.transaction.update_transaction(Balance = balance , State="confirm")
                register_monitor(txid, monitor_founding, self.channel_name)
        return None

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
            "BreachRemedy":"",
            "Value":"",
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
        self.value = self.message_body.get("Value")
        self.asset_type = self.message_body.get("AssetType")
        self.transaction = TrinityTransaction(self.channel_name, self.wallet)

    def handle_message(self):
        print("Handle RsmcMessage :", self.message)
        verify, error = self.verify()
        if verify:
            self.send_responses()
            if self.transaction.get_tx_nonce(self.tx_nonce):
                ctxid = self.commitment.get("txID")
                self.transaction.update_transaction(self.tx_nonce, MonitorTxId=ctxid)
        else:
            self.send_responses(error = error)

    @staticmethod
    def create(channel_name, wallet, sender_pubkey, receiver_pubkey, value, partner_ip,gateway_ip ,tx_nonce, asset_type="TNC",
               breachremedy=False,cli =False,
               router = None, next_router=None):
        transaction = TrinityTransaction(channel_name, wallet)
        founder = transaction.get_founder()
        tx_state = transaction.get_transaction_state()
        sender_balance = transaction.get_balance().get(sender_pubkey)
        receiver_balance = transaction.get_balance().get(receiver_pubkey)
        balance_value = sender_balance.get(asset_type)
        if balance_value < value and tx_state == "pending":
            if cli:
                return False, "No Balance"
            else:
                message = { "MessageType":"CreateTransactionACK",
    "Receiver":"{}@{}".format(receiver_pubkey,partner_ip),
    "ChannelName":channel_name,
    "Error": "No Balance"
    }
        sender_balance = float(balance_value.get(sender_pubkey)) - float(value)
        receiver_balance = float(balance_value.get(receiver_pubkey)) + float(value)
        commitment = createCTX(founder["addressFunding"], sender_balance, receiver_balance,
                               sender_pubkey, receiver_pubkey, founder["scriptRSMC"])

        revocabledelivery = createRDTX(commitment.get("addressRSMC"), pubkey_to_address(sender_pubkey), sender_balance,
                                       commitment.get("txId"),
                                       commitment.get("scriptRSMC"))

        if not breachremedy:
            message = { "MessageType":"Founder",
                    "Sender": "{}@{}".format(sender_pubkey, gateway_ip),
                    "Receiver":"{}@{}".format(receiver_pubkey, partner_ip),
                    "TxNonce": tx_nonce,
                    "ChannelName":channel_name,
                    "MessageBody": {
                                      "Commitment":commitment,
                                       "RevocableDelivery":revocabledelivery,
                                       "AssetType":asset_type,
                                       "Value": value
                                      }
                 }
            if router and next_router:
                message.setdefault("Router", router)
                message.setdefault("NextRouter", next_router)
        else:
            founder = transaction.get_tx_nonce(tx_nonce=str(int(tx_nonce)-1))
            breachremedy = createBRTX(founder["addressFunding"], pubkey_to_address(receiver_pubkey), sender_balance,
                                      commitment["scriptRSMC"])
            breachremedy_sign = sign(wallet, breachremedy.get("txData"))
            message = {"MessageType": "Founder",
                       "Sender": "{}@{}".format(sender_pubkey, gateway_ip),
                       "Receiver": "{}@{}".format(receiver_pubkey, partner_ip),
                       "TxNonce": tx_nonce,
                       "ChannelName": channel_name,
                       "MessageBody": {
                           "BreachRemedy": breachremedy_sign,
                           "AssetType": asset_type,
                           "Value": value
                           }
                       }
            if not transaction.get_tx_nonce(tx_nonce).get("BR"):
                transaction.update_transaction(tx_nonce, BR="waiting")
        RsmcMessage.send(message)
        balance = {}.setdefault(sender_pubkey,{}.setdefault(asset_type, sender_balance))
        balance.setdefault(receiver_pubkey,{}.setdefault(asset_type,receiver_balance))
        transaction.update_transaction(tx_nonce, Balance=balance, State="pending")


    def verify(self):
        return True, None

    def send_responses(self, error = None):
        if not error:
            if self.breach_remedy:
                tx = self.transaction.get_tx_nonce(self.tx_nonce)
                if tx.get("BR") == "waiting":
                    self.transaction.update_transaction(self.tx_nonce, BR=self.breach_remedy)
                else:
                    self.transaction.update_transaction(self.tx_nonce, BR=self.breach_remedy)
                    RsmcMessage.create(self.channel_name,self.wallet,self.receiver_pubkey,self.sender_pubkey,
                                       self.value,self.sender_ip, breachremedy=True)
                    ctx = self.transaction.update_transaction(self.tx_nonce)
                    monitor_ctxid = ctx.get("MonitorTxId")
                    txData = ctx.get("RevocableDelivery").get("orginalData").get("txData")
                    txDataself = self.sign_message(txData)
                    txDataother = self.sign_message(ctx.get("RevocableDelivery").get("txDataSing")),
                    witness = ctx.get("RevocableDelivery").get("orginalData").get("witness_part1")+\
                              ctx.get("RevocableDelivery").get("orginalData").get("witness_part2")
                    register_monitor(monitor_ctxid,monitor_height,txData+witness, txDataother, txDataself)
                    balance = self.transaction.get_balance()
                    self.transaction.update_transaction(State="confirm")
                    ch.Channel.channel(self.channel_name).update_channel(balance=balance)
                    ch.sync_channel_info_to_gateway(self.channel_name, "UpdateChannel")

                    #Todo monitor B transaction
                    #monitor_ctxid = self.transaction.get_tx_nonce(str(int(self.tx_nonce)-1)).get("MonitorTxId")
                    #breach_remedy_sign = self.sign_message(self.breach_remedy.get("txDataSing"))
                    #rawdata =
                    #register_monitor(monitor_ctxid,  record_block, )

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
                print("Send RsmcMessage Response  ",message_response)
        else:
            message_response = { "MessageType":"FounderFail",
                                "Sender": self.receiver,
                                "Receiver":self.sender,
                                "TxNonce": self.tx_nonce,
                                 "ChannelName":self.channel_name,
                                "MessageBody": { "Commitment":self.commitment,
                                                  "RevocableDelivery":self.revocable_delivery,
                                                },
                                "Error": error
                                }
            self.send(message_response)
            print("Send RsmcMessage Response  ", message_response)

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
        print("Handle RsmcResponsesMessage:  ", self.message)
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
        #Todo
        #hctx = createHCTX(senderpubkey,receiverpubkey,HTLCvalue,sender_balance,
        #                 receiver_balance,hashR,founder["addressFunding"],founder["scriptFunding"])
        #hedtx = createHEDTX(hctx["addressHTLC"], receiver_address, HTLCvalue, hctx["HTLCscript"])
        #httx = createHTTX(hctx["addressHTLC"], sender_address, HTLCvalue, hctx["HTLCscript"])
        #message = {"MessageType": "Founder",
        #           "Sender": "{}@{}".format(senderpubkey, gateway_ip),
        #           "Receiver": "{}@{}".format(receiverpubkey, partner_ip),
        #           "TxNonce":tx_nonce ,
        #          "ChannelName": channel_name,
        #          "MessageBody": {
        #               "HCTX": hctx,
        #               "HEDTX": hedtx,
        #               "HTTX": httx
        #                }
        #           }
        #HtlcMessage.send(message)



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


def monitor_founding(height, channel_name, state):
    channel = ch.Channel.channel(channel_name)
    deposit = ch.Channel.get_deposit()
    channel.update_channel(state=state, balance = deposit)
    ch.sync_channel_info_to_gateway(channel_name,"AddChannel")


def monitor_height(height, txdata, signother, signself):
    register_block(str(int(height)+1000),send_rsmcr_transaction,height,txdata,signother, signself)

def send_rsmcr_transaction(height,txdata,signother, signself):
    height_script = blockheight_to_script(height)
    rawdata = txdata.format(blockheight_script=height_script,signOther=signother,signSelf=signself)
    TrinityTransaction.sendrawtransaction(rawdata)
