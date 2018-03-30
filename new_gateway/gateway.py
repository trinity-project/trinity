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
# route_tree.create_node(pk, ipport, data)  # root node
# tree.create_node("Jane", "jane", parent="daviv")
node_list = set()
# get from wallet
# local_url = "xxxxxxxxxxxx@0.0.0.0:8000"
# wallet_info = {
#     "fee": 3,
#     "url": "xxxxxxxxxxxx@0.0.0.0:8000"
# }
route = {
    "FullPath": ["A", "B", "C"],
    "NextJump": "B"
}
node = {
    "wallet_info": None,
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
        # self._add_timer_push_web_task()
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
            receiver_pk, receiver_ip_port = utils.parse_url(data["Receiver"])
            self_pk, self_ip_port = utils.parse_url(node["wallet_info"]["url"])
            # include router info situation
            if data.get("RouterInfo"):
                router = data["RouterInfo"]
                full_path = router["FullPath"]
                next_jump = router["Next"]
                # valid msg
                if next_jump == node["wallet_info"]["url"]:
                    # arrive end
                    if full_path(len(full_path)-1)[0] == next_jump:
                        # spv---node---spv siuation
                        if len(full_path) == 1:
                            # right active
                            message = utils.generate_trigger_transaction_msg(
                                node["wallet_info"]["url"],
                                data["Receiver"],
                                data["MessageBody"]["Value"] - node["wallet_info"]["Fee"]
                            )
                            pk = utils.parse_url(data["Receiver"])[0]
                            self._send_wsocket_msg(self.ws_pk_dict[pk], json.dumps(message))
                            # left active
                            message = utils.generate_trigger_transaction_msg(
                                data["Sender"],
                                node["wallet_info"]["url"],
                                data["MessageBody"]["Value"] - node["wallet_info"]["Fee"]
                            )
                            self._send_jsonrpc_msg("TransactionMessage", json.dumps(message))
                        # xx--node--node--..--xx siuation
                        else:
                            # to self's spv
                            if receiver_pk != self_pk:
                                message = utils.generate_trigger_transaction_msg(
                                    node["wallet_info"]["url"],
                                    data["Receiver"],
                                    data["MessageBody"]["Value"] - node["wallet_info"]["Fee"]
                                )
                                pk = utils.parse_url(data["Receiver"])[0]
                                self._send_wsocket_msg(self.ws_pk_dict[pk], json.dumps(message))
                            # to self's wallet 
                            # previs hased send the transactions to this node
                            # do nothing to the origin mesg
                            else:
                                pass
                    # go on pass msg
                    else:
                        new_next_jump = full_path(full_path.index((next_jump, node["wallet_info"]["fee"])) + 1)[0]
                        data["RouterInfo"]["Next"] = new_next_jump
                        # node1--node2--xxx this for node1 siuation
                        if data["Sender"] == node["wallet_info"]["url"]:
                            message = utils.generate_trigger_transaction_msg(
                                node["wallet_info"]["url"], # self
                                new_next_jump,
                                data["MessageBody"]["Value"]
                            )
                            self._send_jsonrpc_msg("TransactionMessage", json.dumps(message))
                        # pxxx---node----exxx for node
                        else:
                            # pxxx is spv
                            if utils.parse_url(data["Sender"])[1] == self_ip_port:
                                # left active
                                left_message = utils.generate_trigger_transaction_msg(
                                    data["Sender"],
                                    node["wallet_info"]["url"],
                                    data["MessageBody"]["Value"] - node["wallet_info"]["Fee"]
                                )
                                # right active
                                right_message = utils.generate_trigger_transaction_msg(
                                    node["wallet_info"]["url"], # self
                                    new_next_jump,
                                    data["MessageBody"]["Value"] - node["wallet_info"]["fee"]
                                )
                                self._send_jsonrpc_msg("TransactionMessage", json.dumps(left_message))
                                self._send_jsonrpc_msg("TransactionMessage", json.dumps(right_message))
                            # pxxx is node
                            else:
                                message = utils.generate_trigger_transaction_msg(
                                    node["wallet_info"]["url"], # self
                                    new_next_jump,
                                    data["MessageBody"]["Value"] - node["wallet_info"]["fee"]
                                )
                                self._send_jsonrpc_msg("TransactionMessage", json.dumps(message))
                        pk = utils.parse_url(new_next_jump)[0]
                        self.tcp_pk_dict.get(pk).send(utils.encode_bytes(data))
                # invalid msg
                else:
                    pass
            # no router info situation
            # send the msg to receiver directly
            else:
                if receiver_ip_port == self_ip_port:
                    # to self's spv
                    if receiver_pk != self_pk:
                        self._send_wsocket_msg(self.ws_pk_dict[receiver_pk], json.dumps(data))
                    # to self's wallet
                    else:
                        self._send_jsonrpc_msg("TransactionMessage", json.loads(data))
                
                # to self's peer
                else:
                    self.tcp_pk_dict[receiver_pk].send(utils.encode_bytes(data))

        elif msg_type == "SyncChannelState":
            pass
            # peer_tree =  RouteTree.to_tree(json.dumps(data))
            # first change self tree and sync to self's neighbors
            # route_tree.sync_tree(peer_tree)
        
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
        self._add_event_push_web_task()
        # data = utils.json_to_dict(strdata)
        data = {}
        msg_type = data.get("MessageType")
        # build map bettween spv pk_key with websocket connection
        if msg_type == "AddChannel":
            spv_pk = utils.get_public_key(data["Sender"])
            self.ws_pk_dict[spv_pk] = websocket
        elif msg_type == "CombinationTransaction":
            pass
        elif msg_type == "GetRouterInfo":
            receiver_pk, receiver_ip_port = utils.parse_url(data.get("Receiver"))
            slef_pk, self_ip_port = utils.parse_url(node["wallet_info"]["url"])
            # spv transaction to another spv on the same node
            if receiver_ip_port == self_ip_port and receiver_pk != slef_pk:
                router = {
                    "FullPath": [(node["wallet_info"]["url"], node["wallet_info"]["fee"])],
                    "Next": node["wallet_info"]["url"]
                }
            else:
                nids = node["route_tree"].find_router(receiver_ip_port)
                # next_jump = nids.index()
                full_path = []
                for nid in nids:
                    node_object = node["route_tree"].get_node(nid)
                    url = node_object.tag + node_object.identifier
                    fee = node_object.data["fee"]
                    full_path.append((url, fee))
                if not len(full_path):
                    router = None
                else:
                    next_jump = full_path[0][0]
                    router = {
                        "FullPath": full_path,
                        "Next": next_jump
                    }
            message = json.dumps(utils.generate_ack_router_info_msg(router))
            self._send_wsocket_msg(websocket, message)
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
            node["wallet_info"]["url"] = node["wallet_info"]["PublicKey"]
            return json.dumps(utils.generate_ack_sync_wallet_msg)
        # search chanenl router return the path
        elif method == "GetRouterInfo":
            receiver = data.get("Receiver")
            receiver_ip_port = utils.parse_url(receiver)[1]
            # search tree through ip_port(node identifier in the tree)
            nids = node["route_tree"].find_router(receiver_ip_port)
            # next_jump = nids.index()
            full_path = []
            for nid in nids:
                node_object = node["route_tree"].get_node(nid)
                url = node_object.tag + node_object.identifier
                fee = node_object.data["fee"]
                full_path.append((url, fee))
            next_jump = full_path[0][0]

            if not len(full_path):
                return json.dumps(utils.generate_ack_router_info_msg(None))
            else:
                router = {
                    "FullPath": full_path,
                    "Next": next_jump
                }
                return json.dumps(utils.generate_ack_router_info_msg(router))


    def _add_event_push_web_task(self):
        utils.mock_node_list_data(route_tree)
        message = {
            "MessageType": "RouterInfo",
            "RouterInfo": route_tree.to_json(with_data=True)
        }
        print(message)
        ensure_future(WsocketService.push_by_event(self.websocket.websockets, message))

    def _add_timer_push_web_task(self):
        ensure_future(WsocketService.push_by_timer(self.websocket.websockets, 15))
    
    def sync_channel_route_to_peer(self):
        self_tree = node["route_tree"]
        for child in self_tree.is_branch(self_tree.root):
            node_object = self_tree.get_node(child)
            pk = node_object.tag
            self.tcp_pk_dict.get(pk).send(utils.encode_bytes(self_tree.to_json()))


    def handle_transaction_message(self, data):
        receiver_pk, receiver_ip_port = utils.parse_url(data["Receiver"])
        self_pk, self_ip_port = utils.parse_url(node["wallet_info"]["url"])
        # include router info situation
        if data.get("RouterInfo"):
            router = data["RouterInfo"]
            full_path = router["FullPath"]
            next_jump = router["Next"]
            # valid msg
            if next_jump == node["wallet_info"]["url"]:
                # arrive end
                if full_path(len(full_path)-1)[0] == next_jump:
                    # spv---node---spv siuation
                    if len(full_path) == 1:
                        # right active
                        message = utils.generate_trigger_transaction_msg(
                            node["wallet_info"]["url"],
                            data["Receiver"],
                            data["MessageBody"]["Value"] - node["wallet_info"]["Fee"]
                        )
                        pk = utils.parse_url(data["Receiver"])[0]
                        self._send_wsocket_msg(self.ws_pk_dict[pk], json.dumps(message))
                        # left active
                        message = utils.generate_trigger_transaction_msg(
                            data["Sender"],
                            node["wallet_info"]["url"],
                            data["MessageBody"]["Value"] - node["wallet_info"]["Fee"]
                        )
                        self._send_jsonrpc_msg("TransactionMessage", json.dumps(message))
                    # xx--node--node--..--xx siuation
                    else:
                        # to self's spv
                        if receiver_pk != self_pk:
                            message = utils.generate_trigger_transaction_msg(
                                node["wallet_info"]["url"],
                                data["Receiver"],
                                data["MessageBody"]["Value"] - node["wallet_info"]["Fee"]
                            )
                            pk = utils.parse_url(data["Receiver"])[0]
                            self._send_wsocket_msg(self.ws_pk_dict[pk], json.dumps(message))
                        # to self's wallet 
                        # previs hased send the transactions to this node
                        # do nothing to the origin mesg
                        else:
                            pass
                # go on pass msg
                else:
                    new_next_jump = full_path(full_path.index((next_jump, node["wallet_info"]["fee"])) + 1)[0]
                    data["RouterInfo"]["Next"] = new_next_jump
                    # node1--node2--xxx this for node1 siuation
                    if data["Sender"] == node["wallet_info"]["url"]:
                        message = utils.generate_trigger_transaction_msg(
                            node["wallet_info"]["url"], # self
                            new_next_jump,
                            data["MessageBody"]["Value"]
                        )
                        self._send_jsonrpc_msg("TransactionMessage", json.dumps(message))
                    # pxxx---node----exxx for node
                    else:
                        # pxxx is spv
                        if utils.parse_url(data["Sender"])[1] == self_ip_port:
                            # left active
                            left_message = utils.generate_trigger_transaction_msg(
                                data["Sender"],
                                node["wallet_info"]["url"],
                                data["MessageBody"]["Value"] - node["wallet_info"]["Fee"]
                            )
                            # right active
                            right_message = utils.generate_trigger_transaction_msg(
                                node["wallet_info"]["url"], # self
                                new_next_jump,
                                data["MessageBody"]["Value"] - node["wallet_info"]["fee"]
                            )
                            self._send_jsonrpc_msg("TransactionMessage", json.dumps(left_message))
                            self._send_jsonrpc_msg("TransactionMessage", json.dumps(right_message))
                        # pxxx is node
                        else:
                            message = utils.generate_trigger_transaction_msg(
                                node["wallet_info"]["url"], # self
                                new_next_jump,
                                data["MessageBody"]["Value"] - node["wallet_info"]["fee"]
                            )
                            self._send_jsonrpc_msg("TransactionMessage", json.dumps(message))
                    pk = utils.parse_url(new_next_jump)[0]
                    self.tcp_pk_dict.get(pk).send(utils.encode_bytes(data))
            # invalid msg
            else:
                pass
        # no router info situation
        # send the msg to receiver directly
        else:
            if receiver_ip_port == self_ip_port:
                # to self's spv
                if receiver_pk != self_pk:
                    self._send_wsocket_msg(self.ws_pk_dict[receiver_pk], json.dumps(data))
                # to self's wallet
                else:
                    self._send_jsonrpc_msg("TransactionMessage", json.loads(data))
            # to self's peer
            else:
                self.tcp_pk_dict[receiver_pk].send(utils.encode_bytes(data))

gateway_singleton = Gateway()

if __name__ == "__main__":
    from routertree import SPVHashTable
    spv_table = SPVHashTable()
    utils.mock_node_list_data(route_tree, spv_table)
    print(route_tree.nodes)