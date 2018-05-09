# coding: utf-8
"""\
gateway utils
"""
import json
import re
from config import cg_end_mark, cg_bytes_encoding, cg_wsocket_addr,\
 cg_tcp_addr, cg_public_ip_port, cg_remote_jsonrpc_port
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

def get_wallet_addr(current_url, asset_type, net_tops):
    """
    get the server addr which wallet start on
    """
    return (get_wallet_attribute("WalletIp", current_url, asset_type, net_tops), cg_remote_jsonrpc_port)

def get_wallet_attribute(attr_name, current_url, asset_type, net_tops):
    """
    return wallet attr by attr_name
    """
    pk = get_public_key(current_url)
    return net_tops[asset_type].get_node_dict(pk).get(attr_name)

def check_is_spv(url):
    """
    check the sender or receiver is spv
    """
    ip_port = get_ip_port(url)
    if ip_port == cg_public_ip_port.split(":")[0] + str(cg_wsocket_addr[1]):
        return True
    else:
        return False

def check_is_owned_wallet(url):
    """
    check the sender or receiver is the wallet \n
    which attached this gateway
    """
    ip_port = get_ip_port(url)
    return ip_port == cg_public_ip_port

def check_is_same_gateway(founder, receiver):
    """
    check the founder and receiver are attached same gateway
    """
    return get_ip_port(founder) == get_ip_port(receiver)

def select_channel_peer_source(founder, receiver):
    """
    just for the wallet not in the same gateway\n
    :param founder:  url\n
    :param receiver: url\n
    :param wallets:  wallet dict\n
    """
    if get_ip_port(founder) == cg_public_ip_port:
        return receiver, founder
    else:
        return founder, receiver

def json_to_dict(str_json):
    return json.loads(str_json)

def check_end_mark(bdata):
    text = decode_bytes(bdata, target="str")
    return len(re.findall(cg_end_mark + "$", text))


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

def make_topo_node_data(wallet):
    """
    :param wallet: _Wallet instance
    """
    return {
        "Publickey": wallet.public_key,
        "Name": wallet.name,
        "Deposit": wallet.deposit,
        "Fee": wallet.fee,
        "Balance": wallet.balance,
        "Ip": cg_public_ip_port,
        "WalletIp": wallet.ip,
        "SpvList": []
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

def _make_router(path, full_path, net_topo):
    total_fee = 0
    for nid in path:
        node = net_topo.get_node_dict(nid)
        url = nid + "@" + node.get("Ip")
        fee = node.get("Fee")
        full_path.append((url, fee))
        index = path.index(nid)
        if index > 0 and index < len(nids) - 1:
            total_fee = total_fee + fee
    if not len(full_path):
        router = None
    else:
        next_jump = full_path[0][0]
        router = {
            "FullPath": full_path,
            "Next": next_jump
        }
    return router

def search_route_for_spv(sender, receiver, net_topo, spv_table):

    """
    :param sender: spv self url
    :param receiver: tx target url
    :param net_topo:
    :param spv_table: 
    """
    receiver_pk = get_public_key(receiver)
    spv_pk = get_public_key(spv_pk)
    source_wallet_pks = spv_table.find_keys(spv_pk)
    path = []
    full_path = []
    # spv-wallet-..-spv tx 
    if check_is_spv(receiver):
        target_wallet_pks = spv_table.find_keys(receiver_pk)
        common_wallet_set = set(source_wallet_pks).intersection(set(target_wallet_pks))
        # spv-wallet-spv
        if len(common_wallet_set):
            wallet_pk = list(common_wallet_set)[0]
            path = [wallet_pk]
        # spv-wallet-..-wallet-spv
        else:
            for s_pk in source_wallet_pks:
                if len(path): break
                for t_pk in target_wallet_pks:
                    path = net_topo.find_shortest_path_decide_by_fee(s_pk, t_pk)
                    if len(path): break
    # spv-wallet-..-wallet tx
    else:
        for s_pk in source_wallet_pks:
            path = net_topo.find_shortest_path_decide_by_fee(s_pk, receiver_pk)
            if len(path): break
    return _make_router(path, full_path, net_topo)

def search_route_for_wallet(sender, receiver, net_topo, spv_table):
    
    """
    :param sender: spv self url
    :param receiver: tx target url
    :param net_topo:
    :param spv_table: 
    """
    rev_pk = get_public_key(receiver)
    sed_pk = get_public_key(sender)
    path = []
    full_path = []
    # wallet-wallet-..-spv
    if check_is_spv(receiver):
        target_wallet_pks = spv_table.find_keys(receiver_pk)
        for t_pk in target_wallet_pks:
            path = net_topo.find_shortest_path_decide_by_fee(sed_pk, t_pk)
            if len(path): break
    # wallet-wallet-..-wallet
    else:
        path = net_topo.find_shortest_path_decide_by_fee(sed_pk, rev_pk)
    return _make_router(path, full_path, net_topo)
