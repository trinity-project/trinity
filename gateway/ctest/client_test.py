# coding: utf-8
import time
import os
import json
import psutil
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
                "CommitMinDeposit": 1.5,
                "Fee": 11,
                "Balance": {"TNC": 110},
                "alias": "test"
            }
        }
        req_url = "http://127.0.0.1:{}/".format(8077 + x - 1)
        # pprint(message)
        # req_url = ["http://192.168.205.221:8077/"]
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
    jsonrpcclient.request("http://127.0.0.1:{}".format(start_req_port + f_pk_id - 1), 'SyncChannel', json.dumps(message))
    jsonrpcclient.request("http://127.0.0.1:{}".format(start_req_port + r_pk_id - 1), 'SyncChannel', json.dumps(message))

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

# process = psutil.Process(449)
def log_process_memory_cpu_used(process, pids):
    rss = process.memory_info().rss/1024/1024
    cpu_percent = process.cpu_percent()
    pid_index = pids.index(process.pid)
    with open("test/pk{}_cpu_memory.txt".format(pid_index + 1), "a") as fs:
        fs.write("cpu used: {}%    memory used: {}MB\n".format(cpu_percent, rss))

if __name__ == "__main__":
    # sync_wallet_data(1)
    ############ 4、5、6 ############
    # sync_channel("pk4@localhost:8092", "pk5@localhost:8093")
    # time.sleep(5)
    # sync_channel("pk4@localhost:8092", "pk6@localhost:8094")
    # time.sleep(5)
    # sync_channel("pk5@localhost:8093", "pk6@localhost:8094")

    # sync_channel("pk4@localhost:8092", "pk2@localhost:8090")

    ############ 1、2、3 ############
    # sync_wallet_data(2)
    # time.sleep(5)
    # sync_channel("pk1@localhost:8089", "pk3@localhost:8091")
    # time.sleep(5)
    # sync_channel("pk1@127.0.0.1:8089", "pk2@127.0.0.1:8090")
    # time.sleep(5)
    # sync_channel("pk3@localhost:8091", "pk2@localhost:8090")
    # sync_channel("pk4@localhost:8092", "pk3@localhost:8091")
    ############3、4 ############
    # sync_channel("pk3@localhost:8091", "pk4@localhost:8092")
    ############1、5 ############
    # sync_channel("pk1@localhost:8089", "pk5@localhost:8093")
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
    # for x in range(1000):
    #     triggle_tx("pk2@localhost:8090", "pk4@localhost:8092")
    #     print(x)
    #     time.sleep(0.04)
    # sync_wallet_data(1)
    # triggle_tx("pk1@localhost:8089", "pk5@localhost:8093")
    #print(os.getpid())
    # log_process_memory_cpu_used(449)
    # print(psutil.cpu_count())
    # print(psutil.cpu_count(logical=False))
    # pids = [22711,23180,23671,24080,24491]
    # processs = [psutil.Process(pid) for pid in pids]
    # for x in range(900000):
    #     time_start
    #     triggle_tx("pk2@localhost:8090", "pk5@localhost:8093")
    #     time.sleep(0.04)
    #     if x%7500 == 0:
    #         for process in processs:
    #             log_process_memory_cpu_used(process,pids)
    message = {
        "MessageType":"PaymentAck",
        "Receiver":"036e61fcc048800614240cb2c7a3d116203d620d6f1aadf7ef561b295ccba02700@106.15.91.150:8089",
        "MessageBody": {
            "PaymentLink": "fdbqsugvouasvbowubvuiwebvebvowbv"
        }
    }
    # jsonrpcclient.request("http://localhost:8077", 'TransactionMessage', json.dumps(message))
    "02442f3eda23eba03aadb02bb25ccb0b680748eb70f4ef96906425ebffc289b103@106.15.91.150:8089"
    message1 = {
        "MessageType":"AddChannel",
        "MessageBody": {
            "Founder":  "pk1@localhost:8089",
            "Receiver": "pk2@localhost:8089",
            "Balance": {
                "pk2@localhost:8089": {
                    "NEO": 10
                },
                "pk1@localhost:8089": {
                    "NEO": 10
                }
            }
        }
    }
    message2 = {
        "MessageType":"AddChannel",
        "MessageBody": {
            "Founder":  "pk1@localhost:8089",
            "Receiver": "pk3@localhost:8089",
            "Balance": {
                "pk3@localhost:8089": {
                    "NEO": 10
                },
                "pk1@localhost:8089": {
                    "NEO": 10
                }
            }
        }
    }
    message3 = {
        "MessageType":"AddChannel",
        "MessageBody": {
            "Founder":  "pk2@localhost:8089",
            "Receiver": "pk3@localhost:8089",
            "Balance": {
                "pk3@localhost:8089": {
                    "NEO": 10
                },
                "pk2@localhost:8089": {
                    "NEO": 10
                }
            }
        }
    }
    message_1 = {
            "MessageBody": {
            "Publickey": "pk1",
            "Ip": "0.0.0.0:20556",
            "CommitMinDeposit": 3,
            "Fee": 2,
            "Balance": {"NEO": 10},
            "alias": "trinity2"
        }
    }
    message_2 = {
            "MessageBody": {
            "Publickey": "pk2",
            "Ip": "0.0.0.0:20556",
            "Channel":{
                "TNC":
                {
                    "CommitMinDeposit": 1,   # the min commit deposit
                    "CommitMaxDeposit": 5000,# the max commit deposit
                    "Fee": 0.01 # gateway fee
                }
            },
            "Balance": {"NEO": 10},
            "alias": "trinity1"
        }
    }
    message_3 = {
            "MessageBody": {
            "Publickey": "pk3",
            "Ip": "0.0.0.0:20554",
            "Channel":{
                "TNC":
                {
                    "CommitMinDeposit": 1,   # the min commit deposit
                    "CommitMaxDeposit": 5000,# the max commit deposit
                    "Fee": 0.01 # gateway fee
                }
            },
            "Balance": {"NEO": 10},
            "alias": "trinity1"
        }
    }
    message = {
        "MessageType": "Founder", 
        "Sender": "03c9c849a0bb84284b4cbc2a67ee3cc9523e050c48aa9aedf9998972bd44c7b826@localhost:8089", 
        "Receiver": "037e164ccc6b7e9db6d6c2d421c8ac13d4399e5408d27c017a6c871219899cb251@localhost:8766",
        "MessageBody": {
            "AssetType": "TNC"
        }
    }
    # jsonrpcclient.request("http://localhost:8077", 'SyncWalletData', json.dumps(message_1))
    # jsonrpcclient.request("http://localhost:8077", 'SyncWalletData', json.dumps(message_2))
    # jsonrpcclient.request("http://localhost:8077", 'SyncWalletData', json.dumps(message_3))
    # time.sleep(5)
    # jsonrpcclient.request("http://localhost:8077", 'SyncChannel', json.dumps(message1))
    # time.sleep(5)
    jsonrpcclient.request("http://localhost:8077", 'SyncWalletData', json.dumps(message_2))
    jsonrpcclient.request("http://localhost:8077", 'SyncWalletData', json.dumps(message_3))
    # time.sleep(5)
    # jsonrpcclient.request("http://localhost:8077", 'SyncChannel', json.dumps(message1))

    # jsonrpcclient.request("http://localhost:8077", 'SyncChannel', json.dumps(message1))
    # jsonrpcclient.request("http://118.89.44.106:8077", 'SyncChannel', json.dumps(message1))
    # jsonrpcclient.request("http://localhost:8077", 'SyncWalletData', json.dumps(message))


   
