# coding: utf-8
from routertree import RouteTree, SPVHashTable
from routergraph import RouterGraph
from config import cg_public_ip_port

class _Asset:
    def __init__(self, **kwargs):
        # instance attributes
        self.fee = kwargs.get("fee")
        self.deposit = kwargs.get("deposit")
        self.balance = kwargs.get("balance")
        self.asset_type = kwargs.get("asset_type")

    def __str__(self):
        return "Asset(type: {}, fee: {}, deposit: {}, balance: {})".\
            format(self.asset_type, self.fee, self.deposit, self.balance)

    def __repr__(self):
        return self.__str__()

    def update(self, **kwargs):
        """
        update the asset attributes
        """
        for k in self.__dict__:
            if k in kwargs.keys():
                self.__dict__[k] = kwargs[k]

class Wallet:
    def __init__(self, **kwargs):
        # basic attributes
        self.public_key = kwargs.get("public_key")
        self.url = "{}@{}".format(self.public_key, cg_public_ip_port)
        self.name = kwargs.get("name")
        self.assets = {}
        self._add_or_update_asset(**kwargs)

    def __str__(self):
        return "Wallet(pk: {}, assets: {})".\
            format(self.public_key, self.assets)

    def __repr__(self):
        return self.__str__()
    
    def _init_channel_struct(self, asset):
        asset.spv_table = SPVHashTable()
        asset.router_graph = RouterGraph()
        data = {
            "Nid": cg_public_ip_port,     # this field will discarded
            "PublicKey": self.public_key,
            "Ip": cg_public_ip_port,
            "Name": self.name,
            "Deposit": asset.deposit,
            "Fee": asset.fee,
            "Balance": asset.balance,
            "AssetType": asset.asset_type,
            "SpvList": []
        }
        asset.router_graph.add_self_node(data)

    def _add_or_update_asset(self, **kwargs):
        asset_type = kwargs.get("asset_type")
        if not asset_type:
            raise Exception("asset_type must provide")
        if self.assets.get(asset_type):
            asset = self.assets[asset_type]
            asset.update(**kwargs)
            spv_list = asset.spv_table.find(self.public_key)
            data = {
                "Nid": cg_public_ip_port,
                "Name": self.name if not kwargs.get("name") else kwargs.get("name"),
                "Deposit": asset.deposit,
                "Fee": asset.fee,
                "Balance": asset.balance,
                "SpvList": [] if not spv_list else spv_list
            }
            asset.router_graph.update_data(data)
        else:
            asset = _Asset(
                fee = kwargs.get("fee"),
                deposit = kwargs.get("deposit"),
                balance = kwargs.get("balance"),
                asset_type = kwargs.get("asset_type")
            )
            self._init_channel_struct(asset)
            self.assets[asset_type] = asset

    @classmethod
    def add_or_update_wallet(cls, wallets, **kwargs):
        """
        add or update a wallet by public_key \n
        :param wallets: the dict with the pairs(pk,Wallet instace)\n
        :param kwargs: fee,deposit,balance,asset_type,public_key,name
        """
        public_key = kwargs.get("public_key")
        if not public_key:
            raise Exception("public_key must provide")
        if wallets.get(public_key):
            wallet = wallets[public_key]
            print(kwargs)
            wallet._add_or_update_asset(**kwargs)
        else:
            wallet = cls(**kwargs)
            wallets[public_key] = wallet

    @classmethod
    def remove_wallet(cls, wallets, public_key):
        """
        :param wallets: the dict with the pairs(pk,Wallet instace)\n
        :param public_key:
        """
        if not wallets.get(public_key):
            raise Exception("public_key must provide")
        del wallets[public_key]
    
if __name__ == "__main__":
    w1 = Wallet(public_key="pk1", fee=1, balance=8, deposit=3, asset_type="TNC")
    w2 = Wallet(public_key="pk2", fee=2, balance=9, deposit=3, asset_type="NEO")
    walelts = {
        "pk1": w1,
        "pk2": w2
    }
    print(walelts)
    data = {"fee": 100, "public_key": "pk1", "asset_type": "TNC", "name": "test"}
    print(walelts["pk1"].assets["TNC"].router_graph._graph.nodes[cg_public_ip_port])
    Wallet.add_or_update_wallet(walelts, **data)
    print(walelts)
    # print(walelts["pk1"].assets["TNC"].__dict__)
    print(walelts["pk1"].assets["TNC"].router_graph._graph.nodes[cg_public_ip_port])