# coding: utf-8
from asyncio import Protocol, get_event_loop, iscoroutine

class ClientManage():
    def __init__(self):
        self.transports = set()

    def register(self, transport):
        self.transports.add(transport)

    def unregister(self, transport):
        self.transports.remove(transport)

climanage_singleton = ClientManage()

class ClientProtocol(Protocol):
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
        climanage_singleton.register(self._transport)
        peername = transport.get_extra_info('peername')
        print('Connection from {}'.format(peername))

    def data_received(self, data):
        self.received.append(data)
        #检测数据包是否完整 结尾是否包含eof标识
        if b"eof" in data:
            complete_bdata = b"".join(self.received)
            # handle message
            from gateway import gateway_singleton
            gateway_singleton.handle_tcp_request(self._transport, complete_bdata)
        else:
            print("数据还没有接收完毕")

    def connection_lost(self, exc):
        self.state = "closed"
        climanage_singleton.unregister(self._transport)
        self._transport.close()
        print("Connection lost", exc)
        # todo 一些清理的工作
        del self

    def pause_writing(self):
        print(self._transport.get_write_buffer_size())
        self.state = "paused"

    def resume_writing(self):
        print(self._transport.get_write_buffer_size())
        self.state = "resumed"


def create_connection(addr):
    """
    如果server已经与地址为addr的host保持连接\n
    则直接使用server的连接通信\n
    否则创建一个client连接\n
    该函数返回一个server_transport或者一个coro object
    """
    from gateway import gateway_singleton
    find_server_transport = False
    server_transport = None
    for transport in gateway_singleton.tcpserver.transports:
        peername = transport.get_extra_info('peername', default=None)
        peer_host = peername[0] if peername else None
        if addr[0] == peer_host:
            find_server_transport = True
            server_transport = transport
            break
        else:
            continue
    if not find_server_transport:
        loop = get_event_loop()
        return loop.create_connection(ClientProtocol, addr[0], addr[1])
    else:
        return server_transport

async def send_tcp_msg(addr, msg):
    transport = create_connection(addr)
    if iscoroutine(transport):
        con = await result
        con.send(msg)
    else:
        transport.send(msg)

