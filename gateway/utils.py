# coding: utf-8
"""\
gateway utils
"""
import json
import re
from config import cg_end_mark, cg_bytes_encoding, cg_wsocket_addr,\
 cg_tcp_addr, cg_public_ip_port, cg_remote_jsonrpc_addr, cg_local_jsonrpc_addr
import os
import sys
path = os.getcwd().replace("/gateway", "")
sys.path.append(path)
# from model.channel_model import APIChannel
# from model.node_model import APINode
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

def save_wallet_cli(clients):
    with open("wcli.json", "w") as fs:
        text = json.dumps(list(clients.keys()))
        fs.write(text)

def get_wallet_clis():
    with open("wcli.json", "r") as fs:
        return json.loads(fs.read())

def get_wallet_addr(url, clients):
    """
    get the server addr which wallet cli rpc start on
    """
    pk = get_public_key(url)
    wallet = get_all_active_wallet_dict(clients).get(pk)
    if wallet:
        ip, port = wallet.cli_ip.split(":")
        wallet_addr = (ip, int(port))
    else:
        wallet_addr = ("0.0.0.0", 0)
    return wallet_addr

def get_wallet_attribute(attr_name, current_url, asset_type, net_tops):
    """
    return wallet attr by attr_name
    """
    pk = get_public_key(current_url)
    return net_tops[asset_type].get_node_dict(pk).get(attr_name)

def get_all_active_wallet_dict(clients):

    """
    :param clients: wallet client dict
    """
    wallets = {}
    for key in clients:
        active_wallet = clients[key].opened_wallet
        if active_wallet:
            wallets[active_wallet.public_key] = active_wallet
    return wallets

def get_all_active_wallet_keys_iterator(clients):

    """
    :param clients: wallet client dict
    """
    for key in clients:
        active_wallet = clients[key].opened_wallet
        if active_wallet:
            yield active_wallet.public_key

def check_is_spv(url):
    """
    check the sender or receiver is spv
    """
    port = get_addr(url)[1]
    if port == cg_wsocket_addr[1]:
        return True
    else:
        return False

def check_is_owned_wallet(url, clients):
    """
    check the sender or receiver is the wallet \n
    which attached this gateway

    @ return: owned: Wallet registered at this gateway if True, otherwise, False.
              state: Wallet has opened if true, otherwise, False.
    """
    pk, ip_port = parse_url(url)

    if ip_port != cg_public_ip_port:
        return False, False

    if pk not in get_all_active_wallet_keys_iterator(clients):
        # probably the wallet has been closed.
        return True, False

    return True, True

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
    fee_dict = {}
    channel_config = data.get("Channel")
    if channel_config:
        for key in channel_config:
            fee_dict[key] = channel_config[key].get("Fee")
    return {
        "ip": data.get("Ip"),
        "public_key": data.get("Publickey"),
        "name": data.get("alias"),
        # "deposit": data.get("CommitMinDeposit"),
        "fee": fee_dict,
        "balance": data.get("Balance")
    }

