
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Numeric,Boolean
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pymysql
from decimal import Decimal


pymysql.install_as_MySQLdb()
engine = create_engine('sqlite:///transction_record.db')
Session = sessionmaker(bind=engine)
Base = declarative_base()
session=Session()

class TX_RECORD(Base):
    __tablename__ = 'tx_record'
    id = Column(Integer, primary_key=True)
    tx_id = Column(String(256))
    state = Column(Boolean)
    asset_type = Column(String(64))
    address_from = Column(String(64))
    address_to = Column(String(64))
    value = Column(Numeric(16,8))


    @staticmethod
    def save(tx_id,asset_type,address_from,address_to,value,state):
        new_instance = TX_RECORD(tx_id=tx_id,state=state,
                                 asset_type=asset_type,address_from=address_from,
                                address_to=address_to,value=Decimal(value))
        session.add(new_instance)
        session.commit()

    @staticmethod
    def query(address):
        res=session.query(TX_RECORD).filter(TX_RECORD.address_from == address or TX_RECORD.address_from == address).all()
        return res

    def to_json(self):
        return {
            "tx_id":self.tx_id,
            "asset_type":self.asset_type,
            "address_from":self.address_from,
            "address_to":self.address_to,
            "value":self.value,
            "state":self.state,
        }


Base.metadata.create_all(engine)