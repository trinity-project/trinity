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

class RouteTree(Tree):

    def __init__(self):
        super().__init__()

    def create(self,tag, identifier, data):
        self.create_node(tag=tag, identifier=identifier, data=data)
        self.root = identifier

    def find_father(self, nid):
        node = self.get_node(nid)
        return self.parent(node.identifier) if node else self.root


    def update_subtree(self, tree_massage):
        """

        :param tree_massage:
{
	"Harry": {
		"children": [{
			"Bill": {
				"data": null
			}
		}, {
			"Jane": {
				"children": [{
					"Diane": {
						"children": [{
							"Mary": {
								"data": null
							}
						}],
						"data": null
					}
				}],
				"data": null
			}
		}],
		"data": null
	}
}
        :return:
        """
        new_root = tree_massage.keys()[0]
        node  = self.get_node(new_root)
        if node:
            self.remove_node(new_root)
        father = self.find_father(new_root)

        return self.expand_branch(father = father, tr_json=tree_massage)

    @classmethod
    def to_tree(cls, tr_json):
        tree = cls()
        for item in json.loads(tr_json):
            tree.expand_branch(tr_json = tr_json)

        return tree


    def expand_branch(self, tr_json, father= None):
        tr = json.loads(tr_json)
        root = list(tr.keys())[0]
        try:
            self.create_node(tag=root, identifier=root, parent=father)
        except DuplicatedNodeIdError:
            pass
        # print(tr.values())
        child = list(tr.values())[0].get("children")
        # print(child)
        if child:
            for item in child:
                self.expand_branch(json.dumps(item), father=root)
        else:
            pass

    # Node(tag, nid, data)
    # tag: readable noe name for human to 
    # nid: unique id in scope three
    def sync_tree(self, peer_tree):
        """
        get all peers node id\n
        traversal all peers \n
        deep copy current tree get the new_tree\n
        make child as the new_tree root\n
        """
        new_peer_trees = list()
        # peer_tree_root = peer_tree.root
        copy_tree = copy.deepcopy(self)
        copy_peer_tree = copy.deepcopy(peer_tree)
        self.paste(self.root, copy_peer_tree)
        peer_tree.paste(peer_tree.root, copy_tree)
        return peer_tree
        # for child in self.is_branch(self.root):
        #     new_tree = copy.deepcopy(self)
        #     new_tree.root = child
        #     new_peer_trees.append(new_tree)
        # return new_peer_trees
        # return new_peer_trees

    









