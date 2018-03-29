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
    text = text.replace(cg_end_mark, "")
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
    return encode_bytes(message)

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

def generate_ack_sync_wallet_msg():
    message = {
        "MessageType": "AckSyncWallet",
        "MessageBody" {}
    }
    return message

def handletransactionmessage(bdata):
    data = utils.decode_bytes(bdata)
    receiver_ip_port = data["Receiver"].split("@")[1]
    receiver_pk = data["Receiver"].split("@")[0]
    self_ip_port = node["wallet_info"]["url"].split("@")[1]
    self_pk = node["wallet_info"]["url"].split("@")[0]
    # 交易对象可能是自己或者是挂在自己的spv
    if receiver_ip_port == self_ip_port:
        #交易对象是自己 无手续费 直接扔给wallet处理
        if receiver_pk == self_pk:
            self._send_jsonrpc_msg("TransactionMessage", json.dumps(data))
        #交易对象不是自己 极有可能是挂在自己上面的spv 需要手续费 需要check自己的散列表 验证是spv的身份
        else:
            # 交易对象是挂在自己上面的spv
            if receiver_pk in node["spv_table"].find(self_pk):
                pass
            # spv验证失败 可能已掉线或者有人冒充
            else:
                pass
    # 交易对象是其他节点或挂在其他节点上的spv 需要手续费
    else:
        # 消息已经包含路由信息的情况
        if data.get("RouterInfo"):
            router = data["RouterInfo"]
            full_path = router["FullPath"]
            next_jump = router["Next"]
            # 交易信息是传给自己的
            if next_jump == self_ip_port:
                # 到达终点
                if full_path(len(full_path)-1) == next_jump:
                    # todo spv or itself
                # 继续传递信息
                else:
                    new_next_jump = full_path(full_path.index(next_jump) + 1)
                    data["RouterInfo"]["Next"] = new_next_jump
                    self.tcp_ip_port_dict.get(route["Next"]).send(utils.encode_bytes(data))
                    message = utils.generate_trigger_transaction_msg(
                        node["wallet_info"]["url"], # self
                        new_next_jump,
                        data["MessageBody"]["Value"] - node["wallet_info"]["Fee"]
                    )
                    self._send_jsonrpc_msg("TransactionMessage", json.dumps(message))
            # 交易信息传错了 暂时作丢弃处理
            else:
                pass
        # 消息不包含路由的信息的情况
        else:
            receiver = data["Receiver"]
            full_path = node["route_tree"].find_router(receiver)
            # 没有找到通道路由
            if not len(full_path):
                print("not found path to the distination")
                return
            else:
                next_index = full_path.index(self_ip_port) + 1
                next_jump = full_path[next_index]
                router = {
                    "FullPath": full_path,
                    "Next": next_jump
                }
                data["RouterInfo"] = router
                self.tcp_ip_port_dict.get(route["Next"]).send(utils.encode_bytes(data))
                message = utils.generate_trigger_transaction_msg(
                    data["Sender"],
                    route["Next"],
                    data["MessageBody"]["Value"] - node["wallet_info"]["Fee"]
                )
                self._send_jsonrpc_msg("TransactionMessage", json.dumps(data))