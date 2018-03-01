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

from sqlalchemy import Column, String, create_engine, Integer, Float, BigInteger
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
from configure import Configure
from crypto import crypto_channel, uncryto_channel
from exception import ChannelDBAddFail, ChannelDBUpdateFail, ChannelExist, QureyRoleNotCorrect

Base = declarative_base()

DATABASE_PATH = Configure["DBFile"]


class ChannelAddrDataBase(Base):
    """
    channel address table

    """
    __tablename__ = 'channel_address_table'

    address = Column(String(256), primary_key=True)
    ip = Column(String())
    port = Column(String())
    public_key = Column(String())


class ChannelDatabase(Base):
    """
    channel table
    """
    __tablename__ = 'channel_table'

    channel_name = Column(String(256), primary_key=True)
    receiver = Column(String(256))
    sender = Column(String(256))
    state = Column(Integer())
    sender_deposit = Column(Float())
    receiver_deposit = Column(Float())
    open_block_number = Column(Integer())
    start_block_number = Column(BigInteger())
    settle_timeout = Column(Integer())
    sender_deposit_cache = Column(Float())
    receiver_deposit_cache = Column(Float())
    tx_id = Column(String())
    contract_address = Column(String())
    contract_hash = Column(String())
    sendersignature=Column(String())
    receiversignature=Column(String())

class MessageDatabase(Base):
    """
    message table
    """
    __tablename__ = "message_table"

    id = Column(Integer, primary_key=True, autoincrement=True)
    address = Column(String())
    type = Column(String())
    message = Column(String())
    channel_name = Column(String())
    state = Column(String())



engine = create_engine('sqlite:///'+DATABASE_PATH)
DBSession = sessionmaker(bind=engine)
Session = DBSession()
Base.metadata.create_all(engine)