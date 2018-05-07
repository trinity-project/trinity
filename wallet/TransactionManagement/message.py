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

#coding=utf-8

from wallet.TransactionManagement.transaction import TrinityTransaction
from wallet.utils import pubkey_to_address, get_asset_type_id
from TX.interface import *
from wallet.ChannelManagement import channel as ch
from model.base_enum import EnumChannelState
from wallet.Interface.gate_way import send_message
from wallet.utils import sign,\
    check_onchain_balance, \
    check_max_deposit,\
    check_mix_deposit,\
    check_deposit
from TX.utils import blockheight_to_script
from wallet.BlockChain.monior import register_block, \
    register_monitor
from model import APIChannel
from log import LOG
import json
from wallet.TransactionManagement.payment import Payment

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
        send_message(message)


class RegisterMessage(Message):
    """
    transaction massage:
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
        LOG.info("Handle RegisterMessage: {}".format(json.dumps(self.message)))
        verify, error = self.verify()
        if not verify:
            message = {
                "MessageType": "RegisterChannelFail",
                "Sender": self.receiver,
                "Receiver": self.sender,
                "ChannelName": self.channel_name,
                "MessageBody": {
                    "OrigianlMessage": self.message
                },
                "Error": error
            }
            Message.send(message)
        founder_pubkey, founder_ip = self.sender.split("@")
        partner_pubkey, partner_ip = self.receiver.split("@")
        founder_address = pubkey_to_address(founder_pubkey)
        partner_address = pubkey_to_address(partner_pubkey)
        deposit = {}
        subitem = {}
        subitem.setdefault(self.asset_type, self.deposit)
        deposit[founder_pubkey] = subitem
        deposit[partner_pubkey] = subitem
        APIChannel.add_channel(self.channel_name, self.sender.strip(), self.receiver.strip(),
                               EnumChannelState.INIT.name, 0, deposit)
        FounderMessage.create(self.channel_name,partner_pubkey,founder_pubkey,
                              self.asset_type.upper(),self.deposit,founder_ip,partner_ip)

    def verify(self):
        if self.sender == self.receiver:
            return False, "Not Support Sender is Receiver"
        if self.receiver != self.wallet.url:
            return False, "The Endpoint is Not Me, I am {}".format(self.wallet.url)
        state, error = self.check_balance()
        if not state:
            return state, error
        state, error = self.check_depoist()
        if not state:
            return state, error

        return True, None

    def check_depoist(self):
        state, de = check_deposit(self.deposit)
        if not state:
            if isinstance(de,float):
                return False,"Deposit should be larger than 0 , but give {}".format(str(de))
            else:
                return False,"Deposit Formate error {}".format(de)

        state, maxd = check_max_deposit(self.deposit)
        if not state:
            if isinstance(maxd,float):
                return False, "Deposit is larger than the max, max is {}".format(str(maxd))
            else:
                return False, "Max deposit configure error {}".format(maxd)

        state , mixd = check_mix_deposit(self.deposit)
        if not state:
            if isinstance(mixd,float):
                return False, "Deposit is less than the min, min is {}".format(str(mixd))
            else:
                return False, "Mix deposit configure error {}".format(mixd)

        return True,None

    def check_balance(self):
        if check_onchain_balance(self.wallet.pubkey, self.asset_type, self.deposit):
            return True, None
        else:
            return False, "No Balance OnChain to support the deposit"


class TestMessage(Message):

    def __init__(self, message, wallet):
        super().__init__(message)
        self.wallet= wallet

    def handle_message(self):
        founder = self.wallet.url
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
        self.gateway_ip = self.wallet.url.split("@")[1].strip()

    def handle_message(self):
        tx_nonce = TrinityTransaction(self.channel_name, self.wallet).get_latest_nonceid()
        LOG.info("CreateTransaction: {}".format(str(tx_nonce)))
        RsmcMessage.create(self.channel_name, self.wallet, self.wallet.pubkey,
                           self.receiver_pubkey, self.value, self.receiver_ip, self.gateway_ip,str(tx_nonce))


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
    transaction massage:
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
            "Deposit": 10,
            "RoleIndex":0
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
        self.role_index = self.message_body.get("RoleIndex")
        self.rdtxid = self.revocable_delivery.get("txId")
        self.comments = self.message.get("Comments")

    def _check_transaction_file(self):
        if not self.wallet.LoadStoredData(self.channel_name):
            self.wallet.SaveStoredData(self.channel_name, "{}.data".format(self.channel_name))
            self.transaction.create_tx_file(self.channel_name)

    def _handle_0_message(self):
        self.send_responses(role_index=self.role_index)
        self.transaction.update_transaction(str(self.tx_nonce), Founder = self.founder ,MonitorTxId=self.rdtxid)
        role_index = int(self.role_index) + 1
        FounderMessage.create(self.channel_name, self.receiver_pubkey,
                              self.sender_pubkey, self.asset_type.upper(), self.deposit, self.sender_ip,
                              self.receiver_ip, role_index=role_index, wallet=self.wallet, comments=self.comments)

    def _handle_1_message(self):
        txid = self.founder.get("txId")
        self.send_responses(role_index=self.role_index)
        ch.Channel.channel(self.channel_name).update_channel(state=EnumChannelState.OPENING.name)
        print("Channel Now is Opening")
        register_monitor(txid, monitor_founding, self.channel_name, EnumChannelState.OPENED.name)
        subitem = {}
        subitem.setdefault(self.asset_type.upper(), self.deposit)
        balance = {}
        balance.setdefault(self.sender_pubkey, subitem)
        balance.setdefault(self.receiver_pubkey, subitem)
        self.transaction.update_transaction(str(self.tx_nonce), Balance=balance, State="confirm")

    def handle_message(self):
        LOG.info("Handle FounderMessage: {}".format(str(self.message)))
        verify, error = self.verify()
        if verify:
            self._check_transaction_file()
            if self.role_index == 0:
                return self._handle_0_message()
            elif self.role_index == 1:
                return self._handle_1_message()
            else:
                LOG.error("Not correct role index, expect 0 or 1 but get {}".format(str(self.role_index)))
                return None
        else:
            self.send_responses(self.role_index, error = error)

    @staticmethod
    def create(channel_name, self_pubkey, partner_pubkey,asset_type, deposit, partner_ip,
               gateway_ip,role_index=0, wallet=None, comments= None):
        """

        :param channel_name:
        :param self_pubkey:
        :param partner_pubkey:
        :param asset_type:
        :param deposit:
        :param partner_ip:
        :param gateway_ip:
        :param role_index:
        :param wallet:
        :return:
        """
        walletfounder = {
            "pubkey":self_pubkey,
            "deposit":float(deposit)
    }
        walletpartner = {
            "pubkey":partner_pubkey,
            "deposit":float(deposit)
    }

        transaction = TrinityTransaction(channel_name, wallet)

        if role_index == 0:
            founder = createFundingTx(walletpartner, walletfounder)
        else:
            founder = transaction.get_founder()

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
                                       "AssetType":asset_type.upper(),
                                       "Deposit": deposit,
                                       "RoleIndex":role_index,
                                      },
                    "Comments": comments
                 }
        FounderMessage.send(message)

    def verify(self):
        if self.sender == self.receiver:
            return False, "Not Support Sender is Receiver"
        if self.receiver != self.wallet.url:
            return False, "The Endpoint is Not Me"
        return True, None

    def create_verify_tx(self):
        if self.role_index == 0:
            walletfounder = {
                "pubkey": self.receiver_pubkey,
                "deposit": float(self.deposit)
            }
            walletpartner = {
                "pubkey": self.sender_pubkey,
                "deposit": float(self.deposit)
            }
            Txfounder = createFundingTx(walletpartner,walletfounder)
        elif self.role_index == 1:
            walletfounder = {
                "pubkey": self.sender_pubkey,
                "deposit": float(self.deposit)
            }
            walletpartner = {
                "pubkey": self.receiver_pubkey,
                "deposit": float(self.deposit)
            }
            Txfounder = createFundingTx(walletpartner, walletfounder)

        commitment = createCTX(Txfounder.get("addressFunding"), self.deposit, self.deposit, self.sender_pubkey,
                           self.receiver_pubkey, Txfounder.get("scriptFunding"))

        address_self = pubkey_to_address(self.sender_pubkey)

        revocabledelivery = createRDTX(commitment.get("addressRSMC"), address_self, self.deposit, commitment.get("txId"),
                                   commitment.get("scriptRSMC"))
        return {"Founder":Txfounder,
                "CTx":commitment,
                "RTx":revocabledelivery}


    def send_responses(self, role_index, error = None):
        founder_sig = {"txDataSign": self.sign_message(self.founder.get("txData")),
                        "originalData": self.founder}
        commitment_sig = {"txDataSign": self.sign_message(self.commitment.get("txData")),
                       "originalData": self.commitment}
        rd_sig = {"txDataSign": self.sign_message(self.revocable_delivery.get("txData")),
                       "originalData": self.revocable_delivery}
        if error:
            message_response = { "MessageType":"FounderFail",
                                "Sender": self.receiver,
                                "Receiver":self.sender,
                                 "ChannelName":self.channel_name,
                                "TxNonce": 0,
                                "MessageBody": {"Founder": self.founder,
                                                  "Commitment":self.commitment,
                                                  "RevocableDelivery":self.revocable_delivery,
                                                "AssetType":self.asset_type.upper(),
                                                "Deposit":self.deposit,
                                                "RoleIndex": role_index,
                                                },
                                 "Comments": self.comments,
                                 "Error":error
                                }
        else:
            message_response = { "MessageType":"FounderSign",
                                "Sender": self.receiver,
                                "Receiver":self.sender,
                                 "ChannelName":self.channel_name,
                                "TxNonce": 0,
                                "MessageBody": {"Founder": founder_sig,
                                                  "Commitment":commitment_sig,
                                                  "RevocableDelivery":rd_sig,
                                                "AssetType": self.asset_type.upper(),
                                                "Deposit": self.deposit,
                                                "RoleIndex": role_index,
                                                },
                                 "Comments": self.comments
                                }
        FounderMessage.send(message_response)
        LOG.info("Send FounderMessage Response:  {}".format(json.dumps(message_response )))
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
                   "RevocableDelivery":self.revocabledelivery,
                   "AssetType": self.asset_type.upper(),
                    "Deposit": self.deposit,
                    "RoleIndex": role_index,
                    "Comments"："retry"

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
        self.role_index = self.message_body.get("RoleIndex")
        self.comments = self.message.get("Comments")

    def _check_transaction_file(self):
        if not self.wallet.LoadStoredData(self.channel_name):
            self.wallet.SaveStoredData(self.channel_name, "{}.data".format(self.channel_name))
        if not self.transaction.transaction_exist():
            self.transaction.create_tx_file(self.channel_name)

    def _handle_0_message(self):
        self.transaction.update_transaction("0", Founder=self.founder, Commitment=self.commitment,
                                            RD=self.revocable_delivery)

    def _handle_1_message(self):
        self.transaction.update_transaction("0", Founder=self.founder, Commitment=self.commitment,
                                            RD=self.revocable_delivery)
        result = self.send_founder_raw_transaction()
        if result is True:
            ch.Channel.channel(self.channel_name).update_channel(state=EnumChannelState.OPENING.name)
            print("Channel Now is Opening")
            txid = self.founder.get("originalData").get("txId")
            register_monitor(txid, monitor_founding, self.channel_name, EnumChannelState.OPENED.name)
        else:
            message_response = {"MessageType": "FounderFail",
                                "Sender": self.receiver,
                                "Receiver": self.sender,
                                "ChannelName": self.channel_name,
                                "TxNonce": 0,
                                "MessageBody":self.message_body,
                                "Error": "SendFounderRawTransactionFail",
                                "Comments":"retry" if self.comments != "retry" else None
                                }
            Message.send(message_response)
            ch.Channel.channel(self.channel_name).delete_channel()

    def _handle_error_message(self):
        ch.Channel.channel(self.channel_name).delete_channel()
        #ToDo  Just walk around
        if self.comments == "retry":
            ch.create_channel(self.wallet.url, self.sender, self.asset_type,self.deposit, comments=self.comments,
                              channel_name=self.channel_name)

    def send_founder_raw_transaction(self):
        signdata = self.founder.get("txDataSign")
        txdata = self.founder.get("originalData").get("txData")
        signdata_self = self.sign_message(txdata)

        witnes = self.founder.get("originalData").get("witness").format(signOther=signdata,
                                                                        signSelf=signdata_self)
        return TrinityTransaction.sendrawtransaction(TrinityTransaction.genarate_raw_data(txdata, witnes))

    def update_transaction(self):
        sender_pubkey, sender_ip = self.sender.split("@")
        receiver_pubkey, receiver_ip = self.receiver.split("@")
        subitem = {}
        subitem.setdefault(self.asset_type.upper(), self.deposit)
        balance = {}
        balance.setdefault(sender_pubkey, subitem)
        balance.setdefault(receiver_pubkey, subitem)
        self.transaction.update_transaction(str(self.tx_nonce), Balance=balance, State="confirm")

    def handle_message(self):
        LOG.info("Handle FounderResponsesMessage: {}".format(str(self.message)))
        if self.error:
            LOG.error("FounderResponsesMessage Error: {}" .format(str(self.message)))
            return self._handle_error_message()
        verify, error = self.verify()
        if verify:
            self._check_transaction_file()
            if self.role_index == 0:
                self._handle_0_message()
            elif self.role_index == 1:
                self._handle_1_message()
            else:
                LOG.error("Not correct role index, expect 0 or 1 but get {}".format(str(self.role_index)))
                return None
        return None

    def verify(self):
        if self.sender == self.receiver:
            return False, "Not Support Sender is Receiver"
        if self.receiver != self.wallet.url:
            return False, "The Endpoint is Not Me"
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
            "AssetType":"TNC",
            "RoleIndex":0,
            "Comments":None
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
        self.role_index = self.message_body.get("RoleIndex")
        self.comments = self.message_body.get("Comments")

    def handle_message(self):
        LOG.info("Handle RsmcMessage : {}".format(str(self.message)))
        verify, error = self.verify()
        if verify:
            if self.role_index == 0:
                return self._handle_0_message()
            elif self.role_index == 1:
                return self._handle_1_message()
            elif self.role_index == 2:
                return self._handle_2_message()
            elif self.role_index == 3:
                return self._handle_3_message()
            else:
                LOG.error("Not correct role index, expect 0/1/2/3 but get {}".format(str(self.role_index)))
                return None
        else:
            self.send_responses(error = error)

    @staticmethod
    def create(channel_name, wallet, sender_pubkey, receiver_pubkey, value, partner_ip,gateway_ip ,
               tx_nonce, asset_type="TNC",cli =False,router = None, next_router=None,
               role_index=0, comments=None):
        """

        :param channel_name:
        :param wallet:
        :param sender_pubkey:
        :param receiver_pubkey:
        :param value:
        :param partner_ip:
        :param gateway_ip:
        :param tx_nonce:
        :param asset_type:
        :param breachremedy:
        :param cli:
        :param router:
        :param next_router:
        :param role_index:
        :param comments:
        :return:
        """
        message = RsmcMessage.generateRSMC(channel_name, wallet, sender_pubkey, receiver_pubkey, value, partner_ip,
                                           gateway_ip, tx_nonce, asset_type, cli, router, next_router, role_index, comments)
        LOG.info("Send RsmcMessage role index 1 message  ")
        RsmcMessage.send(message)


    @staticmethod
    def generateRSMC(channel_name, wallet, sender_pubkey, receiver_pubkey, value, partner_ip, gateway_ip ,
               tx_nonce, asset_type="TNC",cli =False,router = None, next_router=None,
               role_index=0, comments=None):
        """

        :param channel_name:
        :param wallet:
        :param sender_pubkey:
        :param receiver_pubkey:
        :param value:
        :param partner_ip:
        :param gateway_ip:
        :param tx_nonce:
        :param asset_type:
        :param breachremedy:
        :param cli:
        :param router:
        :param next_router:
        :param role_index:
        :param comments:
        :return:
        """

        transaction = TrinityTransaction(channel_name, wallet)
        founder = transaction.get_founder()
        LOG.debug("Rsmc Create  founder {}".format(json.dumps(founder)))
        tx_state = transaction.get_transaction_state()
        channel = ch.Channel.channel(channel_name)
        balance = channel.get_balance()
        #balance = transaction.get_balance(str(int(tx_nonce)-1))
        LOG.debug("Rsmc Create get balance {}".format(str(balance)))

        if balance:
            sender_balance = balance.get(sender_pubkey)
            receiver_balance = balance.get(receiver_pubkey)
            balance_value = sender_balance.get(asset_type.upper())
            receiver_balance_value = receiver_balance.get(asset_type.upper())
            LOG.info("RSMC Balance  %s" %(str(balance_value)))
        else:
            balance_value = 0
            receiver_balance_value = 0

        if float(balance_value) < value or tx_state == "pending":
            if cli:
                print("No Balance")
            else:
                message = { "MessageType":"CreateTransactionACK",
                            "Receiver":"{}@{}".format(receiver_pubkey,partner_ip),
                            "ChannelName":channel_name,
                            "Error": "No Balance"
                            }
                return message

        if role_index in [0,2]:
            sender_balance = float(balance_value) - float(value)
            receiver_balance = float(receiver_balance_value) + float(value)
        elif role_index in [1,3]:
            sender_balance = float(balance_value) + float(value)
            receiver_balance = float(receiver_balance_value) - float(value)
        message = {}
        if role_index == 0 or role_index == 1:
            commitment = createCTX(founder["originalData"]["addressFunding"], sender_balance, receiver_balance,
                               sender_pubkey, receiver_pubkey, founder["originalData"]["scriptFunding"])

            revocabledelivery = createRDTX(commitment.get("addressRSMC"), pubkey_to_address(sender_pubkey), sender_balance,
                                       commitment.get("txId"),
                                       commitment.get("scriptRSMC"))
            message = { "MessageType":"Rsmc",
                    "Sender": "{}@{}".format(sender_pubkey, gateway_ip),
                    "Receiver":"{}@{}".format(receiver_pubkey, partner_ip),
                    "TxNonce": tx_nonce,
                    "ChannelName":channel_name,
                    "MessageBody": {
                                      "Commitment":commitment,
                                       "RevocableDelivery":revocabledelivery,
                                       "AssetType":asset_type.upper(),
                                       "Value": value,
                                       "RoleIndex":role_index,
                                       "Comments":comments
                                      }
                 }
            balance = {}
            subitem = {}
            subitem.setdefault(asset_type.upper(), sender_balance)
            balance.setdefault(sender_pubkey, subitem)
            subitem = {}
            subitem.setdefault(asset_type.upper(), receiver_balance)
            balance.setdefault(receiver_pubkey, subitem)
            transaction.update_transaction(str(tx_nonce), Balance=balance, State="pending")
            if router and next_router:
                message.setdefault("Router", router)
                message.setdefault("NextRouter", next_router)

        elif role_index == 2 or role_index == 3:
            tx = transaction.get_tx_nonce(tx_nonce=str(int(tx_nonce)-1))
            if tx.get("Commitment"):
                commitment = tx.get("Commitment").get("originalData")
                rscmcscript = commitment["scriptRSMC"]
            elif tx.get("HCTX"):
                commitment = tx.get("HCTX").get("originalData")
                rscmcscript = commitment["RSMCscript"]

            breachremedy = createBRTX(founder["originalData"]["addressFunding"], pubkey_to_address(receiver_pubkey), sender_balance,
                                      rscmcscript)
            breachremedy_sign = sign(wallet, breachremedy.get("txData"))
            breachremedy_info = {"txDataSign": breachremedy_sign,
                                 "originalData":breachremedy}

            message = {"MessageType": "Rsmc",
                       "Sender": "{}@{}".format(sender_pubkey, gateway_ip),
                       "Receiver": "{}@{}".format(receiver_pubkey, partner_ip),
                       "TxNonce": tx_nonce,
                       "ChannelName": channel_name,
                       "MessageBody": {
                           "BreachRemedy": breachremedy_info,
                           "AssetType": asset_type.upper(),
                           "Value": value,
                           "RoleIndex":role_index,
                           "Comments":comments
                           }
                       }

        return message


    def _check_balance(self, balance):
        pass

    def verify(self):
        return True, None

    def store_monitor_commitement(self):
        ctxid = self.commitment.get("txID")
        self.transaction.update_transaction(str(self.tx_nonce), MonitorTxId=ctxid)

    def _handle_0_message(self):
        LOG.info("RSMC handle 0 message {}".format(json.dumps(self.message)))
        # recorc monitor commitment txid
        self.store_monitor_commitement()
        self.send_responses()

        # send 1 message
        RsmcMessage.create(self.channel_name,self.wallet,
                               self.receiver_pubkey,self.sender_pubkey,
                               self.value,self.sender_ip,self.receiver_ip,self.tx_nonce,
                           asset_type=self.asset_type.upper(), role_index= 1, comments=self.comments)


    def _handle_1_message(self):
        LOG.info("RSMC handle 1 message  {}".format(json.dumps(self.message)))
        self.store_monitor_commitement()
        self.send_responses()

        # send 2 message
        RsmcMessage.create(self.channel_name, self.wallet,
                           self.receiver_pubkey, self.sender_pubkey,
                           self.value, self.sender_ip, self.receiver_ip, self.tx_nonce,
                           asset_type=self.asset_type.upper(), role_index=2, comments=self.comments)

    def _handle_2_message(self):
        # send 3 message
        self.transaction.update_transaction(str(self.tx_nonce), BR=self.breach_remedy)
        RsmcMessage.create(self.channel_name, self.wallet,
                           self.receiver_pubkey, self.sender_pubkey,
                           self.value, self.sender_ip, self.receiver_ip, self.tx_nonce,
                           asset_type=self.asset_type.upper(), role_index=3, comments=self.comments)
        self.confirm_transaction()

    def _handle_3_message(self):
        self.transaction.update_transaction(str(self.tx_nonce), BR=self.breach_remedy)
        self.confirm_transaction()

    def confirm_transaction(self):
        ctx = self.transaction.get_tx_nonce(str(self.tx_nonce))
        monitor_ctxid = ctx.get("MonitorTxId")
        txData = ctx.get("RD").get("originalData").get("txData")
        txDataself = self.sign_message(txData)
        txDataother = self.sign_message(ctx.get("RD").get("txDataSign")),
        witness = ctx.get("RD").get("originalData").get("witness")
        register_monitor(monitor_ctxid, monitor_height, txData + witness, txDataother, txDataself)
        balance = self.transaction.get_balance(str(self.tx_nonce))
        self.transaction.update_transaction(str(self.tx_nonce), State="confirm")
        ch.Channel.channel(self.channel_name).update_channel(balance=balance)
        ch.sync_channel_info_to_gateway(self.channel_name, "UpdateChannel")
        last_tx = self.transaction.get_tx_nonce(str(int(self.tx_nonce) - 1))
        monitor_ctxid = last_tx.get("MonitorTxId")
        btxDataself = ctx.get("BR").get("originalData").get("txData")
        btxsignself = self.sign_message(btxDataself)
        btxsignother =  ctx.get("BR").get("txDataSign")
        bwitness = ctx.get("BR").get("originalData").get("witness")
        try:
            self.confirm_payment()
        except Exception as e:
            LOG.info("Confirm payment error {}".format(str(e)))

        register_monitor(monitor_ctxid, monitor_height, btxDataself + bwitness, btxsignother, btxsignself)

    def confirm_payment(self):
        for key, value in Payment.HashR.items():
            if key == self.comments:
                PaymentAck.create(value[1], key)
                Payment(self.wallet,value[1]).delete_hr(key)

    def send_responses(self, error = None):
        if not error:
            commitment_sig = {"txDataSign": self.sign_message(self.commitment.get("txData")),
                              "originalData": self.commitment}
            rd_sig = {"txDataSign": self.sign_message(self.revocable_delivery.get("txData")),
                      "originalData": self.revocable_delivery}
            message_response = {"MessageType": "RsmcSign",
                                "Sender": self.receiver,
                                "Receiver": self.sender,
                                "TxNonce": self.tx_nonce,
                                "ChannelName": self.channel_name,
                                "MessageBody": {"Commitment": commitment_sig,
                                                "RevocableDelivery": rd_sig,
                                                "Value": self.value,
                                                "RoleIndex": self.role_index,
                                                "Comments":self.comments
                                                }
                                }
            self.send(message_response)
        else:
            message_response = {"MessageType": "RsmcFail",
                                "Sender": self.receiver,
                                "Receiver": self.sender,
                                "TxNonce": self.tx_nonce,
                                "ChannelName": self.channel_name,
                                "MessageBody": {"Commitment": self.commitment,
                                                "RevocableDelivery": self.revocable_delivery,
                                                "Value": self.value,
                                                "RoleIndex": self.role_index,
                                                "Comments":self.comments
                                                },
                                "Error": error
                                }
            self.send(message_response)
            LOG.info("Send RsmcMessage Response {}".format(json.dumps(message_response)))


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
        LOG.info("Handle RsmcResponsesMessage: {}".format(json.dumps(self.message)))
        if self.error:
            return "{} message error"
        verify, error = self.verify()
        if verify:
            # Todo Breach Remedy  Transaction
            self.transaction.update_transaction(str(self.tx_nonce), Commitment=self.commitment,
                                                RD=self.revocable_delivery, BR = self.breach_remedy)
            ctx = self.commitment.get("originalData").get("txId")
            register_monitor(ctx, monitor_founding,self.channel_name, EnumChannelState.CLOSED.name)

    def verify(self):
        return True, None


class RResponse(TransactionMessage):
    """
    { "MessageType":"RResponse",
    "Sender": "9090909090909090909090909@127.0.0.1:20553",
    "Receiver":"101010101001001010100101@127.0.0.1:20552",
    "TxNonce": 0,
    "ChannelName":"3333333333333333333333333333",
    "MessageBody": {
            "HR":hr,
            "R":r,
            "Comments":comments
            }
    }
    """

    def __init__(self,message, wallet):
        super().__init__(message,wallet)
        self.channel_name = message.get("ChannelName")
        self.tx_nonce = message.get("TxNonce")
        self.hr = self.message_body.get("HR")
        self.r = self.message_body.get("R")
        self.count = self.message_body.get("Count")
        self.asset_type = self.message_body.get("AssetType")
        self.comments = self.message_body.get("Comments")
        self.transaction = TrinityTransaction(self.channel_name, self.wallet)

    @staticmethod
    def create(sender, receiver, tx_nonce, channel_name, hr, r, value, asset_type, comments):
        message = { "MessageType":"RResponse",
                    "Sender": sender,
                    "Receiver":receiver,
                    "TxNonce": tx_nonce,
                    "ChannelName":channel_name,
                    "MessageBody": {
                           "HR":hr,
                           "R":r,
                           "Count":value,
                           "AssetType":asset_type,
                           "Comments":comments
                         }
                   }
        Message.send(message)

    def verify(self):
        if self.receiver != self.wallet.url:
            return False, "Not Send to me"
        if Payment.verify_hr(self.hr, self.r):
            return True, None
        else:
            return False, "Not find r"

    def handle_message(self):
        verify, error = self.verify()
        if verify:
            self.transaction.update_transaction(str(self.tx_nonce), State="confirm")
            sender_pubkey, gateway_ip = self.wallet.url.split("@")
            receiver_pubkey, partner_ip = self.sender.split("@")
            tx_nonce = int(self.tx_nonce)+1

            RsmcMessage.create(self.channel_name, self.wallet, sender_pubkey, receiver_pubkey, self.count,
                               partner_ip,gateway_ip ,tx_nonce, asset_type=self.asset_type,
               role_index=0, comments=self.hr)
            payment = Payment.get_hash_history(self.hr)

            if payment:
                channel_name = payment.get("Channel")
                LOG.debug("Payment get channel {}/{}".format(json.dumps(payment), channel_name))
                count = payment.get("Count")
                peer = ch.Channel.channel(channel_name).get_peer(self.wallet.url)
                LOG.info("peer {}".format(peer))
                RResponse.create(self.wallet.url,peer,self.tx_nonce, channel_name,
                                 self.hr, self.r, count, self.asset_type, self.comments)
                transaction = TrinityTransaction(channel_name, self.wallet)
                transaction.update_transaction(str(self.tx_nonce),State="confirm")
                Payment.update_hash_history(self.hr, channel_name, count, "confirm")
            else:
                return None
        else:
            message = { "MessageType":"RResponseAck",
                        "Sender": self.receiver,
                        "Receiver":self.sender,
                        "TxNonce": self.tx_nonce,
                        "ChannelName":self.channel_name,
                        "MessageBody": self.message_body,
                        "Error":error
                     }
            Message.send(message)
        return None


class RResponseAck(TransactionMessage):
    """
     { "MessageType":"RResponseAck",
                        "Sender": self.receiver,
                        "Receiver":self.sender,
                        "TxNonce": self.tx_nonce,
                        "ChannelName":self.channel_name,
                        "MessageBody": self.message_body,
                        "Error":error
                     }
    """

    def __init__(self, message, wallet):
        super().__init__(message,wallet)

    def handle_message(self):
        print(json.dumps(self.message, indent=4))


class HtlcMessage(TransactionMessage):
    """
    { "MessageType":"Htlc",
    "Sender": "9090909090909090909090909@127.0.0.1:20553",
    "Receiver":"101010101001001010100101@127.0.0.1:20552",
    "TxNonce": 0,
    "ChannelName":"3333333333333333333333333333",
    "Router":[],
    "Next":"",
    "MessageBody": {
            "HCTX":"",
            "RDTX":"",
            "HEDTX":"",
            "HTTX":"",
            "HTDTX":"",
            "HTRDTX":"",
            "RoleIndex":"",
            "Comments":""
        }
    }
    """

    def __init__(self, message, wallet):
        super().__init__(message,wallet)
        self.hctx = self.message_body.get("HCTX")
        self.hedtx = self.message_body.get("HEDTX")
        self.rdtx = self.message_body.get("RDTX")
        self.httx = self.message_body.get("HTTX")
        self.htdtx = self.message_body.get("HTDTX")
        self.htrdtx = self.message_body.get("HTRDTX")
        self.role_index = self.message_body.get("RoleIndex")
        self.channel_name = message.get("ChannelName")
        self.value = self.message_body.get("Value")
        self.comments = self.message_body.get("Comments")
        self.router = self.message.get("Router")
        self.next = self.message.get("Next")
        self.count = self.message_body.get("Count")
        self.asset_type = self.message_body.get("AssetType")
        self.hr = self.message_body.get("HashR")
        self.transaction = TrinityTransaction(self.channel_name, self.wallet)

    def handle_message(self):
        verify, error = self.verify()
        if verify:
            if self.role_index ==0:
                self._handle_0_message()
            elif self.role_index ==1:
                self._handle_1_message()
        else:
            self.send_responses(self.role_index,error = error)

    def verify(self):
        return True, None

    def check_if_the_last_router(self):
        return self.wallet.url == self.router[-1][0]


    def _handle_0_message(self):
        Payment.update_hash_history(self.hr, self.channel_name, self.count, "pending")
        self.send_responses(self.role_index)
        self.transaction.update_transaction(str(self.tx_nonce), TxType = "HTLC", HEDTX=self.hedtx,
                                            HR=self.hr,Count=self.count,State ="pending")
        HtlcMessage.create(self.channel_name, self.wallet, self.wallet.url, self.sender, self.count, self.hr,
                           self.tx_nonce, 1, self.asset_type, self.router,
                           self.next, comments=self.comments)

        if self.check_if_the_last_router():
            pass
        else:
            next = self.get_next_router()
            LOG.debug("Get Next Router {}".format(str(next)))
            channels = ch.filter_channel_via_address(self.wallet.url, next, state=EnumChannelState.OPENED.name)
            fee = self.get_fee(self.wallet.url)
            count = float(self.count)-float(fee)
            channel = ch.chose_channel(channels,self.wallet.url.split("@")[0], count, self.asset_type)

            HtlcMessage.create(channel.channel, self.wallet,self.wallet.url, next, count, self.hr,
                               self.tx_nonce, self.role_index,self.asset_type,self.router,
                                   next, comments=self.comments)

    def _handle_1_message(self):
        self.send_responses(self.role_index)
        self.transaction.update_transaction(str(self.tx_nonce), TxType="HTLC", HEDTX=self.hedtx, State="pending")

    def get_fee(self, url):
        router_url = [i[0] for i in self.router]
        index = router_url.index(url)
        try:
            return self.router[index][1]
        except IndexError:
            return 0

    def get_next_router(self):
        router_url = [i[0] for i in self.router]
        index = router_url.index(self.wallet.url)
        try:
            return router_url[index+1]
        except IndexError:
            return None

    @staticmethod
    def create(channel_name, wallet,sender, receiver, HTLCvalue, hashR,tx_nonce, role_index,asset_type,router,
               next_router, comments=None):
        """

        :param channel_name:
        :param wallet:
        :param sender:
        :param receiver:
        :param HTLCvalue:
        :param hashR:
        :param tx_nonce:
        :param role_index:
        :param asset_type:
        :param router:
        :param next_router:
        :param comments:
        :return:
        """
        transaction = TrinityTransaction(channel_name, wallet)
        balance = ch.Channel.channel(channel_name).get_balance()
        print(balance)
        senderpubkey = sender.strip().split("@")[0]
        receiverpubkey = receiver.strip().split("@")[0]
        sender_balance = balance.get(senderpubkey).get(asset_type)
        receiver_balance = balance.get(receiverpubkey).get(asset_type)
        founder = transaction.get_founder()
        if role_index == 0:

            hctx = create_sender_HTLC_TXS(senderpubkey, receiverpubkey, HTLCvalue, sender_balance,
                                      receiver_balance, hashR, founder["originalData"]["addressFunding"],
                                      founder["originalData"]["scriptFunding"])
            transaction.update_transaction(str(tx_nonce), HR=hashR, TxType="HTLC",
                                           Count=HTLCvalue, State="pending")

            hedtx_sign = wallet.SignContent(hctx["HEDTX"]["txData"])
            hedtx = {"txDataSign": hedtx_sign,
                     "originalData": hctx["HEDTX"]}
            hctx["HEDTX"] = hedtx

        elif role_index == 1:
            hctx = create_receiver_HTLC_TXS(senderpubkey, receiverpubkey, HTLCvalue, sender_balance,
                                      receiver_balance, hashR, founder["originalData"]["addressFunding"],
                                      founder["originalData"]["scriptFunding"])

            hetx_sign = wallet.SignContent(hctx["HETX"]["txData"])
            hetx = {"txDataSign": hetx_sign,
                     "originalData": hctx["HETX"]}
            hctx["HETX"] = hetx

            herdtx_sign = wallet.SignContent(hctx["HERDTX"]["txData"])
            herdtx = {"txDataSign": hetx_sign,
                    "originalData": hctx["HERDTX"]}
            hctx["HERDTX"] = herdtx

        else:
            LOG.error("Not correct role index, expect 0/1 but get {}".format(str(role_index)))
            return None

        hctx["RoleIndex"] = role_index
        hctx["Comments"] = comments
        hctx["Count"] = HTLCvalue
        hctx["AssetType"] = asset_type
        hctx["HashR"] = hashR

        message = { "MessageType":"Htlc",
                  "Sender": sender,
                  "Receiver":receiver,
                  "TxNonce": tx_nonce,
                  "ChannelName":channel_name,
                   "Router": router,
                   "Next":next_router,
                  "MessageBody": hctx

        }
        Message.send(message)

        return None

    def _send_0_response(self):
        hctx_sig = {"txDataSign": self.sign_message(self.hctx.get("txData")),
                    "originalData": self.hctx}
        rdtx_sig = {"txDataSign": self.sign_message(self.rdtx.get("txData")),
                    "originalData": self.rdtx}
        httx_sig = {"txDataSign": self.sign_message(self.httx.get("txData")),
                    "originalData": self.httx}
        htrdtx_sig = {"txDataSign": self.sign_message(self.htrdtx.get("txData")),
                      "originalData": self.htrdtx}


        message_response = {"MessageType": "HtlcSign",
                            "Sender": self.receiver,
                            "Receiver": self.sender,
                            "TxNonce": self.tx_nonce,
                            "ChannelName": self.channel_name,
                            "Router": self.router,
                            "MessageBody": {
                                "HCTX": hctx_sig,
                                "RDTX": rdtx_sig,
                                "HTTX": httx_sig,
                                "HTRDTX": htrdtx_sig,
                                "RoleIndex": 0,
                                "Count":self.count,
                                "AssetType": self.asset_type,
                                 "HashR": self.hr
                                }
                            }
        Message.send(message_response)

    def _send_1_response(self):
        hctx_sig = {"txDataSign": self.sign_message(self.hctx.get("txData")),
                    "originalData": self.hctx}
        rdtx_sig = {"txDataSign": self.sign_message(self.rdtx.get("txData")),
                    "originalData": self.rdtx}
        htdtx_sig = {"txDataSign": self.sign_message(self.htdtx.get("txData")),
                    "originalData": self.htdtx}
        message_response = {"MessageType": "HtlcSign",
                            "Sender": self.receiver,
                            "Receiver": self.sender,
                            "TxNonce": self.tx_nonce,
                            "ChannelName": self.channel_name,
                            "Router": self.router,
                            "MessageBody": {
                                "HCTX": hctx_sig,
                                "RDTX": rdtx_sig,
                                "HTDTX": htdtx_sig,
                                "RoleIndex": 1,
                                "Count": self.count,
                                "AssetType": self.asset_type,
                                 "HashR": self.hr
                                 }
                            }
        Message.send(message_response)

    def send_responses(self, role_index, error = None):
        if not error:
            if role_index == 0:
                self._send_0_response()
            elif role_index == 1:
                self._send_1_response()
            else:
                LOG.error("No correct roleindex {}".format(str(role_index)))
        else:
            message_response = { "MessageType":"HtlcFail",
                                "Sender": self.receiver,
                                "Receiver":self.sender,
                                "TxNonce": self.tx_nonce,
                                 "ChannelName": self.channel_name,
                                "MessageBody": self.message_body,
                                "Error": error
                                }
            Message.send(message_response)


class HtlcResponsesMessage(TransactionMessage):
    """
    { "MessageType":"HtlcGSign",
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
        self.hctx = self.message_body.get("HCTX")
        self.rdtx = self.message_body.get("RDTX")
        self.hedtx = self.message_body.get("HEDTX")
        self.htdtx = self.message_body.get("HTDTX")
        self.httx = self.message_body.get("HTTX")
        self.htrdtx = self.message_body.get("HTRDTX")
        self.role_index = self.message_body.get("RoleIndex")
        self.channel_name = message.get("ChannelName")
        self.value = self.message_body.get("Value")
        self.comments = self.message_body.get("Comments")
        self.router = self.message.get("Router")
        self.count = self.message_body.get("Count")
        self.asset_type = self.message_body.get("AssetType")
        self.hr = self.message_body.get("HashR")
        self.transaction = TrinityTransaction(self.channel_name, self.wallet)

    def check_if_the_last_router(self):
        return self.wallet.url == self.router[-1][0]

    def handle_message(self):
        if self.error:
            return "{} message error"
        verify, error = self.verify()
        if verify:
            self.transaction.update_transaction(str(self.tx_nonce), HCTX = self.hctx, HEDTX=self.hedtx, HTTX= self.httx)
            if self.role_index ==1:
                if self.check_if_the_last_router():
                    r = Payment(self.wallet).fetch_r(self.hr)
                    RResponse.create(self.wallet.url, self.sender, self.tx_nonce,
                                     self.channel_name, self.hr, r[0], self.count, self.asset_type, self.comments)
                    self.transaction.update_transaction(str(self.tx_nonce), State="confirm")

    def verify(self):
        return True, None


class SettleMessage(TransactionMessage):
    """
       { "MessageType":"Settle",
      "Sender": self.receiver,
      "Receiver":self.sender,
      "TxNonce": 10,
      "ChannelName":"090A8E08E0358305035709403",
      "MessageBody": {
                   "Commitment":{}

    }
    }
    """

    def __init__(self, message, wallet):
        super().__init__(message, wallet)
        self.settlement = self.message_body.get("Settlement")
        self.channel_name = self.message.get("ChannelName")
        self.transaction = TrinityTransaction(self.channel_name, self.wallet)
        self.tx_nonce = self.message.get("TxNonce")
        self.balance = self.message_body.get("Balance")

    def handle_message(self):
        verify, error = self.verify()
        if verify:
            tx_id = self.settlement.get("txId")
            txdata_sign = self.wallet.SignContent(self.settlement.get("txData"))
            message = { "MessageType":"SettleSign",
                        "Sender": self.receiver,
                        "Receiver":self.sender,
                        "TxNonce": self.tx_nonce,
                        "ChannelName":self.channel_name,
                        "MessageBody": {
                                  "Settlement":{
                                      "txDataSign":txdata_sign,
                                      "originalData":self.settlement
                                  }
                       }
                   }
            Message.send(message)
            ch.Channel.channel(self.channel_name).update_channel(state = EnumChannelState.SETTLING.name)
            register_monitor(tx_id, monitor_founding, self.channel_name, EnumChannelState.CLOSED.name)

        else:
            message = {"MessageType": "SettleSign",
                       "Sender": self.receiver,
                       "Receiver": self.sender,
                       "TxNonce": self.tx_nonce,
                       "ChannelName": self.channel_name,
                       "MessageBody": {
                           "Settlement": self.settlement,
                           "Balance":self.balance
                                    },
                       "Error":error
                       }

            Message.send(message)

    @staticmethod
    def create(channel_name, wallet, sender, receiver, asset_type):
        """
           { "MessageType":"Settle",
          "Sender": sender,
          "Receiver":receiver,
          "TxNonce": 10,
          "ChannelName":"090A8E08E0358305035709403",
          "MessageBody": {
                       "Settlement":{}
                       "Balance":{}
        }
        }
        """
        trans = TrinityTransaction(channel_name, wallet)
        founder = trans.get_founder()
        address_founder = founder["originalData"]["addressFunding"]
        founder_script = founder["originalData"]["scriptFunding"]
        tx_nonce = "-1"
        channel = ch.Channel.channel(channel_name)
        balance = channel.get_balance()
        sender_pubkey = sender.split("@")[0].strip()
        receiver_pubkey = receiver.split("@")[0].strip()
        sender_balance = balance.get(sender_pubkey).get(asset_type.upper())
        receiver_balance = balance.get(receiver_pubkey).get(asset_type.upper())
        settlement_tx = createRefundTX(address_founder,float(sender_balance),receiver_balance,sender_pubkey,receiver_pubkey,
                                    founder_script)

        message = { "MessageType":"Settle",
          "Sender": sender,
          "Receiver":receiver,
          "TxNonce": tx_nonce,
          "ChannelName":channel_name,
          "MessageBody": {"Settlement":settlement_tx,
                          "Balance": balance
                           }
         }
        Message.send(message)
        ch.Channel.channel(channel_name).update_channel(state=EnumChannelState.SETTLING.name)

    def verify(self):
        return True, None


class SettleResponseMessage(TransactionMessage):
    """
       { "MessageType":"SettleSign",
      "Sender": self.receiver,
      "Receiver":self.sender,
      "TxNonce": 10,
      "ChannelName":"090A8E08E0358305035709403",
      "MessageBody": {
                   "Commitment":{}

    }
    }
    """

    def __init__(self, message, wallet):
        super().__init__(message, wallet)
        self.settlement = self.message_body.get("Settlement")
        self.channel_name = self.message.get("ChannelName")
        self.transaction = TrinityTransaction(self.channel_name, self.wallet)
        self.tx_nonce = self.message.get("TxNonce")
        self.balance = self.message_body.get("Balance")

    def handle_message(self):
        verify, error = self.verify()
        if verify:
            tx_data = self.settlement.get("originalData").get("txData")
            tx_data_sign_other = self.settlement.get("txDataSign")
            tx_data_sign_self = self.wallet.SignContent(tx_data)
            tx_id = self.settlement.get("originalData").get("txId")
            witness = self.settlement.get("originalData").get("witness")
            role = ch.Channel.channel(self.channel_name).get_role_in_channel(self.wallet.url)
            if role =="Founder":
                sign_self = tx_data_sign_self
                sign_other = tx_data_sign_other
            elif role == "Partner":
                sign_self = tx_data_sign_other
                sign_other = tx_data_sign_self
            else:
                raise Exception("Not Find the url")
            raw_data = witness.format(signSelf=tx_data_sign_self, signOther=tx_data_sign_other)
            TrinityTransaction.sendrawtransaction(TrinityTransaction.genarate_raw_data(tx_data, raw_data))
            register_monitor(tx_id,monitor_founding,self.channel_name, EnumChannelState.CLOSED.name)

    def verify(self):
        return True, None


class PaymentLink(TransactionMessage):
    """
    {
        "MessageType": "PaymentLink",
        "Sender": "03dc2841ddfb8c2afef94296693315a234026fa8f058c3e4259a04f8be6d540049@106.15.91.150:8089",
        "MessageBody": {
            "Parameter": {
                "Amount": 0,
                "Assets": "TNC",
                "Description": "Description"
            }
        }
    }"""

    def __init__(self, message, wallet):
        super().__init__(message, wallet)

        parameter = self.message_body.get("Parameter")
        self.amount = parameter.get("Amount") if parameter else None
        self.asset = parameter.get("Assets") if parameter else None
        self.comments = parameter.get("Description") if parameter else None

    def handle_message(self):
        pycode = Payment(self.wallet,self.sender).generate_payment_code(get_asset_type_id(self.asset),
                         self.amount, self.comments)
        message = {"MessageType":"PaymentLinkAck",
                   "Receiver":self.sender,
                   "MessageBody": {
                                    "PaymentLink": pycode
                                   },
                   }
        Message.send(message)

        return None


class PaymentAck(TransactionMessage):
    """
        {
        "MessageType": "PaymentAck",
        "Receiver": "03dc2841ddfb8c2afef94296693315a234026fa8f058c3e4259a04f8be6d540049@106.15.91.150:8089",
        "MessageBody": {
            "State": "Success",
            "Hr": "Hr"
        }
    }
    """
    def __init__(self,message, wallet):
        super().__init__(message, wallet)

    @staticmethod
    def create(receiver, hr, state="Success"):
        message = {
        "MessageType": "PaymentAck",
        "Receiver": receiver,
        "MessageBody": {
                         "State": state,
                         "Hr": hr
                         }
                }
        Message.send(message)


def monitor_founding(height, channel_name, state):
    channel = ch.Channel.channel(channel_name)
    deposit = channel.get_deposit()
    channel.update_channel(state=state, balance = deposit)
    ch.sync_channel_info_to_gateway(channel_name,"AddChannel")
    print("Channel is {}".format(state))
    return None


def monitor_height(height, txdata, signother, signself):
    register_block(str(int(height)+1000),send_rsmcr_transaction,height,txdata,signother, signself)


def send_rsmcr_transaction(height,txdata,signother, signself):
    height_script = blockheight_to_script(height)
    rawdata = txdata.format(blockheight_script=height_script,signOther=signother,signSelf=signself)
    TrinityTransaction.sendrawtransaction(rawdata)
