"""Author: Trinity Core Team 

MIT License

Copyright (c) 2018 Trinity

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE."""

import json
import copy
from treelib import Node, Tree
from treelib.exceptions import DuplicatedNodeIdError
import re


def parse_uri(uri):
    # fixed url format: publicKey@IP:PORT
    if isinstance(uri, str):
        return re.split('[@:]', uri)

    return None


class RouteTree(Tree):
    """
    # Node(tag, nid, data)
    # tag: readable noe name for human to
    # nid: unique id in scope three
    """

    def __init__(self):
        super().__init__()

        # record the route path
        self.route_path = []

    def create(self,tag, identifier, data):
        self.create_node(tag=tag, identifier=identifier, data=data)
        self.root = identifier

    def find_router(self, identifier, policy=None):
        """

        :param identifier:  use the url as the identifier
        :param policy:      not used currently
        :return:
        """
        self.route_path = [nid for nid in self.rsearch(identifier)][::-1]
        return self.route_path

    @property
    def next_jump(self):
        try:
            return self.route_path[self.route_path.index(self.root)+1]
        except Exception:
            return None

    @classmethod
    def to_tree(cls, tr_json):
        tree = cls()
        for item in json.loads(tr_json):
            tree.expand_branch(tr_json = tr_json)

        return tree

    def expand_branch(self, tr_json, father= None):
        tr = json.loads(tr_json)
        tag = list(tr.keys())[0]
        nid = tr[tag]["data"]["Ip"]
        try:
            self.create_node(tag=tag, identifier=nid, parent=father, data=tr[tag]["data"])
        except DuplicatedNodeIdError:
            pass
        # print(tr.values())
        child = list(tr.values())[0].get("children")
        # print(child)
        if child:
            for item in child:
                self.expand_branch(json.dumps(item), father=nid)
        else:
            pass

    def sync_tree(self, peer_tree):
        """
        get all peers node id\n
        traversal all peers \n
        deep copy current tree get the new_tree\n
        make child as the new_tree root\n
        :param peer_tree:
        :return:
        """
        copy_peer_tree = copy.deepcopy(peer_tree)
        # if contains each other
        for self_nid in self.nodes.keys():
            if copy_peer_tree.contains(self_nid) and self_nid != peer_tree.root:
                copy_peer_tree.remove_node(self_nid)
        if self.contains(peer_tree.root):
            self.remove_node(peer_tree.root)
        # print(peer_tree.to_dict(with_data=True))
        self.paste(self.root, copy_peer_tree)            
            


class WalletSet(object):
    def __init__(self, **kwargs):
        self.address = None
        self.ip = None
        self.port = None
        self.public_key = None
        self.deposit = None
        self.fee = 0

        self.__dict__.update(kwargs)


class SPVHashTable(object):
    """
    Description: use the dictionary to hash the spv table with wallet node address
    """
    hash_instance = None

    def __init__(self):
        self.__maps = {}
        pass

    def __new__(cls, *args, **kwargs):
        if not cls.hash_instance:
            cls.hash_instance = object.__new__(cls, *args, **kwargs)

        return cls.hash_instance

    @property
    def maps(self):
        return self.__maps

    def find_keys(self, spv_key):
        """

        :param spv_key: The public key string of the spv\n
        :return: list type. [wallet-1-public-key , wallet-2-public-key, ...]
        """
        keys = []
        for key in self.maps:
            if spv_key in self.find(key):
                keys.append(key)
        return keys

    def find(self, key):
        """

        :param key: The public key string of the wallet\n
        :return: list type. [spv-1-public-key , spv-2-public-key, ...]
        """
        return self.maps.get(key)

    def add(self, key, value):
        """

        :param key:     The public key string of the wallet
        :param value:   the public key of the spv
        :return:
        """
        if key not in self.maps.keys():
            self.maps.update({key:[value]})
        else:
            self.maps[key].append(value)
        # elif value not in self.maps.get(key):
        #     self.maps[key].append(value)

    def remove(self, key, value):
        """

        :param key:     The public key string of the wallet
        :param value:   the public key of the spv
        :return:
        """
        if key in self.maps.keys():
            spv_list = self.maps[key]
            if value in spv_list:
                spv_list.remove(value)

    def sync_table(self, hash_table):
        """
        :param hash_table: json or dict type
        :return:
        """
        if isinstance(hash_table, str):
            # decoder
            hash_table = self.to_dict(hash_table)

        if not hash_table:
            return

        for key in hash_table:
            if key in self.maps:
                self.maps[key].extend(hash_table[key])
                self.maps[key] = list(set(self.maps[key]))
            else:
                self.maps[key] = hash_table[key]

    def to_json(self):
        return json.dumps(self.maps)

    @staticmethod
    def to_dict(s):
        return json.loads(s)
