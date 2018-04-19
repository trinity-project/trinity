# coding: utf-8
"""
A -> B
A -> C
B -> C
B -> D
C -> D
D -> C
D -> G
E -> F
F -> C
G -> F
G -> E
H -> F
"""
from functools import wraps
import time
import networkx as nx
import matplotlib.pyplot as plt
# G(v)邻接表
graph = {
    # "A": ["", "C"],
    # "B": ["C", "D"],
    # "C": ["D"],
    # "D": ["C","G"],
    # "E": ["F"],
    # "F": ["C"],
    # "G": ["E", "F"],
    # "H": ["F"]
    "A": ["B", "C"],
    "B": ["C"],
    "C": ["B"]
}

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

def find_path(graph, start, end, path=[]):
    path = path + [start]
    if start == end:
        return path
    if not graph.get(start):
        return None
    for node in graph[start]:
        if node not in path:
            newpath = find_path(graph, node, end, path)
            if newpath: return newpath
    return None

def find_all_paths(graph, start, end, path=[]):
    path = path + [start]
    if start == end:
        return [path]
    if not graph.get(start):
        return []
    paths = []
    for node in graph[start]:
        if node not in path:
            newpaths = find_all_paths(graph, node, end, path)
            for newpath in newpaths:
                paths.append(newpath)
    return paths

def find_shortest_path(graph, start, end, path=[]):
    path = path + [start]
    if start == end:
        return path
    if not graph.get(start):
        return None
    shortest = None
    for node in graph[start]:
        if node not in path:
            newpath = find_shortest_path(graph, node, end, path)
            if newpath:
                if not shortest or len(newpath) < len(shortest):
                    shortest = newpath
    return shortest

@timethis
def get_path(graph, start, end, path=[]):
    # print(find_path(graph, start, end, path=[]))
    # print(find_all_paths(graph, start, end, path=[]))
    # print(find_shortest_path(graph, start, end, path=[]))
    print(nx.shortest_path(graph, start, end, weight='weight'))
    # print(list(nx.all_simple_paths(graph, start, end)))
    # print(list(nx.shortest_simple_paths(graph, start, end)))

def show_graph(g):
    # G = nx.petersen_graph()
    # plt.subplot(121)
    # 
    plt.subplot()
    nx.draw(g, with_labels=True, font_weight='bold')
    # nx.draw_shell(G, nlist=[range(5, 10), range(5)], with_labels=True, font_weight='bold')
    # plt.show()
    plt.savefig("test/graph.png")

def show_edges(g):
    print(g["A"])
    print("############")
    for n, nbrs in g.adj.items():
        for nbr , eattr in nbrs.items():
            print(n, nbr, eattr["weight"])

if __name__ == "__main__":
    # G = nx.Graph()
    # G.add_edge('A', 'B', weight=1)
    # G.add_edge('B', 'D', weight=2)
    # G.add_edge('A', 'C', weight=3)
    # G.add_edge('C', 'D', weight=2)
    # G.add_edge('D', 'F', weight=2)
    # G.add_edge('A', 'B', weight=1)
    # G.add_edge('A', 'C', weight=1)
    # G.add_edge('A', 'D', weight=1)
    # G.add_edge('B', 'F', weight=1)
    # G.add_edge('C', 'B', weight=1)
    # G.add_edge('C', 'D', weight=1)
    # G.add_edge('C', 'G', weight=1)
    # G.add_edge('F', 'G', weight=1)
    # G.add_edge('D', 'E', weight=1)
    # G.add_edge('E', 'G', weight=1)
    # K_5 = nx.complete_graph(5)
    # K_3_5 = nx.complete_bipartite_graph(3, 5)
    # rg = nx.barabasi_albert_graph(100, 5)
    # get_path(G, "A", "G")
    # show_graph(G)
    # show_edges(G)
    import os
    import sys
    r_path = os.getcwd()
    print(r_path)
    sys.path.append(r_path)
    from routergraph import RouterGraph
    node1 = {
        "Nid": "p1",
        "Ip": "n1",
        "Pblickkey": "pk1",
        "Name": "test1",
        "Deposit": "1",
        "Fee": 1,
        "Balance": 5,
        "SpvList": []
    }
    node2 = {
        "Nid": "p2",
        "Ip": "n2",
        "Pblickkey": "pk2",
        "Name": "test1",
        "Deposit": "1",
        "Fee": 2,
        "Balance": 5,
        "SpvList": []
    }
    node3 = {
        "Nid": "p3",
        "Ip": "n2",
        "Pblickkey": "pk2",
        "Name": "test1",
        "Deposit": "1",
        "Fee": 3,
        "Balance": 5,
        "SpvList": []
    }
    node4 = {
        "Nid": "p4",
        "Ip": "n2",
        "Pblickkey": "pk2",
        "Name": "test1",
        "Deposit": "1",
        "Fee": 4,
        "Balance": 5,
        "SpvList": []
    }
    # G = RouterGraph(node1)
    # G.add_edge("p1","p2",node2)
    # # G._graph.add_node("p3", **node3)
    # G.add_edge("p2","p3",node3)
    # G.add_edge("p1","p4",node4)
    # G.add_edge("p3","p4",node4)
    # G.remove_edge("p3","p2")
    # print("更新前")
    # print(nx.convert.to_edgelist(G._graph))
    # for k in G._graph.nodes:
    #     print(k,G._graph.nodes[k])
    # print("最短路径")
    # print(G.find_shortest_path_decide_by_fee("p2", "p4"))
    # data = {
    #     "Nid": "p3",
    #     "Ip": "n2",
    #     "Pblickkey": "pk2",
    #     "Name": "test1",
    #     "Deposit": "1",
    #     "Fee": 0,
    #     "Balance": 6,
    #     "SpvList": []
    # }
    # G.update_data(data)
    # print("最短路径")
    # print(G.find_shortest_path_decide_by_fee("p2", "p4"))
    # print(G._graph.edges["p1","p2"])
    G1 = nx.Graph()
    G2 = nx.Graph()
    # G1.add_edge('n1', 'n2', weight=1)
    # G1.add_edge('n1', 'n3', weight=2)
    
    G2.add_edge('1', '2', weight=3)
    # G2.add_node('n5')
    # G1.add_node('3')
    G3 = nx.algorithms.operators.binary.compose(G1,G2)
    G3.add_edge("3","1")
    G3.add_edge("3","2")
    # G3.add_edge("1","4")
    print(list(G3.nodes))
    print(set(G3.neighbors("3")))
    # # G1.add_edge('n1', 'n4', weight=1)
    # print(G3.nodes)
    # del G1
    # del G2
    # print(G2.nodes)
    # print(type(G.nodes))
    # print(G.nodes["n1"])
    # print(G.nodes["n2"])
    # for edge in G3.edges:
    #     print(edge,type(edge))
    # G.remove_nodes_from(["n2","n3"])
    # print(G3.edges)
    # try:
    #     e = next(G3.neighbors("n5"))
    #     print(e)
    # except StopIteration:
    #     print("isolad")
    # print("更新后")
    # print(nx.convert.to_edgelist(G._graph))
    # for k in G._graph.nodes:
    #     print(k,G._graph.nodes[k])
    # print([edge for edge in G.edges])
    # print(G.has_edge("n2","n1"))
    # print(G.adj)
    # print(list(nx.generate_adjlist(G,delimiter=':')))
    # from networkx.readwrite import json_graph
    # data1 = json_graph.node_link_data(G._graph)
    # print(data1)
    # print(list(G.adjacency()))
    show_graph(G3)
    # show_graph(G3)
