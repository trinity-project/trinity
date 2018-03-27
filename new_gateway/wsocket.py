# coding: utf-8
import websockets

class WsocketService:
    """
    websocket 服务
    不可实例化
    """
    @staticmethod
    async def push(cons):
        """
        推送消息到所有客户端
        """
        for con in cons:
            try:
                await con.send("This is a push message triggered by some event")
            except websockets.exceptions.ConnectionClosed:
                pass
            
    @staticmethod
    async def handle(con, path):
        """
        处理所有来自客户端的websocket请求
        """
        while True:
            try:
                print('client {} conected'.format(con.remote_address[1]))
                # todo 数据包完是否整检测
                message = await con.recv()
                from gateway import gateway_singleton
                gateway_singleton.handle_wsocket_request(con, message)
                # await con.send(message)
            except websockets.exceptions.ConnectionClosed:
                print('client {} disconected'.format(con.remote_address[1]))
                break

    @staticmethod
    def create(addr):
        """
        返回一个await object
        """
        return websockets.serve(WsocketService.handle, addr[0], addr[1])