from sqlalchemy import Column, String, create_engine, Integer, Float, BigInteger
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
import hashlib
from crypto import crypto_channel, uncryto_channel
from exception import ChannelDBAddFail, ChannelDBUpdateFail, ChannelExist

Base = declarative_base()

DATABASE_PAHT = "/tmp/test.db"


class ChannelAddrDataBase(Base):
    """
    channel address table

    """
    __tablename__ = 'channel address database'

    address = Column(String(256), primary_key=True)
    ip = Column(String())
    port = Column(String())
    public_key = Column(String())


class ChannelAddress(object):
    """
    channel address managment
    """

    def __init__(self):
        pass

    def add_address(self, address, ip="NULL", port="NULL", public_key="NULL"):
        with OpenDataBase(DBSession) as ad:
            try:
                ad.add(ChannelAddrDataBase(address=address, ip=ip, port=port, public_key= public_key))
                ad.commit()
            except:
                raise ChannelDBAddFail
        return None

    def delete_address(self, address):
        with OpenDataBase(DBSession) as ad:
            try:
                ad.query(ChannelAddrDataBase).filter(ChannelAddrDataBase.address == address).delete()
                ad.commit()
            except:
                raise
        return None

    def query_address(self, address):
        with OpenDataBase(DBSession) as ad:
            return ad.query(ChannelAddrDataBase).filter(ChannelAddrDataBase.address == address).one()

    def update_address(self, address, ip, port, public_key="NULL"):
        with OpenDataBase(DBSession) as ad:
            try:
                ad.merge(ChannelAddrDataBase(address=address, ip=ip, port=port, public_key= public_key))
                ad.commit()
            except:
                raise ChannelDBUpdateFail
        return None


class ChannelDatabase(Base):
    """
    channel table
    """
    __tablename__ = 'channel database'

    channel_name = Column(String(256), primary_key=True)
    receiver = Column(String(256))
    sender =  Column(String(256))
    state = Column(Integer())
    sender_deposit = Column(Float())
    receiver_deposit = Column(Float())
    open_block_number = Column(Integer())
    start_block_number = Column(BigInteger())
    settle_timeout = Column(Integer())

engine = create_engine('sqlite:///'+DATABASE_PAHT)
DBSession = sessionmaker(bind=engine)
Base.metadata.create_all(engine)




class OpenDataBase(object):
    def __init__(self, db):
        self.db = db

    def __enter__(self):
        self.session = self.db()
        return self.session

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()


class ChannelState(object):
    """
    Channel state
    """
    def __init__(self, channelname):
        self.match = None
        self.channelname= channelname
        self.find_channel()

    def find_channel(self):
        with OpenDataBase(DBSession) as channle:
            try:
                self.match = channle.query(ChannelDatabase).filter(ChannelDatabase.channel_name == self.channelname).one()
                return True if self.match else False
            except:
                return False

    @property
    def senderinDB(self):
        return self.match.sender

    @property
    def recieverinDB(self):
        return self.match.receiver

    @property
    def receiver_deposit(self):
        return self.match.receiver_deposit

    @property
    def sender_deposit(self):
        return self.match.sender_deposit

    @property
    def receiver_in_database(self):
        return self.match.receiver if self.match else None
        
    @property
    def state_in_database(self):
        return self.match.state if self.match else None

    def add_channle_to_database(self, sender, receiver, channel_name, state, sender_deposit,receiver_deposit,open_block_number, settle_timeout, start_block_number = 0):
        channel_state = ChannelDatabase(receiver=receiver, sender= sender, channel_name=channel_name, state=state.value,
                                        sender_deposit=sender_deposit,receiver_deposit = receiver_deposit,
                                        open_block_number=open_block_number, settle_timeout = settle_timeout,
                                        start_block_number=start_block_number)
        with OpenDataBase(DBSession) as channle:
            try:
                channle.add(channel_state)
                channle.commit()
            except:
                raise ChannelDBAddFail
        return None

    def update_channel_to_database(self,sender, receiver, channel_name, state, sender_deposit, receiver_deposit, open_block_number, settle_timeout, start_block_number):
        channel_state = ChannelDatabase(sender = sender, receiver=receiver, channel_name=channel_name, state=state.value,
                                     sender_deposit=sender_deposit,receiver_deposit= receiver_deposit,
                                        open_block_number=open_block_number,settle_timeout = settle_timeout,
                                        start_block_number=start_block_number)
        with OpenDataBase(DBSession) as channle:
            try:
                channle.merge(channel_state)
                channle.commit()
            except:
                raise ChannelDBUpdateFail
        return None

    def delete_channle_in_database(self):
        with OpenDataBase(DBSession) as channle:
            try:
                channle.query(ChannelDatabase).filter(ChannelDatabase.channel_name == self.channelname).delete()
                channle.commit()
            except:
                raise
        return None


class ChannelFile(object):
    """

    """
    PATH = os.path.dirname(__file__)


    @property
    def channel_file_name(self):
        return "{}.data".format(os.path.join(self.PATH, self.channel_name))

    def create_channelfile(self, **kwargs):
        if os.path.exists(self.channel_file_name):
            raise ChannelExist
        else:
            self.update_channel(**kwargs)

    def update_channel(self, **kwargs):
        with open(self.channel_file_name,"ab+") as f:
            crypto_channel(f, **kwargs)
        return None

    def read_channel(self):
        with open(self.channel_file_name,"rb") as f:
            return uncryto_channel(f)

    def delete_channel(self):
        return os.remove(self.channel_file_name)

    def check_channelfile(self):
        return os.path.exists(self.channel_file_name)


if __name__ == "__main__":
    def regist_address(address):
        if ChannelAddress().add_address(address):
            return 0
        else:
            return 101
    regist_address("address")












