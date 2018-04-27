# coding: utf-8
"""
module for tcp msg pack and unpack
"""
import struct
import json

class Datagram:
    """
    the tcp datagram struct\n
    #######################\n
    ver    body_size    cmd\n
    #######################\n
        body    content    \n
    #######################\n
    """
    header_size = 12
    @classmethod
    def pack(cls, message):
        version = 0x000001
        cmd = 0x000065
        bdata = json.dumps(message).encode("utf-8")
        header = [version, len(bdata), cmd]
        header_pack = struct.pack("!3I", *header)
        return header_pack + bdata

    @classmethod
    def unpack(cls, data_buffer):
        while True:
            if len(data_buffer) < cls.header_size:
                break
            header_pack = struct.unpack("!3I", data_buffer[:cls.header_size])
            body_size = header_pack[1]
            # package split situation
            if len(data_buffer) < cls.header_size + body_size:
                break
            body = data_buffer[cls.header_size:cls.header_size+body_size]
            # data_handle(header_pack, body)
            # package splicing
            data_buffer = data_buffer[cls.header_size+body_size:]

