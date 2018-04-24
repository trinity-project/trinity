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
                pass
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