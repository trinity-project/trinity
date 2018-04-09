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
    # message = {
    #         "MessageBody": {
    #         "Publickey": "02442f3eda23eba03aadb02bb25ccb0b680748eb70f4ef96906425ebffc289b103",
    #         "CommitMinDeposit": 3,
    #         "Fee": 1,
    #         "Balance": 10
    #     }
    # }

    # message2 = {
    #         "MessageBody": {
    #         "Publickey": "02e699a116ba2b70d1b41cc05ba0979b5a51131d02c3fcbdd3dbf8c11241bb3345",
    #         "CommitMinDeposit": 2,
    #         "Fee": 1,
    #         "Balance": 20
    #     }
    # }

    cl_message = {
        "MessageType":"AddChannel",
        "MessageBody": {
            "Founder": "pk1@localhost:8089",
            "Receiver": "pk2@localhost:8090"
        }
    }

    cl_message_ = {
        "MessageType":"AddChannel",
        "MessageBody": {
            "Founder": "pk3@localhost:8091",
            "Receiver": "pk2@localhost:8090"
        }
    }

    tx_message = {
        "MessageType": "Rsmc",
        "MessageBody": {
            "Value": 30
        },
        "Receiver": "pk3@localhost:8091",
        "Sender": "pk1@localhost:8091",
        "RouterInfo": {
            "FullPath": [
                ("pk1@localhost:8089",1),
                ("pk2@localhost:8090",1),
                ("pk3@localhost:8091",1)
                # ("pk4@localhost:8092",1),
                # ("pk5@localhost:8093",1),
            ],
            "Next": "pk1@localhost:8089"
        }
    }

    message_1 = {
            "MessageBody": {
            "Publickey": "pk1",
            "CommitMinDeposit": 1,
            "Fee": 1,
            "Balance": 10
        }
    }
    message_2 = {
            "MessageBody": {
            "Publickey": "pk2",
            "CommitMinDeposit": 1,
            "Fee": 1,
            "Balance": 10
        }
    }
    message_3 = {
            "MessageBody": {
            "Publickey": "pk3",
            "CommitMinDeposit": 1,
            "Fee": 1,
            "Balance": 10
        }
    }
    message_4 = {
            "MessageBody": {
            "Publickey": "pk4",
            "CommitMinDeposit": 1,
            "Fee": 1,
            "Balance": 10
        }
    }
    message_5 = {
            "MessageBody": {
            "Publickey": "pk5",
            "CommitMinDeposit": 1,
            "Fee": 1,
            "Balance": 10
        }
    }
    #jsonrpcclient.request('http://localhost:8077/', 'SyncWalletData', json.dumps(message_1))
    #jsonrpcclient.request('http://localhost:8078/', 'SyncWalletData', json.dumps(message_2))
    #jsonrpcclient.request('http://localhost:8079/', 'SyncWalletData', json.dumps(message_3))
    #jsonrpcclient.request('http://localhost:8080/', 'SyncWalletData', json.dumps(message_4))
    # jsonrpcclient.request('http://localhost:8081/', 'SyncWalletData', json.dumps(message_5))
    #jsonrpcclient.request('http://118.89.44.106:8077/', 'SyncWalletData', json.dumps(message2))
    #jsonrpcclient.request('http://localhost:8077/', 'SyncChannel', json.dumps(cl_message))
    #jsonrpcclient.request('http://localhost:8078/', 'SyncChannel', json.dumps(cl_message))
    #jsonrpcclient.request('http://localhost:8078/', 'SyncChannel', json.dumps(cl_message_))
    #jsonrpcclient.request('http://localhost:8079/', 'SyncChannel', json.dumps(cl_message_))
    jsonrpcclient.request('http://localhost:8077/', 'TransactionMessage', json.dumps(tx_message))

    # c = Client()
    # addr = ("localhost", 8089)
    # c.send(addr, (str_tree + "/eof/").encode("utf-8"))

    # while(True):
    #     pass
    # f = open('./tree.json', 'w')
    # f.write(json.dumps(message))
    # with open('./tree.json', 'w') as fs:
    #     fs.write("22222222")
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