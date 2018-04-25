# coding: utf-8
import time
import os
import json
import psutil
import random
# import asyncio
from client import Client
from pprint import pprint
import jsonrpcclient

def sync_wallet_data():
    ips = [
            "192.168.204.112",
            "192.168.205.181"
            # "192.168.205.217",
            # "192.168.205.181",
            # "192.168.205.180",
            # "192.168.205.179",
            # "192.168.205.182",
            # "192.168.205.178",
            # "192.168.205.167",
            # "192.168.205.166",
        ]
    for ip in ips:
        message = {
            "MessageBody": {
                "Publickey": "pk{}".format(ips.index(ip) + 1),
                "CommitMinDeposit": 1,
                "Fee": random.randint(1,10),
                "Balance": {"TNC": 10},
                "alias": "trinity1"
            }
        }
        req_url = "http://{}:8077/".format(ip)
        print(req_url)
        jsonrpcclient.request(req_url, 'SyncWalletData', json.dumps(message))

def sync_channel(founder, receiver):
    message = {
        "MessageType":"AddChannel",
        "MessageBody": {
            "Founder": founder,
            "Receiver": receiver
        }
    }
    f_url = founder.split("@")[1].split(":")[0]
    r_url = receiver.split("@")[1].split(":")[0]
    print(f_url,r_url)
    jsonrpcclient.request("http://{}:8077/".format(f_url), 'SyncChannel', json.dumps(message))
    jsonrpcclient.request("http://{}:8077/".format(r_url), 'SyncChannel', json.dumps(message))

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
    # start_ip = "192.168.205.217"
    sync_wallet_data()
    # # # ############ 4、5、6 ############
    # sync_channel("pk4@192.168.205.179:8089", "pk5@192.168.205.182:8089")
    # time.sleep(5)
    # sync_channel("pk4@192.168.205.179:8089", "pk6@192.168.205.178:8089")
    # time.sleep(5)
    # sync_channel("pk5@192.168.205.182:8089", "pk6@192.168.205.178:8089")
    # time.sleep(5)
    # # # # ############ 1、2、3 ############
    # # # # sync_wallet_data(6)
    # time.sleep(5)
    # sync_channel("pk1@192.168.205.217:8089", "pk3@192.168.205.180:8089")
    time.sleep(5)
    sync_channel("pk1@192.168.204.112:8089", "pk2@192.168.205.181:8089")
    # time.sleep(5)
    # sync_channel("pk3@192.168.205.180:8089", "pk2@192.168.205.181:8089")
    # time.sleep(5)
    
    ############2、4 ############
    # time.sleep(5)
    # sync_channel("pk4@192.168.205.179:8089", "pk2@192.168.205.181:8089")
    ############7、8 ############
    # sync_channel("pk7@192.168.205.167:8089", "pk8@192.168.205.166:8089")
    ############7、1 ############
    # time.sleep(5)
    # sync_channel("pk7@192.168.205.167:8089", "pk1@192.168.205.217:8089")
    ############8、1 ############
    # time.sleep(5)
    # sync_channel("pk8@192.168.205.166:8089", "pk1@192.168.205.217:8089")
    ############2、6 ############
    # time.sleep(5)
    # sync_channel("pk6@192.168.205.178:8089", "pk2@192.168.205.181:8089")
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

        
   
