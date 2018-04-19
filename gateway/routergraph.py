# coding: utf-8
from functools import wraps
import time
import json
import networkx as nx
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

class RouterGraph():
    def __init__(self):
        self.nid = None
        self.node = None
        self._graph = nx.Graph()

    def add_self_node(self, data):
        self._graph.add_node(data["Nid"], **data)
        self.nid = data["Nid"]
        self.node = self._graph.nodes[self.nid]

    def add_edge(self, sid, tid):
        # first sid must in the graph
        # otherwise local node will not receive this sync type msg
        if not self._graph.has_edge(sid, tid):
            t_fee = self._graph.nodes[tid]["Fee"]
            s_fee = self._graph.nodes[sid]["Fee"]
            self._graph.add_edge(sid, tid, weight=fee)
            # # tid already in the graph
            # if self._graph.has_node(tid):
            #     t_fee = self._graph.nodes[tid]["Fee"]
            # # tid not yet in the graph
            # else:
            #     self._graph.add_node(tid, **data)
            #     t_fee = data["Fee"]
            # s_fee = self._graph.nodes[sid]["Fee"]
            # fee = s_fee + t_fee
            # self._graph.add_edge(sid, tid, weight=fee)
        else:
            pass
        # self.add_edge(source, target, weight=1)

    def remove_edge(self, sid, tid):
        if self._graph.has_edge(sid, tid):
            self._graph.remove_edge(sid, tid)
            for nid in [sid, tid]:
                if self._isolated(nid) and nid != self.nid:
                    self._graph.remove_node(nid)
        else:
            pass
    
    def update_data(self, data):
        nid = data["Nid"]
        if not self._graph.has_node(nid):
            return
        node = self.node if nid == self.nid else self._graph.nodes[nid]
        if data["Fee"] != node["Fee"]:
            self._update_edge_data(node, data)
        self._update_node_data(node, data)

    def _isolated(self, nid):
        isolated = False
        try:
            next(self._graph.neighbors(nid))
        except StopIteration:
            isolated = True
        return isolated

    def _update_node_data(self, node, data):
        print("just update node")
        node.update(data)

    def _update_edge_data(self, node, data):
        # update the edges's weight that include the nid
        # self.edges[source, target]['weight'] = weight
        print("update edge")
        nid = data["Nid"]
        old_fee = node["Fee"]
        diff = data["Fee"] - old_fee
        for edge in self._graph.edges:
            if nid in edge:
                self._graph.edges[edge[0],edge[1]]["weight"] += diff
                
    @timethis
    def find_shortest_path_decide_by_fee(self, source, target):
        """
        :param source: start uri\n
        :param target: end uri\n
        :return type list ["A","B","C"]
        """
        # sid = utils.get_ip_port(source)
        # tid = utils.get_ip_port(target)
        return nx.shortest_path(self._graph, source, target, weight='weight')

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
        # source_nid = utils.get_ip_port(data["Source"])
        sender_nid = utils.get_ip_port(data["Sender"])
        source_graph = self.to_graph(data["MessageBody"])
        # u_fee = source_graph.nodes[source_nid]["Fee"]
        # sync triggled by wallet notification
        self._graph = nx.algorithms.operators.binary.compose(self._graph, source_graph)
        if not self._graph.has_edge(sender_nid, self.nid):
            u_fee = self._graph.nodes[sender_nid]["Fee"]
            v_fee = self._graph.nodes[self.nid]["Fee"]
            self._graph.add_edge(sender_nid, self.nid, weight=u_fee + v_fee)
        # if source_nid == sender_nid:
        #     v_fee = self.node["Fee"]
        #     # del self._graph
        #     self._graph = nx.algorithms.operators.binary.compose(self._graph, source_graph)
        #     self.node = self._graph.nodes[self.nid]

        #     # print("==========={}===========".format(self.node))
        #     # print("==========={}===========".format(self._graph.nodes))
        #     if not self._graph.has_edge(source_nid, self.nid):
        #         # print("添加了边")
        #         self._graph.add_edge(source_nid, self.nid, weight=u_fee + v_fee)
        #     # self._graph.edges[source_nid, self.nid]["weight"] = u_fee + v_fee
        # # sync triggled by sync to neighbors
        # else: #195 error
        #     self._graph = nx.algorithms.operators.binary.compose(self._graph, source_graph)
        #     self.node = self._graph.nodes[self.nid]
        #     if not self._graph.has_edge(source_nid, sender_nid):
        #         v_fee = self._graph.nodes[sender_nid]["Fee"]
        #         self._graph.add_edge(source_nid, sender_nid, weight=u_fee + v_fee)
            # self._graph.edges[source_nid, sender_nid]["weight"] =  u_fee + v_fee

    def sync_channel_graph(self, data):
        """
        :param data: type dict
        """
        sync_type = data.get("SyncType")
        # when sync to peers
        if sync_type == "add_single_edge":
            sid = utils.get_ip_port(data["Source"])
            tid = utils.get_ip_port(data["Target"])
            # data = data["MessageBody"]
            self.add_edge(sid, tid)
        elif sync_type == "remove_single_edge":
            sid = utils.get_ip_port(data["Source"])
            tid = utils.get_ip_port(data["Target"])
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
            nid = utils.get_ip_port(nid)
        return self._graph.has_node(nid)

    def has_edge(self, u, v):
        if "@" in u:
            u = utils.get_ip_port(u)
            v = utils.get_ip_port(v)
        return self._graph.has_edge(u, v)