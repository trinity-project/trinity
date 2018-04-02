# coding: utf-8
"""\
gateway 工具函数模块
"""
import json
import time
import re
import copy
from config import cg_end_mark

common_msg_dict = {
    "MessageType": "",
    "Sender": "",
    "Receiver": ""
}

def _remove_end_mark(text):
    patter = re.compile(cg_end_mark + "$")
    text = re.sub(patter, "", text)
    # text = text.replace(cg_end_mark, "")
    return text

def _add_end_mark(text):
    text = text + cg_end_mark
    return text


def decode_bytes(bdata, target="dict"):
    """
    解析收到的字节包\n
    一般情况直接返回相应的 python obj\n
    如果传入的target为"str" 则返回字符串
    """
    data = bdata.decode("utf-8")
    print("########",data,"*******")
    if target == "dict":
        data = _remove_end_mark(data)
        data = json.loads(data)
    return data

def encode_bytes(data):
    """
    编码成字节包\n
    python obj 序列化json字符\n
    并加入消息结束标识符 eof\n
    """
    if type(data) != str:
        data = json.dumps(data)
    data = _add_end_mark(data)
    return data.encode("utf-8")

def json_to_dict(str_json):
    return json.loads(str_json)

def check_end_mark(bdata):
    """
    检测数据包是否包含消息结束标识符 eof\n
    如果包含则返回大于0的整数\n
    否则返回0
    """
    text = decode_bytes(bdata, target="str")
    return len(re.findall(cg_end_mark + "$", text))

def check_is_owned_wallet(receiver_url, local_url):
    # check ip_port first
    receiver_url_split = receiver_url.split("@")
    local_url_split = local_url.split("@")
    if not len(receiver_url_split) or receiver_url_split[0] != local_url_split[0]:
        return False
    else:
        return True

def find_transport(transports, url):
    public_key = url.split("@")[0]
    for transport in transports:
        pass

def get_public_key(url):
    return url.split("@")[0]

def get_ip_port(url):
    return url.split("@")[1]

def get_addr(url):
    ip_port = (url.split("@")[1]).split(":")
    return (ip_port[0], ip_port[1])

def parse_url(url):
    return url.split("@")


def generate_ack_node_join_msg(sender, receiver, node_list):
    message = copy.deepcopy(common_msg_dict)
    message["MessageType"] = "AckJoin"
    message["Sender"], message["Receiver"] = sender, receiver
    message["NodeList"] = list(node_list)
    return encode_bytes(message)

def generate_error_msg(sender, receiver, reason, mode="bytes"):
    message = copy.deepcopy(common_msg_dict)
    message["Sender"], message["Receiver"] = sender, receiver
    message["MessageType"] = "ErrorMessage"
    if mode == "btyes":
        return encode_bytes(message)
    elif mode == "str":
        return json.dumps(message)

def generate_ack_node_add_channel_msg(sender, receiver):
    message = copy.deepcopy(common_msg_dict)
    message["MessageType"] = "AckAddChannel"
    message["Sender"], message["Receiver"] = sender, receiver
    return encode_bytes(message)

def generate_join_net_msg():
    message = {
        "MessageType": "JoinNet"
    }
    return message

def generate_ack_show_node_list(node_list):
    message = {
        "MessageType": "AckShowNodeList",
        "NodeList": list(node_list)
    }
    return json.loads(message)

def generate_trigger_transaction_msg(sender, receiver, value):
    message = {
        "MessageType": "CreateChannelMessage",
        "Receiver": receiver,
        "Sender": sender,
        "MessageBody": {
            "AssetType":"TNC",
            "Value": value
        }
    }
    return message

def generate_ack_sync_wallet_msg(url):
    message = {
        "MessageType": "AckSyncWallet",
        "MessageBody":{
            "Url": url
        }
    }
    return message

def generate_ack_router_info_msg(router):
    message = {
        "MessageType": "AckRouterInfo",
        "RouterInfo": router
    }
    return message

def generate_ack_TransactionMessage():
    message = {
        "MessageType": "AckTransactionMessage"
    }
    return message

def generate_node_list_msg(node):
    route_tree = node["route_tree"]
    if not route_tree.root:
        spv_table = node["spv_table"]
        pk, ip_port = node["wallet_info"]["url"].split("@")
        route_tree.create_node(
            tag="node",
            identifier=ip_port,
            data={
                "Ip": ip_port,
                "Pblickkey": pk,
                "Name": node["name"],
                "Deposit": node["wallet_info"]["deposit"],
                "Fee": node["wallet_info"]["fee"],
                "SpvList": [] if not node["spv_table"].find(ip_port) else node["spv_table"].find(ip_port)
            }
        )
        node_data = route_tree.to_dict(with_data=True)
    else:
        node_data = route_tree.to_dict(with_data=True)
    message = {
        "MessageType": "NodeList",
        "Nodes": node_data
    }
    return message

def generate_sync_tree_msg(route_tree, sender):
    message = {
        "MessageType": "SyncChannelState",
        "Sender": sender,
        "MessageBody": route_tree.to_dict(with_data=True)
    }
    return message