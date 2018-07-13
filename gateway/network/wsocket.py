# coding: utf-8
import websockets
from asyncio import sleep,CancelledError
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
                await con.send(msg)
            except Exception:
                pass
    
    @staticmethod 
    async def push_by_timer(cons, second, msg):
        while True:
            await sleep(second)
            for con in cons:
                try:
                    await con.send(msg)
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
        gateway_singleton.handle_spv_make_connection(con)
        while True:
            try:
                message = await con.recv()
                wst_logger.debug("receive: %s", message)
            except websockets.exceptions.ConnectionClosed as ex:
                wst_logger.info('client {} disconnected'.format(con.remote_address))
                gateway_singleton.handle_spv_lost_connection(con)
                # task done or cancelled
                break
            # except Exception:
            #     pass
            else: 
                try:
                    gateway_singleton.handle_spv_request(con, message)
                except Exception as e:
                    wst_logger.exception("handle spv msg exception")

    @staticmethod
    async def send_msg(con, msg):
        try:
            await con.send(msg)
        except Exception:
            pass

    @staticmethod
    async def create_server_coro(addr):
        """
        the coro for create websocket server\n
        return an instance of WebSocketServer 
        """
        ws_server = await websockets.serve(WsocketService.handle, addr[0], addr[1])
        wst_logger.info("WST server is serving on %s", addr)
        return ws_server