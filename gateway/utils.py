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

def get_peers_form_db(address):
    condition = {
        "$or": [{"src_addr": address}, {"dest_addr": address}]
    }
    channels = APIChannel.batch_query_channel(filters=condition)
    channels = APIChannel.batch_query_channel(filters={"src_addr":address})
    channeld = APIChannel.batch_query_channel(filters={"dest_addr":address})