# coding: utf-8
import pprint
from tcpservice import TcpService
from wsocket import WsocketService
from asyncio import get_event_loop, gather, Task, sleep, ensure_future
from config import cg_tcp_addr, cg_wsocket_addr

class Gateway():
    """
    gateway 类 定义了所有直接相关的行为与属性
    """
    def __init__(self):
        """Counstruct"""
        self.websocket = None
        self.tcpserver = None
        self.loop = None
        self.clients = set()

    def _create_service_coros(self):
        """
        创建tcp wsocket service coros\n
        它们进入event_loop执行后最终返回tcp、wsocket server
        """
        return TcpService.create(cg_tcp_addr), WsocketService.create(cg_wsocket_addr)

    def _save(self, services, loop):
        """
        保存servers、event loop
        """
        self.tcpserver, self.websocket = services
        self.loop = loop

    # def create_client(self):
    #     """创建网关client 多个实例"""
    #     client = Client()
    #     self.clients.add(client)
    #     return client
    
    def start(self):
        """ 启动gateway"""
        services_future = gather(*self._create_service_coros())
        loop = get_event_loop()
        loop.run_until_complete(services_future)
        self._save(services_future.result(), loop)
        # pp = pprint.PrettyPrinter(indent=4)
        # pp.pprint(self.tcpserver)
        # pp.pprint(self.websocket)
        print("Gateway tcp service on: {}".format(cg_tcp_addr))
        print("Gateway websocket service on: {}".format(cg_wsocket_addr))
        
        loop.run_forever()

    def clearn(self):
        """
        清理任务
        """
        # print(self.websocket.server)
        self.websocket.close()
        self.loop.run_until_complete(self.websocket.wait_closed())
        for task in Task.all_tasks():
            print(task)
            cancel_result = task.cancel()
            print(cancel_result)
        ensure_future(self._stop())
        self.loop.run_forever()

    def close(self):
        self.loop.close()
        print("gateway closed")

    async def _stop(self):
        """
        延迟stop loop\n
        避免CancelledError exception
        """
        await sleep(0.25)
        self.loop.stop()

    def handle_tcp_request(self, protocol, bdata):
        """
        处理tcp请求
        """
        pass

    def handle_wsocket_request(self, websocket, strdata):
        """
        处理websocket请求
        """
        pass
    
    def _add_push_web_task(self):
        """
        添加web推送任务到event loop
        """
        ensure_future(WsocketService.push(self.websocket.websockets))

    
gateway_singleton = Gateway()