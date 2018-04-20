# coding: utf-8
import websockets
import json
import random
from asyncio import sleep
from glog import wst_logger
class WsocketService:
    """
    websocket server
    not need instance
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
        the callback that receive the client msg
        """
        # every client first connected the server
        from gateway import gateway_singleton
        wst_logger.info('client {} connected'.format(con.remote_address))
        gateway_singleton.handle_web_first_connect(con)
        while True:
            try:
                message = await con.recv()
                wst_logger.debug(">>>> %s <<<<", message)
            except Exception:
                wst_logger.info('client {} disconnected'.format(con.remote_address))
                gateway_singleton.handle_wsocket_disconnection(con)
                # task done
                break
            else:
                try:
                    gateway_singleton.handle_wsocket_request(con, message)
                except Exception:
                    pass
                    

    @staticmethod
    async def send_msg(con, msg):
        try:
            await con.send(msg)
        except Exception:
            pass

    @staticmethod
    async def create(addr):
        """
        :return await object
        """
        ws = await websockets.serve(WsocketService.handle, addr[0], addr[1])
        wst_logger.info("websocket server is serving on %s", addr)
        return ws