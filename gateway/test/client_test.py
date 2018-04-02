# coding: utf-8
import time
import os
import json
# import asyncio
from client import Client
import jsonrpcclient

if __name__ == "__main__":
    str_tree = '{"Harry": {"data": null, "children": [{"Bill": {"data": null}}, {"Jane": {"data": null, "children": [{"Diane": {"data": null}}, {"Mark": {"data": null}}]}}, {"Mary": {"data": null}}]}}'


    # c = Client()
    # addr = ("106.15.91.150", 8089)
    # c.send(addr, (str_tree + "eof").encode("utf-8"))
    # while(True):
    #     pass
    message = {
        "MessageType":"SyncWallet",
        "MessageBody":{
            "Publickey":"publickey",
            "CommitMinDeposit": 3,
            "Fee": 5
        }
    }
    s = "eeeooodfeof"
    import re
    re.sub(r'eof$', "", s)
    # message = "{'ok': 3}"
    # jsonrpcclient.request('http://localhost:8077/', 'SyncWalletData', json.dumps(message))
    c = Client()
    # addr = ("106.15.91.150", 8089)
    # c.send(addr, (str_tree + "eof").encode("utf-8"))

    # while(True):
    #     pass
    # f = open('./tree.json', 'w')
    # f.write(json.dumps(message))
    # f.read()
    print(time.time())
    tree = None
    with open('../tree.json', 'r') as fs:
        tree = json.loads(fs.read())

    print(type(tree), tree)
    print(time.time())