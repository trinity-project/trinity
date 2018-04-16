# coding: utf-8
from functools import wraps
import time
import json
import networkx as nx
from networkx.readwrite import json_graph
import matplotlib.pyplot as plt
from config import cg_public_ip_port
import utils

"""
# when channel build the data format which will send to peer(just source<-->target eachother)
# not include sync with self's other peers
data = {
    "source": s_uri,
    "target": t_uri,
    "node": {
        "Nid": "n1",
        "Ip": "n1",
        "Pblickkey": "pk",
        "Name": "test1",
        "Deposit": "1",
        "Fee": 1,
        "Balance": 5,
        "SpvList": []
    }
}
# when channel closed the data format which will send to adjacent nodes
# include sync with self's other peers
data = {
    "source": s_uri,
    "target": t_uri
}
# when node's data modify
# include sync with self's other peers
data = {
    "Nid": "n1",
    "Ip": "n2",
    "Pblickkey": "pk",
    "Name": "test1",
    "Deposit": "1",
    "Fee": 1,
    "Balance": 5,
    "SpvList": []
}
"""
class ChannelGraph():
    def __init__(self, node):
        self.graph = nx.Graph
        self.add_node(node["Nid"], **node)
        self.nid = cg_public_ip_port
        self.node = self.nodes[self.nid]

    def add_channel(self, data):
        sid = utils.get_ip_port(data["source"])
        tid = utils.get_ip_port(data["target"])
        if not self.has_node(sid) and self.nid == tid
            self.add_node(data["Nid"], **node)
            # as it's undirected so made the weight is the sum of two adjacent nodes
            weight = data["source"]["Fee"] + self.node["Fee"]
            self.add_edge(tid, sid, weight=weight)
        else:
            pass
        # self.add_edge(source, target, weight=1)

    def remove_channel(self, source, target):
        sid = utils.get_ip_port(source)
        tid = utils.get_ip_port(target)
        if self.has_edge(sid, tid):
            self.remove_edge(sid, tid)
        else:
            pass
    
    def update_data(self, data):
        nid = data["Nid"]
        if not self.has_node(nid):
            return
        if data["Fee"] == self.node["Fee"]:
            self._update_node_data(data)
        else:
            self._update_edge_data(data)


    def _update_node_data(self, data):
        self.node.update_data(data)

    def _update_edge_data(self, data):
        # update the edges's weight that include the nid
        # self.edges[source, target]['weight'] = weight
        nid = data["Nid"]
        old_fee = self.nodes[nid]["Fee"]
        diff = data["Fee"] - old_fee
        for edge in self.edges:
            if nid in edge:
                self.edges[edge[0],edge[1]]["weight"] += diff

    def find_shortest_path_decide_by_fee(self, source, target):
        """
        :param source: start uri\n
        :param target: end uri\n
        :return type list ["A","B","C"]
        """
        sid = utils.get_ip_port(source)
        tid = utils.get_ip_port(target)
        return nx.shortest_path(self, sid, tid)

    def to_json(self):
        """
        :return type json str
        """
        data = json_graph.node_link_data(self)
        return json.dumps(data)
