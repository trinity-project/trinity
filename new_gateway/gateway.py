# coding: utf-8
import pprint
import json
import utils
from routertree import RouteTree, parse_uri
from tcpservice import TcpService
from wsocket import WsocketService
from jsonrpc import AsyncJsonRpc
from asyclient import send_tcp_msg
from asyncio import get_event_loop, gather, Task, sleep, ensure_future, iscoroutine
from config import cg_tcp_addr, cg_wsocket_addr

route_tree = RouteTree()
route_tree.create_node("Daviv", "Daviv")  # root node
# tree.create_node("Jane", "jane", parent="daviv")
node_list = set()
# get from wallet
local_url = "xxxxxxxxxxxx@0.0.0.0:8000"
wallet_info = {
    "fee": 3,
    "url": "xxxxxxxxxxxx@0.0.0.0:8000"
}
route = {
    "FullPath": ["A", "B", "C"],
    "NextJump": "B"
}
node = {
    "wallet_info": None
    "route_tree": None,
    "spv_table": None
}
# websocket(connection) and spv url dictionary key: public key,value: websocket
# ws_pk_dict = {

# }
# tcp transport(connection) and node url dictionary key: public key,value: transport
# tcp_pk_dict = {
    
# }
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
        self.tcp_pk_dict = {}
        self.ws_pk_dict = {}
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

    def handle_tcp_request(self, transport, bdata):
        data = utils.decode_bytes(bdata)
        sender = "xxxxxxxxxxxxxxx@localhost:8088"
        msg_type = data.get("MessageType")
        if msg_type == "JoinNet":
            # join net sync node_list
            transport.send(
                utils.generate_ack_node_join_msg(
                    sender, data["Receiver"], node_list
                    )
            )
            node_list.add(data["sender"])
        elif msg_type == "AckJoin":
            node_list.add(data["Receiver"])
            node_list = node_list | data["NodeList"]
        elif msg_type == "AddChannel":
            # basic check
            # request wallet to handle 
            if not utils.check_wallet_url_correct(data["Receiver"], local_url):
                # not self's wallet address
                transport.send(utils.generate_error_msg(local_url, data["Sender"], "Invalid wallet address"))
            else:
                self._send_jsonrpc_msg("CreateChannle", json.dumps(data))
        elif  msg_type == "AckAddChannel":
            # build map with peeer node public key and current transport
            peer_pk = utils.get_public_key(data["Sender"])
            self.tcp_pk_dict[peer_pk] = transport

        elif msg_type == "TransactionMessage":
            # request wallet to handle 
            # recevier url publikey check
            # router info check
            # router select
            receiver_ip_port = data["Receiver"].split("@")[1]
            receiver_pk = data["Receiver"].split("@")[0]
            self_ip_port = node["wallet_info"]["url"].split("@")[1]
            self_pk = node["wallet_info"]["url"].split("@")[0]
            # 交易对象可能是自己或者是挂在自己的spv
            if receiver_ip_port == self_ip_port:
                #交易对象是自己 无手续费 直接扔给wallet处理
                if receiver_pk == self_pk:
                    self._send_jsonrpc_msg("TransactionMessage", json.dumps(data))
                #交易对象不是自己 极有可能是挂在自己上面的spv 需要手续费 需要check自己的散列表 验证是spv的身份
                else:
                    # 交易对象是挂在自己上面的spv
                    if receiver_pk in node["spv_table"].find(self_pk):
                        pass
                    # spv验证失败 可能已掉线或者有人冒充
                    else:
                        pass
             # 交易对象是其他节点或挂在其他节点上的spv 需要手续费
            else:
                # 消息已经包含路由信息的情况
                if data.get("RouterInfo"):
                    router = data["RouterInfo"]
                    full_path = router["FullPath"]
                    next_jump = router["Next"]
                    # 交易信息是传给自己的
                    if next_jump == self_ip_port:
                        # 到达终点
                        if full_path(len(full_path)-1) == next_jump:
                            # todo spv or itself
                            self._send_jsonrpc_msg("TransactionMessage", json.dumps(data))
                        # 继续传递信息
                        else:
                            new_next_jump = full_path(full_path.index(next_jump) + 1)
                            data["RouterInfo"]["Next"] = new_next_jump
                            self.tcp_ip_port_dict.get(route["Next"]).send(utils.encode_bytes(data))
                            message = utils.generate_trigger_transaction_msg(
                                node["wallet_info"]["url"], # self
                                new_next_jump,
                                data["MessageBody"]["Value"] - node["wallet_info"]["Fee"]
                            )
                            self._send_jsonrpc_msg("TransactionMessage", json.dumps(message))
                    # 交易信息传错了 暂时作丢弃处理
                    else:
                        pass
                # 消息不包含路由的信息的情况
                else:
                    receiver = data["Receiver"]
                    full_path = node["route_tree"].find_router(receiver)
                    # 没有找到通道路由
                    if not len(full_path):
                        print("not found path to the distination")
                        return
                    # 找到路由
                    else:
                        next_index = full_path.index(self_ip_port) + 1
                        next_jump = full_path[next_index]
                        router = {
                            "FullPath": full_path,
                            "Next": next_jump
                        }
                        data["RouterInfo"] = router
                        self.tcp_ip_port_dict.get(route["Next"]).send(utils.encode_bytes(data))
                        message = utils.generate_trigger_transaction_msg(
                            data["Sender"],
                            route["Next"],
                            data["MessageBody"]["Value"] - node["wallet_info"]["Fee"]
                        )
                        self._send_jsonrpc_msg("TransactionMessage", json.dumps(message))

        elif msg_type == "SyncChannelState":
            peer_tree =  RouteTree.to_tree(json.dumps(data))
            # first change self tree and sync to self's neighbors
            route_tree.sync_tree(peer_tree)
        
        # test sync router tree
        # tr_dic = utils.decode_bytes(bdata)
        # peer_tree = RouteTree.to_tree(json.dumps(tr_dic))
        # print("本地节点同步前树形结构")
        # route_tree.show()
        # print("peer 同步前的树形结构")
        # peer_tree.show()
        # new_peer_tree = route_tree.sync_tree(peer_tree)
        # print("本地节点同步后树形结构")
        # route_tree.show()
        # print("peer 同步后的树形结构")
        # new_peer_tree.show()
        # print(new_peer_tree.all_nodes())
        # print(peer_tree.show())

    def handle_wsocket_request(self, websocket, strdata):
        """
        处理websocket请求
        """
        data = utils.json_to_dict(strdata)
        msg_type = data.get("MessageType")
        # build map bettween spv pk_key with websocket connection
        if msg_type == "AddChannel":
            spv_pk = utils.get_public_key(data["Sender"])
            self.ws_pk_dict[spv_pk] = websocket
        elif msg_type == "CombinationTransaction":
            pass
        print(strdata)

    def _send_wsocket_msg(self, con, msg):
        ensure_future(WsocketService.send_msg(con, msg))

    def _send_jsonrpc_msg(self, method, msg):
        ensure_future(AsyncJsonRpc.jsonrpc_request(get_event_loop(), method, msg))

    def _send_tcp_msg(self, addr, msg):
        ensure_future(send_tcp_msg(addr, msg))

    def handle_wsocket_disconnection(self, websocket):
        self._add_event_push_web_task()

    def handle_jsonrpc_response(self, method, response):

        print(response)

    def handle_jsonrpc_request(self, method, params):
        data = json.loads(params)
        if method == "ShowNodeList":
            return utils.generate_ack_show_node_list(node_list)
        if method == "JoinNet":
            if data.get("ip"):
                addr = (data.get("ip"), data.get("port"))
                self._send_tcp_msg(utils.generate_join_net_msg())
            else:
                pass
            return "{'JoinNet': 'OK'}"
        elif method == "SyncWalletData":
            data = json.loads(params)
            node["wallet_info"] = dat["MessageBody"]
            node["waleet_info"]["url"] = node["waleet_info"]["PublicKey"]
            return json.dumps(utils.generate_ack_sync_wallet_msg)
        elif method == "GetChannelInfo":
            pass

    def _add_event_push_web_task(self):
        ensure_future(WsocketService.push_by_event(self.websocket.websockets))

    def _add_timer_push_web_task(self):
        ensure_future(WsocketService.push_by_timer(self.websocket.websockets, 15))
    
    
gateway_singleton = Gateway()