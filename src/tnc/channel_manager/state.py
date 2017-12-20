from sqlalchemy import Column, String, create_engine, Integer
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
import hashlib
from tnc.crypto import crypto_channel, uncryto_channel
from tnc.exception import ChannelDBAddFail, ChannelDBUpdateFail, ChannelExist

Base = declarative_base()

class ChannelDatabase(Base):
    """
    channel table
    """
    __tablename__ = 'channel database'

    receiver = Column(String(256))
    sender =  Column(String(256), primary_key=True)
    channel_name = Column(String(256))
    state = Column(Integer())
    deposit = Column(Integer())
    open_block_number = Column(Integer())

engine = create_engine('sqlite:////tmp/test.db')
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
    def __init__(self, sender):
        self.match = None
        self.sender = sender

    def find_sender(self):
        with OpenDataBase(DBSession) as channle:
            try:
                self.match = channle.query(ChannelDatabase).filter(ChannelDatabase.sender == self.sender).one()
                return True if self.match else False
            except:
                return False

    @property
    def receiver_in_database(self):
        return self.match.receiver if self.match else None
        
    @property
    def state_in_database(self):
        return self.match.state if self.match else None

    @property
    def channel_name_in_database(self):
        return self.match.channel_name if self.match else None

    def add_channle_to_database(self, receiver, channel_name, state, deposit,open_block_number):
        channel_state = ChannelDatabase(receiver=receiver, sender=self.sender, channel_name=channel_name, state=state.value,
                                        deposit=deposit,open_block_number=open_block_number)
        with OpenDataBase(DBSession) as channle:
            try:
                channle.add(channel_state)
                channle.commit()
            except:
                raise ChannelDBAddFail
        return None

    def update_channel_to_database(self,receiver, channel_name, state, deposit,open_block_number):
        channel_state = ChannelDatabase(receiver=receiver, sender=self.sender, channel_name=channel_name, state=state.value,
                                     deposit=deposit,open_block_number=open_block_number)
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
                channle.query(ChannelDatabase).filter(ChannelDatabase.sender == self.sender).delete()
                channle.commit()
            except:
                raise
        return None


class ChannelFile(object):
    """

    """
    PATH = os.path.dirname(__file__)

    def __init__(self, sender, receiver):
        self.receiver = receiver
        self.sender = sender

    @property
    def channel_file_name(self):
        return  "{}.data".format(os.path.join(self.PATH, self.channel_name))

    @property
    def channel_name(self):
        if self.receiver and self.sender:
            channel_md5 = hashlib.md5(self.sender.encode())
            channel_md5.update(self.receiver.encode())
            return channel_md5.hexdigest()
        else:
            return None

    def create_channel(self, **kwargs):
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











