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


def find_connection(url):
    """
    has connected the host of the addr
    then communicate with the exist connection
    or create a new connection
    """
    from gateway import gateway_singleton
    from utils import get_public_key
    pk = get_public_key(url)
    exist_transport = gateway_singleton.tcp_pk_dict[pk]
    if exist_transport in (gateway_singleton.tcpserver.transports | gateway_singleton.client.transports):
        return exist_transport
    # disconnected
    else:
        return None

async def send_tcp_msg_coro(url, bdata):
    """
    :param bdata: bytes type
    """
    from gateway import gateway_singleton
    from utils import get_addr, get_public_key
    addr = get_addr(url)
    pk = get_public_key(url)
    con = await get_event_loop().create_connection(ClientProtocol, addr[0], addr[1])
    gateway_singleton.tcp_pk_dict[pk] = con
    con.send(bdata)

