# coding: utf-8
from asyncio import Protocol, get_event_loop
from config import cg_end_mark, cg_bytes_encoding

class TcpServer():
    def __init__(self):
        self.transports = set()
        self.server = None

    def register(self, transport):
        self.transports.add(transport)

    def unregister(self, transport):
        self.transports.remove(transport)

    def wrap(self, server):
        self.server = server

tcpserver_singleton = TcpServer()

class TcpProtocol(Protocol):
    """
    asyncio.Protocol 继承类 不要手动实例化\n
    每个protocol 匹配一个transport\n
    每个client连接会创建一个新的protocol(同时匹配一个transport)
    """
    def __init__(self):
        super().__init__()
        self._transport = None
        self.received = []
        self.rev_totals = 0
        self.send_totals = 0
        self.state = None
    
    def connection_made(self, transport):
        self.state = "connected"
        self._transport = transport
        tcpserver_singleton.register(self._transport)
        peername = transport.get_extra_info('peername')
        print(type(peername))
        print('Connection from {}'.format(peername))

    def data_received(self, data):
        self.received.append(data)
        last_index = len(cg_end_mark)
        if cg_end_mark.encode(cg_bytes_encoding) == data[-last_index:]:
            complete_bdata = b"".join(self.received)
            print("++++++++",len(complete_bdata),"+++++++")
            from gateway import gateway_singleton
            gateway_singleton.handle_tcp_request(self._transport, complete_bdata)
            self.received = []
        else:
            print("split TCP data")

    def connection_lost(self, exc):
        from gateway import gateway_singleton
        from utils import del_dict_item_by_value
        self.state = "closed"
        tcpserver_singleton.unregister(self._transport)
        self._transport.close()
        print("Connection lost", exc)
        del_dict_item_by_value(gateway_singleton.tcp_pk_dict, self._transport)
        del self

    def pause_writing(self):
        print(self._transport.get_write_buffer_size())
        self.state = "paused"

    def resume_writing(self):
        print(self._transport.get_write_buffer_size())
        self.state = "resumed"

class TcpService():
    """
    tcp 服务抽象
    """
    @staticmethod
    async def create(addr):
        """
        返回一个coro object
        """
        loop = get_event_loop()
        server = await loop.create_server(TcpProtocol, addr[0], addr[1])
        tcpserver_singleton.wrap(server)
        return tcpserver_singleton