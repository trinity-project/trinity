# coding: utf-8
"""
module for multi wallets and asset
"""
from routertree import SPVHashTable
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
        return "Asset(type: {}, fee: {}, deposit: {}, balance: {}, graph: {})".\
            format(self.asset_type, self.fee, self.deposit, self.balance, self.router_graph)

    def __repr__(self):
        return self.__str__()

    def update(self, **kwargs):
        """
        update the asset attributes
        """
        for k in self.__dict__:
            if k in kwargs.keys():
                self.__dict__[k] = kwargs[k]

    def _init_channel_struct(self, asset):
        asset.spv_table = SPVHashTable()
        asset.router_graph = RouterGraph()
        data = {
            # the nid of graph is public_key
            # this field may discarded
            "Nid": self.public_key,
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

class _Wallet:
    # class attribute,save the opened wallet
    # at any time, there's only one opened wallet 
    def __init__(self, **kwargs):
        # basic attributes
        self.public_key = kwargs.get("public_key")
        self.fee = kwargs.get("fee")
        self.deposit = kwargs.get("deposit")
        self.balance = kwargs.get("balance")
        self.asset_type = kwargs.get("asset_type")
        self.url = "{}@{}".format(self.public_key, cg_public_ip_port)
        self.name = kwargs.get("name")
        # save wallet_client ip
        self.ip = kwargs.get("ip")
        # wallet status 1: opened;0:closed
        self.status = 1

    def __str__(self):
        # return "Wallet(name: {}, asset_type: {}, fee: {}, deposit: {}, balance: {}, status: {})".\
        #     format(self.name, self.asset_type, self.fee, self.deposit, self.balance, self.status)
        return "Wallet(name: {}, asset_type: {}, status: {})".\
            format(self.name, self.asset_type, self.status)

    def __repr__(self):
        return self.__str__()
    
    def _update_basic_attributes(self, **kwargs):
        for k in self.__dict__:
            if k in kwargs.keys() and k != "asset_type":
                self.__dict__[k] = kwargs[k]

    @classmethod
    def add_or_update(cls, wallets, **kwargs):
        """
        add or update a wallet by public_key \n
        :param wallets: the dict with the pairs(pk,Wallet instace)\n
        :param kwargs: fee,deposit,balance,asset_type,public_key,name
        """
        public_key = kwargs.get("public_key")
        if wallets.get(public_key):
            wallet = wallets[public_key]
            # print(kwargs)
            wallet._update_basic_attributes(**kwargs)
            wallet.status = 1
        else:
            wallet = cls(**kwargs)
            wallets[public_key] = wallet
        return wallet

class WalletClient:
    
    def __init__(self, ip):
        self.ip = ip
        self.opened_wallet = None
        self.wallets = {}

    def __str__(self):
        return "WalletClient(wallets: {})".\
            format(self.wallets)

    def __repr__(self):
        return self.__str__()

    def _update_opened_wallet(self, wallet):
        """
        update the opened wallet instance\n
        and change the old opened wallet status
        """
        if self.opened_wallet == wallet:
            return
        if self.opened_wallet:
            self.opened_wallet.status = 0
        self.opened_wallet = wallet
    
    def remove_wallet(self, public_key):
        if not self.wallets.get(public_key):
            return
        if self.opened_wallet == self.wallets[public_key]:
            self.opened_wallet = None
        del self.wallets[public_key]

    @classmethod
    def add_or_update(cls, clients, **kwargs):
        ip = kwargs.get("ip")
        public_key = kwargs.get("public_key")
        if not ip or not public_key:
            raise Exception("ip and public_key must provide")
        if clients.get(ip):
            client = clients[ip]
        else:
            client = cls(ip)
            clients[ip] = client
        wallet = _Wallet.add_or_update(client.wallets, **kwargs)
        client._update_opened_wallet(wallet)
        return wallet

if __name__ == "__main__":
    from pprint import pprint
    data1 = {"fee": 1, "public_key": "pk1", "balance":8, "deposit":3, "asset_type": "GAS", "name": "test1", "ip": "0.0.0.0"}
    data2 = {"fee": 2, "public_key": "pk2", "balance":9, "deposit":3, "asset_type": "GAS", "name": "test2", "ip": "0.0.0.1"}
    clients = {}
    WalletClient.add_or_update(clients, **data1)
    WalletClient.add_or_update(clients, **data2)
    pprint(clients)
    # wallets = {}
    # print(wallets)
    data = {"fee": 100, "public_key": "pk3", "asset_type": "NEO", "name": "test", "ip": "0.0.0.0"}
    WalletClient.add_or_update(clients, **data)
    print(clients["0.0.0.0"].opened_wallet)
    pprint(clients)