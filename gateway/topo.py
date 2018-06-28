# coding: utf-8
from functools import wraps
import time
import json
import networkx as nx
from spvtable import SPVHashTable
from networkx.readwrite import json_graph
from config import cg_public_ip_port
import utils

"""
message = {
    "MessageType": "SyncChannelState",
    "SyncType": "add_single_edge|remove_single_edge|update_node_data|add_whole_graph",
    "Sender": sender,
    "Broadcast": True,
    "Source": url,
    "Target": url,
    "MessageBody": content
}

# when node channel modify(add,remove) 
# sync with self's other peers
# SyncType = add_whole_graph
MessageBody = {
    "Nid": "n1",
    "Ip": "n2",
    "Pblickkey": "pk",
    "Name": "test1",
    "Deposit": "1",
    "Fee": 1,
    "Balance": 5,
    "SpvList": []
}

# when channel build the data format which will send to peer(just source<-->target eachother)
# not include sync with self's other peers
# SyncType = add_whole_graph
MessageBody = graph.to_json()

# when channel closed the data format which will send to adjacent nodes
# include sync with self's other peers
# SyncType = remove_single_edge
MessageBody = {}

# when node's data modify
# include sync with self's other peers
# SyncType = update_node_data
MessageBody = {
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
def timethis(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.process_time()
        # start = time.time()
        r = func(*args, **kwargs)
        end = time.process_time()
        # end = time.time()
        print('{}.{} spend : {}ms'.format(func.__module__, func.__name__, (end - start)*1000))
        return r
    return wrapper

class Nettopo:
    def __init__(self):
        # save wallet (with same asset type) pk set that attached this gateway
        self.nids = set()
        self._graph = nx.Graph()
        self.spv_table = SPVHashTable()

    def __str__(self):
        return "Nettopo(nodes: {}, links: {})".format(
            list(self._graph.nodes.keys()),
            list(self._graph.edges.keys())
        )
        
    def __repr__(self):
        return self.__str__()

    def add_node(self, data, pk=None):
        if not pk:
            pk = data.get("Publickey")
        if not pk:
            raise Exception("public_key must provide")
        self._graph.add_node(pk, **data)
        self.nids.add(pk)
        # self.nid = pk
        # self.nid = data["Nid"]
        # self.node = self._graph.nodes[self.nid]

    def add_edge(self, sid, tid):
        # first sid must in the graph
        # otherwise local node will not receive this sync type msg
        if not self._graph.has_edge(sid, tid):
            u_node = self._graph.nodes.get(sid)
            v_node = self._graph.nodes.get(tid)
            edge_data = utils.make_edge_data(u_node, v_node)
            self._graph.add_edge(sid, tid, **edge_data)
        else:
            pass

    def remove_edge(self, sid, tid):
        if self._graph.has_edge(sid, tid):
            self._graph.remove_edge(sid, tid)
            return True
            # for nid in [sid, tid]:
            #     has_spv = True if len(self.spv_table.find(nid)) else False
            #     if self._isolated(nid) and not spv_len:
            #         self._graph.remove_node(nid)
        else:
            return False
    
    def update_data(self, data):
        node_data = []
        if isinstance(data, dict):
            node_data.append(data)
        elif isinstance(data, list):
            node_data = data
        else: return
        for data in node_data:
            nid = data.get("Publickey")
            if not self._graph.has_node(nid): return
            node = self._graph.nodes[nid]
            if data["Fee"] != node["Fee"]:
                diff_fee = data["Fee"] - node["Fee"]
                self._update_edge_data(nid, diff_fee)
            self._update_node_data(node, data)

    def _isolated(self, nid):
        isolated = False
        try:
            next(self._graph.neighbors(nid))
        except StopIteration:
            isolated = True
        return isolated

    def _update_node_data(self, node, data):
        print("update node attributes")
        for key in node:
            if key in data.keys():
                if key == "Balance" and isinstance(data[key], dict):
                    node[key].update(data[key])
                else:
                    node[key] = data[key]

    def _update_edge_data(self, nid, diff_fee):
        # update the edges's weight that include the nid
        # self.edges[source, target]['weight'] = weight
        print("update edge attribute")
        for edge in self._graph.edges:
            if nid in edge:
                self._graph.edges[edge[0],edge[1]]["weight"] += diff_fee
                
    @timethis
    def find_shortest_path_decide_by_fee(self, source, target):
        """
        :param source: start uri\n
        :param target: end uri\n
        :return type list ["A","B","C"]
        """
        sid = utils.get_public_key(source)
        tid = utils.get_public_key(target)
        try:
            path = nx.shortest_path(self._graph, sid, tid, weight='weight')
        except nx.exception.NetworkXNoPath:
            path = []
        return path

    def to_json(self, target=None):
        """
        :return type dict or json str
        """
        data = json_graph.node_link_data(self._graph)
        if target == "str":
            return json.dumps(data)
        else:
            return data

    def to_graph(self, data):
        """
        :param data: type dict
        """
        graph = nx.readwrite.json_graph.node_link_graph(data)
        return graph

    def sync_channel_graph_from_graph(self, data):
        """
        :param data: type dict
        """
        # sender_nid = utils.get_public_key(data["Sender"])
        # receiver_nid = utils.get_public_key(data["Receiver"])
        sender_nid = utils.get_public_key(data["Source"])
        receiver_nid = utils.get_public_key(data["Target"])
        sync_graph = self.to_graph(data["MessageBody"])
        self._graph = nx.algorithms.operators.binary.compose(self._graph, sync_graph)
        self.add_edge(sender_nid, receiver_nid)

    def sync_channel_graph(self, data):
        """
        :param data: type dict
        """
        sync_type = data.get("SyncType")
        # when sync to peers
        if sync_type == "add_single_edge":
            sid = utils.get_public_key(data["Source"])
            tid = utils.get_public_key(data["Target"])
            # data = data["MessageBody"]
            self.add_edge(sid, tid)
        elif sync_type == "remove_single_edge":
            sid = utils.get_public_key(data["Source"])
            tid = utils.get_public_key(data["Target"])
            self.remove_edge(sid, tid)
        elif sync_type == "update_node_data":
            data = data["MessageBody"]
            self.update_data(data)
        elif sync_type == "add_whole_graph":
            self.sync_channel_graph_from_graph(data)

    def draw_graph(self):
        import matplotlib.pyplot as plt
        plt.subplot()
        nx.draw(self._graph, with_labels=True, font_size=3)
        plt.savefig("test/{}.png".format(self.nid))

    def show_edgelist(self):
        return nx.convert.to_edgelist(self._graph)

    def has_node(self, nid):
        if "@" in nid:
            nid = utils.get_public_key(nid)
        return self._graph.has_node(nid)

    def has_edge(self, u, v):
        if "@" in u:
            u = utils.get_public_key(u)
            v = utils.get_public_key(v)
        return self._graph.has_edge(u, v)

    def get_node_dict(self, nid):
        return self._graph.nodes[nid]

    def get_nodes(self):
        return self._graph.nodes

    def get_neighbors_set(self, nid):
        return set(self._graph.neighbors(nid))

    def get_number_of_edges(self):
        return self._graph.number_of_edges()

    @classmethod
    def add_or_update(cls, topos, asset_type, magic, wallet):
        """
        add wallet node to topo
        """
        pk = wallet.public_key
        data = utils.make_topo_node_data(wallet, asset_type)
        if topos.get(utils.asset_type_magic_patch(asset_type, magic)):
            topo = topos[utils.asset_type_magic_patch(asset_type, magic)]
            if topo.has_node(pk):
                topo.update_data(data)
                # pass
            else:
                topo.add_node(data, pk=pk)
        else:
            topo = cls()
            topo.magic = magic
            topo.add_node(data, pk=pk)
            topos[utils.asset_type_magic_patch(asset_type, magic)] = topo