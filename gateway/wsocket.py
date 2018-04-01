# coding: utf-8
import websockets
import json
import random
from asyncio import sleep

class WsocketService:
    """
    websocket 服务
    不可实例化
    """
    @staticmethod
    async def push_by_event(cons, msg):
        """
        push spv triggered by some event
        """
        for con in cons:
            try:
                await con.send(json.dumps(msg))
            except Exception:
                pass
    
    @staticmethod 
    async def push_by_timer(cons, second, msg):
        while True:
            await sleep(second)
            for con in cons:
                try:
                    await con.send(json.dumps(msg))
                except Exception:
                    pass
            

    @staticmethod
    async def handle(con, path):
        """
        处理所有来自客户端的websocket请求
        """
        # every client first connected the server
        from gateway import gateway_singleton
        print('client {} conected'.format(con.remote_address))
        gateway_singleton.handle_web_first_connect(con)
        while True:
            try:
                message = await con.recv()
                gateway_singleton.handle_wsocket_request(con, message)
            except websockets.exceptions.ConnectionClosed:
                print('client {} disconected'.format(con.remote_address))
                gateway_singleton.handle_wsocket_disconnection(con)
                break

    @staticmethod
    async def send_msg(con, msg):
        try:
            await con.send(msg)
        except websockets.exceptions.ConnectionClosed:
            pass

    @staticmethod
    def create(addr):
        """
        返回一个await object
        """
        return websockets.serve(WsocketService.handle, addr[0], addr[1])