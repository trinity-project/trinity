# coding: utf-8
"""\
gateway utils
"""
import json
import time
import re
import copy
from config import cg_end_mark, cg_bytes_encoding
import os
import sys
path = os.getcwd().replace("/gateway", "")
sys.path.append(path)
print(path)
# from sserver.model.channel_model import APIChannel

common_msg_dict = {
    "MessageType": "",
    "Sender": "",
    "Receiver": ""
}
tcp_msg_types = [
    "RegisterChannel",
    "SyncChannelState",
    "ResumeChannel",
     "Rsmc",
     "FounderSign",
     "Founder",
     "RsmcSign",
     "FounderFail",
     "Settle",
     "SettleSign",
     "SettleFail",
     "RsmcFail",
     "Htlc",
     "HtlcSign",
     "HtlcFail"
]

request_handle_result = {
    "invalid": 0,
    "correct": 1
}

def _remove_end_mark(text):
    patter = re.compile(cg_end_mark + "$")
    text = re.sub(patter, "", text)
    return text

def _add_end_mark(text):
    text = text + cg_end_mark
    return text


def decode_bytes(bdata, target="dict"):
    """
    :param bdata: bytes type\n
    :param target: "dict" or "str"\n
    :return: python obj or str
    """
    data = bdata.decode(cg_bytes_encoding)
    if target == "dict":
        data = _remove_end_mark(data)
        data = json.loads(data)
    return data

def encode_bytes(data):
    """
    encode python obj to bytes data\n
    :return: bytes type
    """
    if type(data) != str:
        data = json.dumps(data)
    data = _add_end_mark(data)
    return data.encode(cg_bytes_encoding)

def json_to_dict(str_json):
    return json.loads(str_json)

def check_end_mark(bdata):
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

def load_channel_state(tree):
    with open("tree.json", mode="r") as fs:
        json.loads(fs.read())

def save_channel_state(tree):
    with open("tree.json", mode="w") as fs:
        fs.write(json.dumps(tree.to_json(with_data=True)))

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
        "Broadcast": True,
        "MessageBody": route_tree.to_dict(with_data=True)
    }
    return message

def generate_sync_graph_msg(sync_type, sender, **kwargs):
    """
    :param sync_type: "add_single_edge|remove_single_edge|update_node_data|add_whole_graph"\n
    :param kwargs: {route_graph,source,target,node}
    """
    message = {
        "MessageType": "SyncChannelState",
        "SyncType": sync_type
        "Sender": sender,
        "Broadcast": True,
        "Source": kwargs["source"],
        "Target": kwargs["target"]
        # "MessageBody": route_tree.to_json()
    }
    if sync_type == "add_whole_graph":
        message["MessageBody"] = kwargs["route_graph"].to_json()
    elif sync_type == "add_single_edge":
        message["MessageBody"] = kwargs["node"]
    elif sync_type == "remove_single_edge":
        pass
    elif sync_type == "update_node_data":
        message["MessageBody"] = route_graph.node
    return message

def generate_resume_channel_msg(sender):
    message = {
        "MessageType": "ResumeChannel",
        "Sender": sender
    }
    return message

def del_dict_item_by_value(dic, value):
    values = list(dic.values())
    if value in values:
        keys = list(dic.keys())
        del_index = values.index(value)
        del dic[keys[del_index]]

def check_tcp_message_valid(data):
    if type(data) != dict:
        return False
    elif not data.get("MessageType"):
        return False
    elif data.get("MessageType") not in tcp_msg_types:
        return False
    elif not data.get("Sender"):
        return False
    else:
        return True

def get_peers_form_db(address):
    condition = {
        "$or": [{"src_addr": address}, {"dest_addr": address}]
    }
    channels = APIChannel.batch_query_channel(filters=condition)
    channels = APIChannel.batch_query_channel(filters={"src_addr":address})
    channeld = APIChannel.batch_query_channel(filters={"dest_addr":address})