def make_topo_node_data(wallet, asset_type):
    """
    :param wallet: _Wallet instance
    """
    return {
        "Publickey": wallet.public_key,
        "Name": wallet.name,
        "AssetType": asset_type,
        # "Deposit": wallet.deposit,
        "Fee": wallet.fee[asset_type],
        "Balance": wallet.channel_balance,
        "Ip": cg_public_ip_port,
        "WalletIp": wallet.cli_ip,
        "Status": wallet.status
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

def add_or_update_wallet_to_db(wallet, last_opened_pk):
    if not wallet:
        return
    public_key = wallet.public_key
    if APINode.query_node(public_key).get("content"):
        APINode.update_node(
            public_key,
            balance=wallet.balance,
            deposit=wallet.deposit,
            fee=wallet.fee,
            name=wallet.name
        )
    else:
        APINode.add_ransaction(
            public_key=wallet.public_key,
            cli_ip=wallet.cli_ip,
            ip=wallet.ip,
            balance=wallet.balance,
            deposit=wallet.deposit,
            fee=wallet.fee,
            name=wallet.name,
            status=wallet.status
        )
    if last_opened_pk:
        APINode.update_node(last_opened_pk, status=0)

def _make_router(path, full_path, net_topo):
    total_fee = 0
    for nid in path:
        node = net_topo.get_node_dict(nid)
        url = nid + "@" + node.get("Ip")
        fee = node.get("Fee")
        full_path.append((url, fee))
        index = path.index(nid)
        if index > 0 and index < len(path) - 1:
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

def _search_target_wallets(receiver, asset_type, magic):
    from network import Network
    from message import MessageMake
    addr = (get_addr(receiver)[0], cg_local_jsonrpc_addr[1])
    message = MessageMake.make_search_target_wallet(get_public_key(receiver), asset_type, magic)
    response = Network.send_msg_with_jsonrpc_sync("Search", addr, message)
    if response:
        target = response.get("Wallets")
    else:
        target = []
    return target

def search_route_for_spv(sender, source_list, receiver, net_topo, asset_type, magic):

    """
    :param sender: spv self url
    :param source_list: spv channel_peers
    :param receiver: tx target url
    :param net_topo:
    :param asset_type: 
    """
    receiver_pk, rev_ip = parse_url(receiver)
    spv_pk, sed_ip = parse_url(sender)
    source_wallet_pks = []
    target_wallet_pks = []
    path = []
    full_path = []
    for source in source_list:
        source_pk = get_public_key(source)
        if net_topo.get_node_dict(source_pk)["Status"]:
            source_wallet_pks.append(source_pk)
    # spv-wallet-..-spv tx 
    if check_is_spv(receiver):
        # first think about sender and receiver attached in same gateway
        for key in net_topo.spv_table.find_keys(receiver_pk):
            if net_topo.get_node_dict(key)["Status"]:
                target_wallet_pks.append(key)
        common_wallet_set = set(source_wallet_pks).intersection(set(target_wallet_pks))
        # spv-wallet-spv
        if len(common_wallet_set):
            wallet_pk = list(common_wallet_set)[0]
            path = [wallet_pk]
        # spv-wallet-..-wallet-spv not attached in same gateway
        # search target wallet from remote gateway
        if not len(path) and sed_ip != rev_ip:
            target_wallet_pks = _search_target_wallets(receiver, asset_type, magic)
            if len(target_wallet_pks):
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

def search_route_for_wallet(sender, receiver, net_topo, asset_type, magic):
    
    """
    :param sender: spv self url
    :param receiver: tx target url
    :param net_topo:
    """
    rev_pk = get_public_key(receiver)
    sed_pk = get_public_key(sender)
    path = []
    full_path = []
    # wallet-wallet-..-spv
    if check_is_spv(receiver):
        target_wallet_pks = []
        # sender and receiver is attached same gateway(same ip)
        # search target wallet from local spv table
        if get_addr(sender)[0] == get_addr(receiver)[0]:
            for key in net_topo.spv_table.find_keys(receiver_pk):
                # check wallet is on-line
                if net_topo.get_node_dict(key)["Status"]:
                    target_wallet_pks.append(key)
        # search target wallet from remote spv table
        else:
            target_wallet_pks = _search_target_wallets(receiver, asset_type, magic)
        for t_pk in target_wallet_pks:
            path = net_topo.find_shortest_path_decide_by_fee(sed_pk, t_pk)
            if len(path): break
    # wallet-wallet-..-wallet
    else:
        path = net_topo.find_shortest_path_decide_by_fee(sed_pk, rev_pk)
    return _make_router(path, full_path, net_topo)

def make_edge_data(u_node, v_node):
    if not u_node or not v_node: return {}
    u_names = set(u_node["Balance"].keys())
    v_names = set(v_node["Balance"].keys())
    names = list(u_names.intersection(v_names))
    return {
        "weight": u_node["Fee"] + v_node["Fee"],
        "name": names[len(names) -1] if len(names) else "None"
    }

def asset_type_magic_patch(asset_type, data):
    magic = data.get("Magic") if isinstance(data, dict) else data
    if magic: 
        asset_type = asset_type + magic
    return asset_type

if __name__ == "__main__":
    d = {"a":1,"b":2}
    def get_keys_iterator(clients):
        """
        :param clients: wallet client dict
        """
        for key in clients:
            # active_wallet = clients[key].opened_wallet
            yield clients[key]
    print(get_keys_iterator(d))
    print(1 in get_keys_iterator(d))
    print(3 in get_keys_iterator(d))
    print(2 in get_keys_iterator(d))