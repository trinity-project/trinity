# coding: utf-8
from asyncio import Protocol, get_event_loop
from config import cg_end_mark, cg_bytes_encoding

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

    def register(self, protocol):
        self.protocols.add(protocol)

    def unregister(self, protocol):
        self.protocols.remove(protocol)

    def wrap(self, server):
        self.server = server

tcp_manager = ProtocolManage()

class TProtocol(Protocol):
    """
    asyncio.Protocol 继承类 不要手动实例化\n
    每个protocol 匹配一个transport\n
    每个client连接会创建一个新的protocol(同时匹配一个transport)
    """
    def __init__(self):
        super().__init__()
        self.received = []
        self.rev_totals = 0
        self.send_totals = 0
        self.transport = None
        self.state = None
    
    def connection_made(self, transport):
        self.state = "connected"
        self.transport = transport
        peername = transport.get_extra_info('peername')
        print(type(peername))
        print('connection from {}'.format(peername))
        tcp_manager.register(self)

    def data_received(self, data):
        self.received.append(data)
        last_index = len(cg_end_mark)
        if cg_end_mark.encode(cg_bytes_encoding) == data[-last_index:]:
            complete_bdata = b"".join(self.received)
            print("++++++++",len(complete_bdata),"+++++++")
            from gateway import gateway_singleton
            gateway_singleton.handle_tcp_request(self, complete_bdata)
            self.rev_totals += len(complete_bdata)
            # split data 
            if len(self.received) > 1:
                tcp_manager.rev_data_split_times += 1
                tcp_manager.rev_split_data_totals.append(len(complete_bdata))
            self.received = []
        else:
            print("split TCP data")

    def connection_lost(self, exc):
        if exc:
            tcp_manager.exc_close_times += 1
            self.state = "exc_closed"
        else:
            tcp_manager.close_times += 1
            self.state = "closed"
        from gateway import gateway_singleton
        from utils import del_dict_item_by_value
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
    if exist_protocol and exist_protocol.transport.state == "connected":
        return exist_protocol.transport
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
    result = await get_event_loop().create_connection(ClientProtocol, addr[0], addr[1])
    gateway_singleton.tcp_pk_dict[pk] = result[1]
    result[0].write(bdata)
    result[1].send_totals += len(bdata)

async def create_server_coro(addr):
    """
    return an coro object
    """
    loop = get_event_loop()
    server = await loop.create_server(TcpProtocol, addr[0], addr[1])
    tcp_manager.wrap(server)
    return tcp_manager
    