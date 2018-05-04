# coding: utf-8
"""\
gateway utils
"""
import json
import re
from config import cg_end_mark, cg_bytes_encoding, cg_wsocket_addr,\
 cg_tcp_addr, cg_public_ip_port
import os
import sys
path = os.getcwd().replace("/gateway", "")
sys.path.append(path)
print(path)
from model.channel_model import APIChannel
from model.node_model import APINode
import struct

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
        # data = _remove_end_mark(data)
        data = json.loads(data)
    return data

def encode_bytes(data):
    """
    encode python obj to bytes data\n
    :return: bytes type
    """
    if type(data) != str:
        data = json.dumps(data)
    # data = _add_end_mark(data)
    version = 0x000001
    cmd = 0x000065
    bdata = data.encode(cg_bytes_encoding)
    header = [version, len(bdata), cmd]
    header_pack = struct.pack("!3I", *header)
    return header_pack + bdata
    # return data.encode(cg_bytes_encoding)

def check_is_spv(url):
    """
    check the sender or receiver is spv
    """
    ip_port = get_ip_port(url)
    if ip_port == cg_public_ip_port.split(":")[0] + str(cg_wsocket_addr[1]):
        return True
    else:
        return False

def check_is_same_gateway(founder, receiver):
    """
    check the founder and receiver are attached same gateway
    """
    return get_ip_port(founder) == get_ip_port(receiver)

def select_channel_peer(founder, receiver, wallets):
    """
    just for the wallet not in the same gateway\n
    :param founder:  url\n
    :param receiver: url\n
    :param wallets:  wallet dict\n
    """
    f_pk = get_public_key(founder)
    if wallets.get(f_pk):
        return receiver
    else:
        return founder

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

def get_public_key(url):
    return url.split("@")[0]

def get_ip_port(url):
    return url.split("@")[1]

def get_addr(url):
    ip_port = (url.split("@")[1]).split(":")
    return (ip_port[0], int(ip_port[1]))

def parse_url(url):
    return url.split("@")

def del_dict_item_by_value(dic, value):
    values = list(dic.values())
    if value in values:
        keys = list(dic.keys())
        del_index = values.index(value)
        del dic[keys[del_index]]

def make_kwargs_for_wallet(data):
    """
    :param data: dict type
    """
    return {
        "ip": data.get("Ip"),
        "public_key": data.get("Publickey"),
        "name": data.get("alias"),
        "deposit": data.get("CommitMinDeposit"),
        "fee": data.get("Fee"),
        "asset_type": list(data.get("Balance").items())[0][0],
        "balance": list(data.get("Balance").items())[0][1]
    }

def get_channels_form_db(address):
    condition = {
        "$or": [{"src_addr": address}, {"dest_addr": address}]
    }
    channels = APIChannel.batch_query_channel(filters=condition)
    print(channels)
    return channels.get("content")

def get_wallet_from_db(ip):
    nodes = APINode.batch_query_node(filters={"ip": ip})
    # print(nodes)
    return nodes.get("content")

def add_or_update_wallet_to_db(wallet):
    if not wallet:
        return
    addr = wallet["url"]
    if APINode.query_node(addr).get("content"):
        APINode.update_node(
            addr,
            balance=wallet["balance"],
            deposit=wallet["deposit"],
            fee=wallet["fee"],
            name=wallet["name"]
        )
    else:
        APINode.add_ransaction(
            wallet["url"],
            get_public_key(wallet["url"]),
            get_ip_port(wallet["url"]),
            wallet["balance"],
            wallet["deposit"],
            wallet["fee"],
            wallet["name"],
            "alive"
        )

