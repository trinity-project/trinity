# coding: utf-8
from routertree import RouteTree, SPVHashTable
from config import cg_public_ip_port
class Wallet:
    def __init__(self, name, pk, fee, balance):
        self.name = name
        self.pk = pk
        self.url = pk + "@" + cg_public_ip_port
        self.fee = fee
        self.balance = balance
        self.spv_table = SPVHashTable()
        self.channel_tree = self._initialize_tree()

    def __str__(self):
        return "Wallet({}.name, {}.pk)".format(self)

    def add_channel(self):
        pass
    def remove_channel(self):
        pass
    def update_balance(self, balance):
        root_node = self.channel_tree.get_node(cg_public_ip_port)
        root_node.data.balance = balance

    def add_spv(self, spv_pk):
        self.spv_table.add(self.pk)
        root_node = self.channel_tree.get_node(cg_public_ip_port)
        root_node.data["SpvList"].append(spv_pk)

    def remove_spv(self, spv_pk):
        # self.spv_table.
        pass

    def _initialize_tree(self):
        tree = RouteTree()
        tree.create_node(
            tag="node",
            identifier=cg_public_ip_port
            data={
                "Ip": cg_public_ip_port,
                "Pblickkey": self.pk,
                "Name": self.name,
                "Fee": self.fee,
                "Balance": self.balance,
                "SpvList": []
            }
        )
        return tree