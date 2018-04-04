# coding: utf-8
import pprint
import json
import utils
import time
import datetime
from routertree import RouteTree, SPVHashTable
from tcp import create_server_coro, send_tcp_msg_coro, find_connection
from wsocket import WsocketService
from jsonrpc import AsyncJsonRpc
from asyncio import get_event_loop, gather, Task, sleep, ensure_future, iscoroutine
from config import cg_tcp_addr, cg_wsocket_addr, cg_public_ip_port, cg_node_name
from statistics import Statistics, get_timestamp

# route_tree.create_node('node',cg_public_ip_port, data={Deposit:xx,Fee:xx,Balance:4 IP:xx,Publickey:xx,SpvList:[]})  # root node
node_list = set()
node = {
    "wallet_info": None,
    "route_tree": RouteTree(),
    "spv_table": SPVHashTable(),
    # configurable
    "name": cg_node_name
}
global_statistics = Statistics()
class Gateway():
    """
    gateway 类 定义了所有直接相关的行为与属性
    """
    def __init__(self):
        """Counstruct"""
        self.websocket = None
        self.tcpserver = None
        self.loop = None
        self.tcp_pk_dict = {}
        self.ws_pk_dict = {}
    def _create_service_coros(self):
        """
        创建tcp wsocket service coros\n
        它们进入event_loop执行后最终返回tcp、wsocket server
        """
        return create_server_coro(cg_tcp_addr), WsocketService.create(cg_wsocket_addr)

    def _save(self, services, loop):
        """
        保存servers、event loop
        """
        self.tcpserver, self.websocket = services
        self.loop = loop

    
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
        try:
            data = utils.decode_bytes(bdata)
        except UnicodeDecodeError:
            # global_statistics.stati_tcp.rev_invalid_times += 1
            print("{0}:TCP receive a invalid message: {1}". \
                format(get_timestamp(with_strf=True), bdata[:60]))
            return utils.request_handle_result.get("invalid")
        else:
            if not utils.check_tcp_message_valid(data):
                # global_statistics.stati_tcp.rev_invalid_times += 1
                print("{0}:TCP receive a unknow type message: {1}". \
                    format(get_timestamp(with_strf=True), bdata[:60]))
                return utils.request_handle_result.get("invalid")
            else:
                # first save the node_pk and websocket connection map
                node_pk = utils.get_public_key(data["Sender"])
                self.tcp_pk_dict[node_pk] = transport
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
                elif msg_type == "RegisterChannel":
                    self._send_jsonrpc_msg("TransactionMessage", data)
                elif msg_type == "AddChannel":
                    # basic check
                    # request wallet to handle 
                    if not utils.check_wallet_url_correct(data["Receiver"], local_url):
                        # not self's wallet address
                        transport.send(utils.generate_error_msg(local_url, data["Sender"], "Invalid wallet address"))
                    else:
                        self._send_jsonrpc_msg("CreateChannle", json.dumps(data))
                elif msg_type in ["Rsmc","FounderSign","Founder","RsmcSign","FounderFail"]:
                    self.handle_transaction_message(data)
                elif msg_type == "SyncChannelState":
                    # node receive the syncchannel msg
                    # first update self tree
                    # then sync to self's peers except the peer which send the syncchannel msg
                    data_body = data["MessageBody"]
                    if type(data_body) != dict:
                        # global_statistics.stati_tcp.rev_invalid_times += 1
                        print("{0}:TCP receive a invalid SyncChannelState message: {1}". \
                            format(get_timestamp(with_strf=True), bdata[:60]))
                        return utils.request_handle_result.get("invalid")
                    try:
                        node["route_tree"].sync_tree(RouteTree.to_tree(data["MessageBody"]))
                    except Exception:
                        # global_statistics.stati_tcp.rev_invalid_times += 1
                        print("{0}:TCP receive a invalid SyncChannelState message: {1}". \
                            format(get_timestamp(with_strf=True), bdata[:60]))
                        return utils.request_handle_result.get("invalid")
                    else:
                        except_peer = data["Sender"]
                        self.sync_channel_route_to_peer(except_peer)
                    return utils.request_handle_result("correct")
        

    def handle_wsocket_request(self, websocket, strdata):
        """
        handle the websocket request
        """
        # first save the spv_pk and websocket connection map 
        spv_k = utils.get_public_key(data["Sender"])
        self.ws_pk_dict[spv_pk] = websocket
        # data = utils.json_to_dict(strdata)
        data = {}
        msg_type = data.get("MessageType")
        # build map bettween spv pk_key with websocket connection
        if msg_type == "AddChannel":
            # pass the message to wallet to handle
            self._send_jsonrpc_msg("method", strdata)
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
                    url = node_object.data["Pblickkey"] + "@" + node_object.identifier
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
            message = utils.generate_ack_router_info_msg(router)
            self._send_wsocket_msg(websocket, message)
        print(strdata)

    def _send_wsocket_msg(self, con, data):
        """
        :param data: dict type
        """
        ensure_future(WsocketService.send_msg(con, json.dumps(data)))

    def _send_jsonrpc_msg(self, method, data):
        """
        :param data: dict type
        """
        ensure_future(
            AsyncJsonRpc.jsonrpc_request(get_event_loop(), method, json.dumps(data))
        )

    def _send_tcp_msg(self, receiver ,data):
        """
        :param receiver: str type: xxxx@ip:port \n
        :param data: dict type
        """
        bdata = utils.encode_bytes(data)
        # addr = utils.get_addr(sender)
        connection = find_connection(receiver)
        if connection:
            connection.write(bdata)
        else:
            ensure_future(send_tcp_msg_coro(receiver, bdata))
        # add tcp statistics
        # global_statistics.stati_tcp.send_times += 1

    def handle_jsonrpc_response(self, method, response):
        
        print(response)

    def handle_jsonrpc_request(self, method, params):
        # print(params)
        print(type(params))
        if type(params) == str:
            data = json.loads(params)
        else:
            data = params
        msg_type = data.get("MessageType")
        if method == "ShowNodeList":
            return utils.generate_ack_show_node_list(node_list)
        if method == "JoinNet":
            if data.get("ip"):
                self._send_tcp_msg(
                    data["Receiver"],
                    utils.generate_join_net_msg()
                )
            else:
                pass
            return "{'JoinNet': 'OK'}"
        elif method == "SyncWalletData":
            print("Get the wallet sync data\n", data)
            body = data.get("MessageBody")
            node["wallet_info"] = {
                "url": body["Publickey"] + "@" + cg_public_ip_port,
                "deposit": body["CommitMinDeposit"],
                "fee": body["Fee"]
            }
            return json.dumps(utils.generate_ack_sync_wallet_msg(node["wallet_info"]["url"]))
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
                url = node_object.data["Pblickkey"] + "@" + node_object.identifier
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
        elif method == "TransactionMessage":
            if msg_type == "RegisterChannel":
                self._send_tcp_msg(data["Receiver"], data)
            elif msg_type in ["Rsmc","FounderSign","Founder","RsmcSign","FounderFail"]:
                self.handle_transaction_message(data)
        elif method == "SyncBlock":
            # push the data to spvs
            pass
        elif method == "SyncChannel":
            self_url = node["wallet_info"]["url"]
            channel_founder = data["MessageBody"]["Founder"]
            channel_receiver = data["MessageBody"]["Receiver"]
            channel_peer = channel_receiver if channel_founder == self_url else channel_founder
            if msg_type == "AddChannel":
                # send self tree to peer
                message = utils.generate_sync_tree_msg(node["route_tree"], self_url)
                self._send_tcp_msg(channel_peer, message)
            elif msg_type == "UpdateChannel":
                #update balance and send self tree to peers
                self_node = node["route_tree"].get_node(utils.get_ip_port(self_url))
                self_node.data.balance = data["MessageBody"]["Balance"]
                self.sync_channel_route_to_peer()
            elif msg_type == "DeleteChannel":
                # remove channel_peer and notification peers
                node["route_tree"].remove_node(utils.get_ip_port(channel_peer))
                self.sync_channel_route_to_peer()


    def handle_web_first_connect(self, websocket):
        if not node.get("wallet_info"):
            node["wallet_info"] = {
                "deposit": 5,
                "fee": 1,
                "url": "03a6fcaac0e13dfbd1dd48a964f92b8450c0c81c28ce508107bc47ddc511d60e75@" + cg_public_ip_port
            }
        message = utils.generate_node_list_msg(node)
        self._send_wsocket_msg(websocket, message)

    def handle_wsocket_disconnection(self, websocket):
        pass
        #self._add_event_push_web_task()

    def _add_event_push_web_task(self):
        ensure_future(WsocketService.push_by_event(self.websocket.websockets, message))

    def _add_timer_push_web_task(self):
        message = {}
        ensure_future(WsocketService.push_by_timer(self.websocket.websockets, 15, message))
    
    def _init_self_tree(self):
        tag = "node"
        nid = utils.get_ip_port(node["wallet_info"]["url"]),
        pk = utils.get_public_key(node["wallet_info"]["url"])
        spv_list = node["spv_table"].find(pk)
        node["route_tree"].create_node(
            tag="node",
            data = {
                "Ip": nid,
                "Pblickkey": pk,
                "Name": node["name"],
                "Deposit": node["wallet_info"]["deposit"],
                "Fee": node["wallet_info"]["fee"],
                "Balance": node["wallet_info"]["balance"],
                "SpvList": [] if not spv_list else spv_list
            }
        )

    def sync_channel_route_to_peer(self, except_peer=None):
        """
        :param except_peer: str type (except peer url)
        """
        self_tree = node["route_tree"]
        except_nid = None if not except_peer else utils.get_ip_port(except_peer)
        message = utils.generate_sync_tree_msg(self_tree, node["wallet_info"]["url"])
        for child in self_tree.is_branch(self_tree.root):
            if child != except_nid:
                node_object = self_tree.get_node(child)
                ip_port = node_object.data["Ip"].split(":")
                receiver = node_object.data["Pblickey"] + "@" + child
                self._send_tcp_msg(receiver, message)           

    def handle_transaction_message(self, data):
        """
        :param data: bytes type
        """
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
                            data["MessageBody"]["Value"] - node["wallet_info"]["fee"]
                        )
                        pk = utils.parse_url(data["Receiver"])[0]
                        self._send_wsocket_msg(self.ws_pk_dict[pk], json.dumps(message))
                        # left active
                        message = utils.generate_trigger_transaction_msg(
                            data["Sender"],
                            node["wallet_info"]["url"],
                            data["MessageBody"]["Value"] - node["wallet_info"]["fee"]
                        )
                        self._send_jsonrpc_msg("TransactionMessage", message)
                    # xx--node--node--..--xx siuation
                    else:
                        # to self's spv
                        if receiver_pk != self_pk:
                            message = utils.generate_trigger_transaction_msg(
                                node["wallet_info"]["url"],
                                data["Receiver"],
                                data["MessageBody"]["Value"] - node["wallet_info"]["fee"]
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
                        self._send_jsonrpc_msg("TransactionMessage", message)
                    # pxxx---node----exxx for node
                    else:
                        # pxxx is spv
                        if utils.parse_url(data["Sender"])[1] == self_ip_port:
                            # left active
                            left_message = utils.generate_trigger_transaction_msg(
                                data["Sender"],
                                node["wallet_info"]["url"],
                                data["MessageBody"]["Value"] - node["wallet_info"]["fee"]
                            )
                            # right active
                            right_message = utils.generate_trigger_transaction_msg(
                                node["wallet_info"]["url"], # self
                                new_next_jump,
                                data["MessageBody"]["Value"] - node["wallet_info"]["fee"]
                            )
                            self._send_jsonrpc_msg("TransactionMessage", left_message)
                            self._send_jsonrpc_msg("TransactionMessage", right_message)
                        # pxxx is node
                        else:
                            message = utils.generate_trigger_transaction_msg(
                                node["wallet_info"]["url"], # self
                                new_next_jump,
                                data["MessageBody"]["Value"] - node["wallet_info"]["fee"]
                            )
                            self._send_jsonrpc_msg("TransactionMessage", message)
                    # addr = utils.get_addr(new_next_jump)
                    self._send_tcp_msg(new_next_jump, data)
            # invalid msg
            else:
                pass
        # no router info situation
        # send the msg to receiver directly
        else:
            if receiver_ip_port == self_ip_port:
                # to self's spv
                if receiver_pk != self_pk:
                    self._send_wsocket_msg(self.ws_pk_dict[receiver_pk], data)
                # to self's wallet
                else:
                    self._send_jsonrpc_msg("TransactionMessage", data)
            # to self's peer
            else:
                # addr = utils.get_addr(data["Receiver"])
                self._send_tcp_msg(data["Receiver"], data)

gateway_singleton = Gateway()

if __name__ == "__main__":
    from routertree import SPVHashTable
    spv_table = SPVHashTable()
    utils.mock_node_list_data(route_tree, spv_table)
    print(route_tree.nodes)
