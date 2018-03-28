# coding: utf-8
import pprint
import json
import utils
from routertree import RouteTree
from tcpservice import TcpService
from wsocket import WsocketService
from jsonrpc import AsyncJsonRpc
from asyclient import send_tcp_msg
from asyncio import get_event_loop, gather, Task, sleep, ensure_future, iscoroutine
from config import cg_tcp_addr, cg_wsocket_addr

route_tree = RouteTree()
route_tree.create_node("Daviv", "daviv")  # root node
web_list = set()
# route_tree.create_node("Jane", "jane", parent="harry")
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
        self._add_timer_push_web_task()
        print("Gateway tcp service on: {}".format(cg_tcp_addr))
        print("Gateway websocket service on: {}".format(cg_wsocket_addr))
        AsyncJsonRpc.start_jsonrpc_serv()
        # loop.run_forever()

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
        # test sync router tree
        tr_dic = utils.decode_bytes(bdata)
        peer_tree = RouteTree.to_tree(json.dumps(tr_dic))
        print("本地节点同步前树形结构")
        route_tree.show()
        print("peer 同步前的树形结构")
        peer_tree.show()
        new_peer_tree = route_tree.sync_tree(peer_tree)
        print("本地节点同步后树形结构")
        route_tree.show()
        print("peer 同步后的树形结构")
        new_peer_tree.show()
        print(new_peer_tree.all_nodes())
        # print(peer_tree.show())

    def handle_wsocket_request(self, websocket, strdata):
        """
        处理websocket请求
        
        """
        print(strdata)
        # try:
        #     data = json.loads(strdata)
        #     request_type = data["type"]
        # except:
        #     pass
        # if request_type == "join":
        #     res = {
        #         "type": "join_ack",
        #         "body": {
        #             "content": "weclome"
        #         }
        #     }
        # elif request_type == "build_channel":
        #     res = {
        #         "type": "founder",
        #         "body": {
        #             "signature": "signature mock",
        #             "data": {}
        #         }
        #     }
        # elif request_type == "founder_ack":
        #     res = {
        #         "type": "channel_result",
        #         "body": {
        #             "result": "successful"
        #         }
        #     }
        # self._send_wsocket_msg(websocket, res)

    def _send_wsocket_msg(self, con, msg):
        ensure_future(WsocketService.send_msg(con, msg))

    def _send_jsonrpc_msg(self, method, msg):
        ensure_future(AsyncJsonRpc.jsonrpc_request(get_event_loop(), method, msg))

    def _send_tcp_msg(self, addr, msg):
        ensure_future(send_tcp_msg(addr, msg))

    def handle_wsocket_disconnection(self, websocket):
        self._add_event_push_web_task()

    def handle_jsonrpc_response(self, response):
        print(response)

    def handle_jsonrpc_request(self, method, msg):
        return "pong"

    def _add_event_push_web_task(self):
        ensure_future(WsocketService.push_by_event(self.websocket.websockets))

    def _add_timer_push_web_task(self):
        ensure_future(WsocketService.push_by_timer(self.websocket.websockets, 15))
    
    
gateway_singleton = Gateway()