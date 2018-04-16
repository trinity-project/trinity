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
    G = nx.Graph()
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
    from graph_operation import ChannelGraph
    node = {
        "tag": "n1",
        "Ip": "n1",
        "Pblickkey": "pk",
        "Name": "test1",
        "Deposit": "1",
        "Fee": 1,
        "Balance": 5,
        "SpvList": []
    }
    node1 = {
        "tag": "n1",
        "Ip": "n2",
        "Pblickkey": "pk",
        "Name": "test1",
        "Deposit": "1",
        "Fee": 1,
        "Balance": 5,
        "SpvList": []
    }
    G = G = nx.Graph()
    G.add_edge('n1', 'n2')
    G.add_edge('n1', 'n3')
    print(G.nodes)
    # print(type(G.nodes))
    # print(G.nodes["n1"])
    # print(G.nodes["n2"])
    for edge in G.edges:
        print(edge,type(edge))
    G.remove_edge("n2","n1")
    print(G.edges)
    # print([edge for edge in G.edges])
    # print(G.has_edge("n2","n1"))
    # print(G.adj)
    # print(list(nx.generate_adjlist(G,delimiter=':')))
    # from networkx.readwrite import json_graph
    # data1 = json_graph.node_link_data(G)
    # print(type(data1))
    # print(list(G.adjacency()))
    show_graph(G)
