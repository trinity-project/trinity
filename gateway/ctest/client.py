# coding: utf-8
import socket
import time
import os
import sys
r_path = os.getcwd()
print(r_path)
sys.path.append(r_path)
import utils
# import threading

class Client:
    connected = False
    def __init__(self):
        self.sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)

    def _connect(self, addr):
        """
        conect_ex返回0表示连接成功，否则连接失败(出错)
        """
        if not self.connected:
            if not self.sock.connect_ex(addr):
                self.connected = True
            else:
                raise Exception("connection error")
                # pass
                # todo 连接出错处理、统计
    
    def _close(self):
        """
        关闭连接 释放资源
        """
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()

    def send(self, addr, data):
        """
        返回已发送的数据字节数，可能小于data的字节数
        """
        self._connect(addr)
        if self.connected:
            return self.sock.send(data)
    

    def recv(self):
        """
        数据包大小可能会超过buffersize\n
        所以这里使用循环从socket读取数据\n
        如果最终返回空字符，则说明连接已断开\n
        如果读取到结束标识符，说明数据已接收完毕
        """
        bdata = b""
        while True:
            temp = self.sock.recv(1024)
            bdata = bdata + temp
            if not bdata:
                self._close()
                break
            elif utils.check_end_mark(temp):
                break
        return utils.decode_bytes(bdata)

if __name__ == "__main__":
    import struct
    client = Client()
    addr = ("127.0.0.1", 8089)
    version = 0x000001
    cmd = 0x000065
    # bdata = data.encode("utf-8")
    # header = [version, len(b"helloddddddddddddfffffffpk1"), cmd]
    # header_pack = struct.pack("!3I", *header)
    # client.send(addr, header_pack + b"helloddddddddddddfffffffpk1")
    # bdata = b"worldgggggggggggggggggggggpk2"
    message = {
        "MessageType":"AddChannel",
        "MessageBody": {
            "Founder": "pk1",
            "Receiver": "pk2"
        }
    }
    import json
    bdata = json.dumps(message).encode("utf-8")
    header = [version, len(bdata), cmd]
    header_pack = struct.pack("!3I", *header)
    
    
    client.send(addr, header_pack + bdata)
    # time.sleep(0.4)
    # client.send(addr, bdata[10:])

    # client.send(addr, b"p1geeeeeeeerrrrrrrrrrr")
    # client.send(addr, b"p2ffffffrrrrrrrrr")
    # client.send(addr, b"p3eeeeeee55555555555555")
    # client.send(addr, b"p43333333332222222222222222222/")