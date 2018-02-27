# --*-- coding : utf-8 --*--
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

import time
from enum import IntEnum
from sserver.crypt.Crypto import CryptoInstance
from sserver.crypt.Helper import bytes_to_hex_string
from sserver.channel.channel import Channel
from sserver.api.interface import GateWay


class TransactionType(IntEnum):
    CREAT = 0
    TRANS = 1
    CLOSE = 2


class Transaction(object):
    """
    """
    def __init__(self, channel_name, sender, receiver, nonce=None, tx_time=None, tx_type=None, asset_type=None,
                 amount=None,comments=None, pre_hash=None, message_hash=None, signature=None):
        self.message = {
            "channel_name": channel_name,
            "sender": sender,
            "receiver": receiver,
            "nonce": nonce,
            "tx_time": tx_time,
            "tx_type": tx_type,
            "asset_type": asset_type,
            "amount": amount,
            "comments": comments,
            "pre_hash": pre_hash
        }

        self.message_hash = message_hash
        self.signature = signature

    @classmethod
    def from_dict(cls, state: dict):
        ret = cls(None, None, None)
        assert (set(state) - set(ret.__dict__)) == set()
        for k, v in state.items():
            if k in ret.__dict__.keys():
                setattr(ret, k, v)
        return ret

    def initialize_transaction(self):
        self.message.setdefault("tx_time",str(time.time()))
        self.message.setdefault("nonce", 0)
        self.message.setdefault("tx_type", TransactionType.CREAT.value)
        message_hash = self.hash_transaction()
        self.message.setdefault("message_hash", message_hash)

    def hash_transaction(self):
        return CryptoInstance().Hash160(self.message)

    def signature(self, private_kye):
        sig = CryptoInstance().Sign(self.message, private_kye)
        self.message.setdefault("signature", bytes_to_hex_string(sig))

    @staticmethod
    def verify_signature(message, signature, pubkey):
        return CryptoInstance().VerifySignature(message, str.encode(signature), pubkey)

    def send_transaction(self, address):
        return GateWay.send_transaction(address, self.message)


class TransferManager(object):
    """

    """
    def __init__(self, message):
        self.message = message
        self.transaction = Transaction.from_dict(self.message)
        self.channel = Channel(self.message["sender"], self.message["receiver"])

    def pass_through_transaction(self):
        address_to = self.message.get("receiver")
        self.transaction.send_transaction(address_to)


class Settle(object):
    """

    """
    def __init__(self, channel_id, settle_timeout=1):
        self.channel_id = channel_id
        self.settle_timeout = settle_timeout

    def send_settling(self):
        pass
