# coding: utf-8
"""\
gateway 工具函数模块
"""
import json
import time
import re
from config import cg_end_mark

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
    并加入消息结束标识符 /end\n
    """
    data = json.dumps(data)
    data = _add_end_mark(data)
    return data.encode("utf-8")

def check_end_mark(bdata):
    """
    检测数据包是否包含消息结束标识符 /end\n
    如果包含则返回大于0的整数\n
    否则返回0
    """
    text = decode_bytes(bdata, target="str")
    return len(re.findall(cg_end_mark + "$", text))
