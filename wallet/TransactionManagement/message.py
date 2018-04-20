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
from wallet.utils import pubkey_to_address, get_asset_type_id
from TX.interface import *
from wallet.ChannelManagement import channel as ch
from sserver.model.base_enum import EnumChannelState
from wallet.Interface.gate_way import send_message
from wallet.utils import sign
from TX.utils import blockheight_to_script
from wallet.BlockChain.monior import register_block, register_monitor
from sserver.model import APIChannel
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
        LOG.info("Message Send:  {}".format(json.dumps(message)))
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
        LOG.info("Handle RegisterMessage: {}".format(json.dumps(self.message)))
        verify, error = self.verify()
        if not verify:
            return error
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
            return False, "The Endpoint is Not Me"
        return True, None


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
                              self.receiver_ip, role_index=role_index, wallet=self.wallet)

    def _handle_1_message(self):
        txid = self.founder.get("txId")
        self.send_responses(role_index=self.role_index)
        ch.Channel.channel(self.channel_name).update_channel(state=EnumChannelState.OPENING.name)
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
               gateway_ip,role_index=0, wallet=None):
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

        transaction =  TrinityTransaction(channel_name, wallet)

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
                                       "RoleIndex":role_index
                                      }
                 }
        FounderMessage.send(message)

    def verify(self):
        if self.sender == self.receiver:
            return False, "Not Support Sender is Receiver"
        if self.receiver != self.wallet.url:
            return False, "The Endpoint is Not Me"

        return True, None

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
                                                "RoleIndex": role_index
                                                },
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
                                                "RoleIndex": role_index
                                                },
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
                    "RoleIndex": role_index

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
            txid = self.founder.get("originalData").get("txId")
            register_monitor(txid, monitor_founding, self.channel_name, EnumChannelState.OPENED.name)
        else:
            message_response = {"MessageType": "FounderFail",
                                "Sender": self.receiver,
                                "Receiver": self.sender,
                                "ChannelName": self.channel_name,
                                "TxNonce": 0,
                                "MessageBody":self.message_body,
                                "Error": "SendFounderRawTransactionFail"
                                }
            Message.send(message_response)
            ch.Channel.channel(self.channel_name).delete_channel()

    def _handle_error_message(self):
        return ch.Channel.channel(self.channel_name).delete_channel()

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
            "RoleIndex":0
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
               role_index=0):
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
        :return:
        """

        transaction = TrinityTransaction(channel_name, wallet)
        founder = transaction.get_founder()
        LOG.debug("Rsmc Create  founder {}".format(json.dumps(founder)))
        tx_state = transaction.get_transaction_state()
        channle = ch.Channel.channel(channel_name)
        balance = channle.get_balance()
        #balance = transaction.get_balance(str(int(tx_nonce)-1))
        LOG.debug("Rsmc Create get balance {}".format(str(balance)))

        if balance:
            sender_balance = balance.get(sender_pubkey)
            receiver_balance = balance.get(receiver_pubkey)
            balance_value = sender_balance.get(asset_type.upper())
            receiver_balance_value = receiver_balance.get(asset_type.upper())
            LOG.info("RSMC Balance  %s"  %(str(balance_value)))
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
                Message.send(message)
                return

        sender_balance = float(balance_value) - float(value)
        receiver_balance = float(receiver_balance_value) + float(value)
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
                                       "RoleIndex":role_index
                                      }
                 }
            if router and next_router:
                message.setdefault("Router", router)
                message.setdefault("NextRouter", next_router)

        elif role_index == 2 or role_index == 3:
            tx = transaction.get_tx_nonce(tx_nonce=str(int(tx_nonce)-1))
            commitment = tx.get("Commitment").get("originalData")
            breachremedy = createBRTX(founder["originalData"]["addressFunding"], pubkey_to_address(receiver_pubkey), sender_balance,
                                      commitment["scriptRSMC"])
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
                           "RoleIndex":role_index
                           }
                       }
        LOG.info("Send RsmcMessage role index 1 message  ")
        RsmcMessage.send(message)
        balance = {}
        subitem = {}
        subitem.setdefault(asset_type.upper(), sender_balance)
        balance.setdefault(sender_pubkey,subitem)
        subitem = {}
        subitem.setdefault(asset_type.upper(), receiver_balance)
        balance.setdefault(receiver_pubkey,subitem)
        transaction.update_transaction(str(tx_nonce), Balance=balance, State="confirm")

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
                           asset_type=self.asset_type.upper(), role_index= 1)


    def _handle_1_message(self):
        LOG.info("RSMC handle 1 message  {}".format(json.dumps(self.message)))
        self.store_monitor_commitement()
        self.send_responses()

        # send 2 message
        RsmcMessage.create(self.channel_name, self.wallet,
                           self.receiver_pubkey, self.sender_pubkey,
                           self.value, self.sender_ip, self.receiver_ip, self.tx_nonce,
                           asset_type=self.asset_type.upper(), role_index=2)

    def _handle_2_message(self):
        # send 3 message
        self.transaction.update_transaction(str(self.tx_nonce), BR=self.breach_remedy)
        RsmcMessage.create(self.channel_name, self.wallet,
                           self.receiver_pubkey, self.sender_pubkey,
                           self.value, self.sender_ip, self.receiver_ip, self.tx_nonce,
                           asset_type=self.asset_type.upper(), role_index=3)
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

        register_monitor(monitor_ctxid, monitor_height, btxDataself + bwitness, btxsignother, btxsignself)


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
                                                "RoleIndex": self.role_index
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
                                                "RoleIndex": self.role_index
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


class HtlcMessage(TransactionMessage):
    """
    { "MessageType":"Htlc",
    "Sender": "9090909090909090909090909@127.0.0.1:20553",
    "Receiver":"101010101001001010100101@127.0.0.1:20552",
    "TxNonce": 0,
    "ChannelName":"3333333333333333333333333333",
    "MessageBody": {
            "HCTX":"",
            "RDTX":"",
            "HEDTX":"",
            "HTTX":""，
            "HTDTX":"",
            "HTRDTX":"",
            "RoleIndex":""
        }
    }
    """

    def __init__(self, message, wallet):
        super().__init__(message,wallet)
        self.hctx = self.message_body.get("HCTX")
        self.hedtx = self.message_body.get("HEDTX")
        self.rdtx = self.message_body.get("RDTX")
        self.htdtx = self.message_body.get("HTDTX")
        self.httx = self.message_body.get("HTTX")
        self.htrdtx = self.message_body.get("HTRDTX")
        self.role_index = self.message_body.get("RoleIndex")
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
        hctx = createSelfHCTX(senderpubkey,receiverpubkey,HTLCvalue,sender_balance)
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
            hctx_sig = {"txDataSign": self.sign_message(self.hctx.get("txData")),
                                "originalData": self.hctx}
            hedtx_sig = {"txDataSign": self.sign_message(self.hedtx.get("txData")),
                              "originalData": self.hedtx}
            httx_sig = {"txDataSign": self.sign_message(self.httx.get("txData")),
                      "originalData": self.httx}

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
            message_response = { "MessageType":"HtlcFail",
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
            self.transaction.update_transaction(str(self.tx_nonce), HCTX = self.hctx, HEDTX=self.hedtx, HTTX= self.httx)

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
        print(self.asset)
        pycode = Payment(self.wallet,self.sender).generate_payment_code(get_asset_type_id(self.asset),
                         self.amount, self.comments)
        message = {"MessageType":"PaymentLinkAck",
                   "Receiver":self.sender,
                   "MessageBody": {
                                    "PaymentLink": pycode
                                   },
                   }
        Message.send(message)

        #ToDo Just for test, will be remove soon
        # time.sleep(30)
        # state ,result = Payment.decode_payment_code(pycode)
        # hr = json.loads(result).get("hr")
        # PaymentAck.create(self.sender, hr)

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
    return None


def monitor_height(height, txdata, signother, signself):
    register_block(str(int(height)+1000),send_rsmcr_transaction,height,txdata,signother, signself)


def send_rsmcr_transaction(height,txdata,signother, signself):
    height_script = blockheight_to_script(height)
    rawdata = txdata.format(blockheight_script=height_script,signOther=signother,signSelf=signself)
    TrinityTransaction.sendrawtransaction(rawdata)
