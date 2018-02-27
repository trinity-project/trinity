#!/usr/bin/env python
# encoding: utf-8
"""
@author: Maiganne

"""


from app import db


class Balance(db.Model):
    __tablename__ = 'balance'
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(256))
    neo_balance = db.Column(db.Integer,default=0)
    gas_balance =db.Column(db.Numeric(16,8),default=0)

class NeoVout(db.Model):
    __tablename__ = 'neo_vout'
    id = db.Column(db.Integer, primary_key=True)
    tx_id = db.Column(db.String(256))
    address = db.Column(db.String(256))
    asset_id = db.Column(db.String(256))
    vout_number = db.Column(db.Integer)
    value = db.Column(db.Integer,default=0)


    def to_json(self):
        return {
                'tx_id': self.tx_id,
                'address': self.address,
                'asset_id': self.asset_id,
                'vout_number': self.vout_number,
                'value' : float(self.value)
                }
    @staticmethod
    def save(tx_id,address,asset_id,vout_number,value):
        new_instance = NeoVout(tx_id=tx_id, address=address, asset_id=asset_id, vout_number=vout_number,value=value)
        db.session.add(new_instance)
        db.session.commit()
    @staticmethod
    def delete(instanse):
        db.session.delete(instanse)
        db.session.commit()


class GasVout(db.Model):
    __tablename__ = 'gas_vout'
    id = db.Column(db.Integer, primary_key=True)
    tx_id = db.Column(db.String(256))
    address = db.Column(db.String(256))
    asset_id = db.Column(db.String(256))
    vout_number = db.Column(db.Integer)
    value = db.Column(db.Numeric(16,8),default=0)


    def to_json(self):
        return {
                'tx_id': self.tx_id,
                'address': self.address,
                'asset_id': self.asset_id,
                'vout_number': self.vout_number,
                'value' : float(self.value)
                }

    @staticmethod
    def save(tx_id,address,asset_id,vout_number,value):
        new_instance = GasVout(tx_id=tx_id, address=address, asset_id=asset_id, vout_number=vout_number,value=value)
        db.session.add(new_instance)
        db.session.commit()
    @staticmethod
    def delete(instanse):
        db.session.delete(instanse)
        db.session.commit()