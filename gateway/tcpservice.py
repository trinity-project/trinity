# coding: utf-8
from asyncio import Protocol, get_event_loop

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
        #检测数据包是否完整 结尾是否包含eof标识
        if b"eof" in data:
            complete_bdata = b"".join(self.received)
            print("------",len(complete_bdata),"-----")
            # handle message
            from gateway import gateway_singleton
            gateway_singleton.handle_tcp_request(self._transport, complete_bdata)
            # self.received = []
        else:
            print("数据还没有接收完毕")
        # from gateway import gateway_singleton
        # gateway_singleton.handle_tcp_request(self._transport, data)

    def connection_lost(self, exc):
        self.state = "closed"
        tcpserver_singleton.unregister(self._transport)
        self._transport.close()
        print("Connection lost", exc)
        # todo 一些清理的工作
        # remove transport from tcp_pk_map
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