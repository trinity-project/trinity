# coding: utf-8
import time
import os
import json
# import asyncio
from client import Client
from pprint import pprint
import jsonrpcclient

str_tree = '{"Harry": {"data": null, "children": [{"Bill": {"data": null}}, {"Jane": {"data": null, "children": [{"Diane": {"data": null}}, {"Mark": {"data": null}}]}}, {"Mary": {"data": null}}]}}'
def sync_wallet_data(n):
    for x in range(1, n+1):
        message = {
            "MessageBody": {
                "Publickey": "pk{}".format(x),
                "CommitMinDeposit": 1,
                "Fee": 1,
                "Balance": 10
            }
        }
        req_url = "http://localhost:{}/".format(8077 + x - 1)
        # pprint(message)
        jsonrpcclient.request(req_url, 'SyncWalletData', json.dumps(message))

def sync_channel(founder, receiver):
    start_req_port = 8077
    message = {
        "MessageType":"AddChannel",
        "MessageBody": {
            "Founder": founder,
            "Receiver": receiver
        }
    }
    f_pk_id = int(founder[2])
    r_pk_id = int(receiver[2])
    jsonrpcclient.request("http://localhost:{}".format(start_req_port + f_pk_id - 1), 'SyncChannel', json.dumps(message))
    jsonrpcclient.request("http://localhost:{}".format(start_req_port + r_pk_id - 1), 'SyncChannel', json.dumps(message))

def triggle_tx(origin, distination):
    start_req_port = 8077
    origin_port = int((origin.split("@")[1])[-4:])
    distination_port = int((distination.split("@")[1])[-4:])
    origin_pk_id = int(origin[2])
    distination_pk_id = int(distination[2])
    message = {
        "Receiver": distination
    }
    route = jsonrpcclient.request("http://localhost:{}".format(start_req_port + origin_pk_id - 1),"GetRouterInfo",json.dumps(message))
    pprint(route)
    message = {
        "MessageType": "Rsmc",
        "MessageBody": {
            "Value": 30
        },
        "Receiver": distination,
        "Sender": origin,
        "RouterInfo": json.loads(route)["RouterInfo"]
    }
    # return message, start_req_port + origin_pk_id - 1
    jsonrpcclient.request("http://localhost:{}".format(start_req_port + origin_pk_id - 1), 'TransactionMessage', json.dumps(message))

if __name__ == "__main__":
    # sync_wallet_data(5)
    # time.sleep(5)
    # sync_channel("pk1@localhost:8089", "pk3@localhost:8091")
    # time.sleep(5)
    # sync_channel("pk4@localhost:8092", "pk3@localhost:8091")
    # time.sleep(5)
    # sync_channel("pk3@localhost:8091", "pk5@localhost:8093")
    # time.sleep(5)
    # sync_channel("pk1@localhost:8089", "pk2@localhost:8090")
    # time.sleep(5)
    # triggle_tx("pk2@localhost:8090", "pk5@localhost:8093")
    #triggle_tx("pk2@localhost:8090", "pk4@localhost:8092")
    #triggle_tx("pk5@localhost:8093", "pk4@localhost:8092")
    #triggle_tx("pk3@localhost:8091", "pk2@localhost:8090")
    # triggle_tx("pk1@localhost:8089", "pk5@localhost:8093")
    for x in range(1000):
        triggle_tx("pk2@localhost:8090", "pk4@localhost:8092")
        print(x)
        time.sleep(0.04)
