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


from mongoengine import *
from datetime import datetime
from src.util.state import ChannelState
from src.util.state import DepositState


class Address(Document):
    """

    """
    type = StringField(required=True)
    address = StringField(required=True)
    public_key = StringField(required=True)
    ip_address = StringField()
    transaction = ListField()
    jion_time = DateTimeField(default= datetime.now())


class Channel(Document):
    """

    """
    channel_id = StringField(required=True)
    founder = ReferenceField(Address)
    participator  = ReferenceField(Address)
    deposit = LongField()
    open_block_number = LongField()
    create_time = DateTimeField(default=datetime.now())
    state = IntField(default=ChannelState.NULL.value)


class Depoist(EmbeddedDocument):
    """

    """
    index = IntField()
    deposit = LongField()
    state = IntField(default=DepositState.CACHE)
    depoist_time = DateTimeField(default=datetime.now())


connect("trintiy", host = "localhost", port = 27017)

