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
            "MessageBody": {
            "Publickey": "publickey",
            "CommitMinDeposit": 3,
            "Fee": 5,
            "Balance": 10
        }
    }
    message1 = {
        "MessageType":"AddChannel",
        "MessageBody": {
            "Founder": "publickey@106.15.91.150:8089",
            "Receiver": "publickey1@118.89.44.106:8089"
        }
    }
    # message = {
    #     "MessageType":"SyncWallet",
    #     "MessageBody": msbody
    # }
    s = "eeeooodfeof"
    import re
    re.sub(r'eof$', "", s)
    # message = "{'ok': 3}"
    # jsonrpcclient.request('http://localhost:8077/', 'SyncWalletData', json.dumps(message))
    jsonrpcclient.request('http://localhost:8077/', 'SyncChannel', json.dumps(message1))

    # c = Client()
    # addr = ("localhost", 8089)
    # c.send(addr, (str_tree + "/eof/").encode("utf-8"))

    # while(True):
    #     pass
    # f = open('./tree.json', 'w')
    # f.write(json.dumps(message))
    # f.read()
    # print(time.time())
    # tree = None
    # with open('../tree.json', 'r') as fs:
    #     tree = json.loads(fs.read())

    # print(type(tree), tree)
    # print(time.time())
    # def del_dict_item_by_value(dic, value):
    #     values = list(dic.values())
    #     if value in values:
    #         keys = list(dic.keys())
    #         del_index = values.index(value)
    #         del dic[keys[del_index]]

    # del_dict_item_by_value(message, msbody)
    # print(message)