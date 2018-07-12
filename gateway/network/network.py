# coding: utf-8
"""
the module gather all protocols for trinity network communication  
"""
import asyncio
import uvloop
import json
from .tcp import TcpService
from .jsonrpc import AsyncJsonRpc
from .wsocket import WsocketService
from config import cg_tcp_addr, cg_wsocket_addr, cg_public_ip_port, cg_local_jsonrpc_addr,\
cg_remote_jsonrpc_addr, cg_reused_tcp_connection
from asyncio import ensure_future
from utils import encode_bytes
from glog import tcp_logger, wst_logger
import time

class Network:
    """
    network class \n
    class attribute: rpc_server/tcp_manager/ws_server
    """
    # class methods
    @classmethod
    def create_servers(cls):
        loop = uvloop.new_event_loop()
        asyncio.set_event_loop(loop)
        create_server_coros = [
            AsyncJsonRpc.create_server_coro(cg_local_jsonrpc_addr),
            TcpService.create_server_coro(cg_tcp_addr),
            WsocketService.create_server_coro(cg_wsocket_addr)
        ]
        tasks = asyncio.gather(*create_server_coros)
        loop.run_until_complete(tasks)
        cls.loop = loop
        cls.rpc_server, cls.tcp_manager, cls.ws_server = tasks.result()
        
    @classmethod
    def run_servers_forever(cls):
        cls.loop.run_forever()

    @classmethod
    def clearn_servers(cls):
        cls.ws_server.close()
        cls.tcp_manager.server.close()
        cls.rpc_server.close()
        tasks = asyncio.gather(*asyncio.Task.all_tasks(), loop=cls.loop, return_exceptions=True)
        tasks.add_done_callback(lambda t: cls.loop.stop())
        tasks.cancel()
        while not tasks.done() and not cls.loop.is_closed():
            cls.loop.run_forever()

    @classmethod
    def add_event_push_web_task(cls, data):
        """
        :param message: dict type \n
        :param interval: default 15s
        """
        data = json.dumps(data)
        future = ensure_future(WsocketService.push_by_event(cls.ws_server.websockets, data))
        future.add_done_callback(lambda t: t.exception())

    @classmethod
    def add_timer_push_web_task(cls, data, interval=15):
        """
        :param message: dict type \n
        :param interval: default 15s
        """
        data = json.dumps(data)
        future = ensure_future(WsocketService.push_by_timer(cls.ws_server.websockets, interval, data))
        future.add_done_callback(lambda t: t.exception())

    # static method
    @staticmethod
    def send_msg_with_tcp(receiver, data):
        """
        :param receiver: str type: xxxx@ip:port \n
        :param data: dict type
        """
        # time.sleep(0.05)
        bdata = encode_bytes(data)
        connection = TcpService.find_connection(receiver)
        if connection and cg_reused_tcp_connection:
            tcp_logger.info("find the exist connection")
            connection.write(bdata)
        else:
            future = asyncio.ensure_future(TcpService.send_tcp_msg_coro(receiver, bdata))
            future.add_done_callback(lambda t: t.exception())
    
    @staticmethod
    def send_msg_with_wsocket(connection, data):
        """
        :param connection: wsocket connection\n
        :param data: dict type
        """
        if connection:
            data = json.dumps(data)
            future = asyncio.ensure_future(WsocketService.send_msg(connection, data))
            future.add_done_callback(lambda t: t.exception())
        else:
            wst_logger.info("the spv is disconnected")

    @staticmethod
    def send_msg_with_jsonrpc(method, addr, data, loop=None, callback=None):
        """
        :param method: the method that request to the remote server\n
        :param addr: wallet rpc server addr type\n
        :param data: dict type\n
        :param data: asyncio event loop
        """
        data = json.dumps(data)
        future = asyncio.ensure_future(
            AsyncJsonRpc.jsonrpc_request(method, data, addr)
        )
        if callback:
            import functools
            wrapped = functools.partial(callback, addr=addr)
            future.add_done_callback(wrapped)
        else:
            future.add_done_callback(lambda t: t.exception())

    @staticmethod
    def send_msg_with_jsonrpc_sync(method, addr, data):
        data = json.dumps(data)
        res = AsyncJsonRpc.jsonrpc_request_sync(method, data, addr)
        return json.loads(res) if res else res
  