# coding: utf-8
from asyncio import Protocol, get_event_loop
from config import cg_end_mark, cg_bytes_encoding, cg_tcp_addr, cg_debug_multi_ports
from utils import request_handle_result
from glog import tcp_logger
import struct
# from datagram import Datagram

class ProtocolManage():
    """
    tcp protocol(connection) manage class
    """
    def __init__(self):
        self.protocols = set()
        self.close_times = 0
        self.exc_close_times = 0
        self.rev_split_data_totals = []
        self.rev_data_split_times = 0
        self.rev_invalid_times = 0

    def register(self, protocol):
        self.protocols.add(protocol)

    def unregister(self, protocol):
        self.protocols.remove(protocol)

    def wrap(self, server):
        self.server = server

tcp_manager = ProtocolManage()

class TProtocol(Protocol):
    """
    Each client connection will create a new protocol instance
    """
    def __init__(self):
        super().__init__()
        self.received = bytes()
        self.rev_totals = 0
        self.send_totals = 0
        self.header_size = 12
        self.transport = None
        self.state = None
        # for wallet cli
        self.is_wallet_cli = False
        self.wallet_ip = None
    
    def connection_made(self, transport):
        self.state = "connected"
        self.transport = transport
        peername = transport.get_extra_info('peername')
        if not cg_debug_multi_ports:
            if cg_tcp_addr[1] ==  peername[1]:
                tcp_logger.info("connect the server %s", peername)
            else:
                tcp_logger.info("client %s connected", peername)
        else:
            if "80" in str(peername[1]):
                tcp_logger.info("connect the server %s", peername)
            else:
                tcp_logger.info("client %s connected", peername)
        tcp_manager.register(self)

    def data_received(self, data):
        # tcp_logger.info("receive %d bytes message from %s", body_size, self.get_peername())
        self.received = self.received + data
        # print(len(self.received))
        # print(self.received)
        while True:
            # print(len(self.received), self.header_size)
            if len(self.received) < self.header_size:
                return
            header_pack = struct.unpack("!3I", self.received[:self.header_size])
            # print("header_pack:", header_pack)
            body_size = header_pack[1]
            if header_pack[0] + header_pack[2] != 102:
                return
            # print(body_size)
            # package split situation
            if len(self.received) < self.header_size + body_size:
                return
            body = self.received[self.header_size:self.header_size+body_size]
            tcp_logger.info("receive %d bytes message from %s", body_size, self.get_peername())
            tcp_logger.debug(">>>> %s <<<<", body)
            from gateway import gateway_singleton
            result = gateway_singleton.handle_node_request(self, body)
            # package splicing or clan the data_buffer:self.received
            self.received = self.received[self.header_size+body_size:]
            # print(self.received)
            
            

    def connection_lost(self, exc):
        peername = self.transport.get_extra_info('peername')
        if exc:
            tcp_manager.exc_close_times += 1
            self.state = "exc_closed"
            tcp_logger.info("the connection %s was broken", peername)
        else:
            tcp_manager.close_times += 1
            self.state = "closed"
            tcp_logger.info("the connection %s was closed", peername)
        from gateway import gateway_singleton
        from utils import del_dict_item_by_value
        if self.is_wallet_cli and not exc:
            gateway_singleton.handle_wallet_cli_off_line(self)
        if self in list(gateway_singleton.tcp_pk_dict.values()) and not exc:
            gateway_singleton.handle_node_off(peername)
        tcp_manager.unregister(self)
        self.transport.close()
        del_dict_item_by_value(gateway_singleton.tcp_pk_dict, self)
        del self


    def pause_writing(self):
        print(self.transport.get_write_buffer_size())
        self.state = "paused"

    def resume_writing(self):
        print(self.transport.get_write_buffer_size())
        self.state = "resumed"

    def get_peername(self):
        return self.transport.get_extra_info("peername")

class TcpService:
    """
    tcpservice class
    """
    @staticmethod
    def find_connection(url):
        """
        has connected the host of the addr
        then communicate with the exist connection
        or create a new connection
        """
        from gateway import gateway_singleton
        from utils import get_public_key
        pk = get_public_key(url)
        exist_protocol = gateway_singleton.tcp_pk_dict.get(pk)
        if exist_protocol and exist_protocol.state == "connected":
            return exist_protocol.transport
        # disconnected
        else:
            return None

    @staticmethod
    async def send_tcp_msg_coro(url, bdata):
        """
        :param bdata: bytes type
        """
        from gateway import gateway_singleton
        from utils import get_addr, get_public_key
        addr = get_addr(url)
        pk = get_public_key(url)
        result = await get_event_loop().create_connection(TProtocol, addr[0], addr[1])
        tcp_logger.info('Result of creating connection<{}> is {}'.format(addr, result))
        gateway_singleton.tcp_pk_dict[pk] = result[1]
        result[0].write(bdata)
        result[1].send_totals += len(bdata)
        import pprint
        pprint.pprint(gateway_singleton.tcp_pk_dict)
        
    @staticmethod
    async def create_server_coro(addr):
        """
        the coro for create tcp server\n
        return an instance of ProtocolManage 
        """
        loop = get_event_loop()
        server = await loop.create_server(TProtocol, addr[0], addr[1])
        tcp_manager.wrap(server)
        tcp_logger.info("TCP server is serving on %s", addr)
        return tcp_manager
