# coding: utf-8
import pprint
import os
import json
import utils
from routertree import SPVHashTable
from routergraph import RouterGraph
from network import Network
from message import Message, MessageMake
from statistics import Statistics
from glog import tcp_logger, wst_logger
from config import cg_public_ip_port

node_list = set()
node = {
    "wallet_info": None,
    "route_graph": RouterGraph(),
    "spv_table": SPVHashTable()
    # configurable
    # "name": cg_node_name
}
global_statistics = Statistics()
class Gateway():
    """
    gateway class
    """
    def __init__(self):
        """Counstruct"""
        self.websocket = None
        self.tcpserver = None
        self.rpcserver = None
        self.loop = None
        self.tcp_pk_dict = {}
        self.ws_pk_dict = {}

    def start(self):
        """ start gateway"""
        Network.create_servers()
        if os.getenv("resume"):
            self.resume_channel_from_db()
        print("###### Trinity Gateway Start Successfully! ######")
        Network.run_servers_forever()

    def clearn(self):
        """
        clearn task
        """
        Network.clearn_servers()

    def close(self):
        Network.loop.close()
        print("###### Trinity Gateway Closed ######")

    def handle_node_request(self, protocol, bdata):
        try:
            data = utils.decode_bytes(bdata)
        except UnicodeDecodeError:
            return utils.request_handle_result.get("invalid")
        else:
            
            if not Message.check_message_is_valid(data):
                return utils.request_handle_result.get("invalid")
            else:
                # first save the node_pk and websocket connection map
                peername = protocol.transport.get_extra_info('peername')
                peer_ip = "{}".format(peername[0])
                # check sender is peer or not
                # because 'tx message pass on siuatinon' sender may not peer
                if peer_ip == utils.get_ip_port(data["Sender"]).split(":")[0]:
                    node_pk = utils.get_public_key(data["Sender"])
                    self.tcp_pk_dict[node_pk] = protocol
                pprint.pprint(self.tcp_pk_dict)
                msg_type = data.get("MessageType")
                if msg_type == "JoinNet":
                    # join net sync node_list
                    message = MessageMake.make_ack_node_join_msg(
                        sender=data["Receiver"],
                        receiver=data["Sender"],
                        node_list=node_list
                    )
                    Network.send_msg_with_tcp(data["Receiver"], message)
                    node_list.add(data["sender"])
                elif msg_type == "AckJoin":
                    # node_list.add(data["Receiver"])
                    node_list = node_list | data["NodeList"]
                elif msg_type == "RegisterChannel":
                    Network.send_msg_with_jsonrpc("TransactionMessage", data)
                elif msg_type == "AddChannel":
                    # basic check
                    # request wallet to handle 
                    if not utils.check_wallet_url_correct(data["Receiver"], local_url):
                        # not self's wallet address
                        pass
                    else:
                        Network.send_msg_with_jsonrpc("CreateChannle", data)

                elif msg_type in Message.get_tx_msg_types():
                    self.handle_transaction_message(data)
                    return utils.request_handle_result.get("correct")
                elif msg_type == "ResumeChannel":
                    # when node accept the restart peer resume the channel request
                    # then flag the sync message as no need to broadcast to peer's peer
                    message = MessageMake.make_sync_graph_msg(
                        "add_whole_graph", 
                        node["wallet_info"]["url"],
                        route_graph=node["route_graph"],
                        broadcast=False
                    )
                    Network.send_msg_with_tcp(data.get("Sender"), message)
                    return utils.request_handle_result.get("correct")
                elif msg_type == "SyncChannelState":
                    # node receive the syncchannel msg
                    # first update self
                    # then sync to self's neighbors except (has synced)
                    try:
                        node["route_graph"].sync_channel_graph(data)
                        tcp_logger.debug("sync graph from peer successful")
                        print("**********number of edges is: ",node["route_graph"]._graph.number_of_edges(),"**********")
                        print("**********",node["route_graph"].show_edgelist(),"**********")
                    except Exception:
                        tcp_logger.exception("sync tree from peer raise an exception")
                        return utils.request_handle_result.get("invalid")
                    else:
                        if data["Broadcast"]:
                            data["Sender"] = node["wallet_info"]["url"]
                            self.sync_channel_route_to_peer(data)
                        # node["route_graph"].draw_graph()
                        return utils.request_handle_result.get("correct")
        
    def handle_spv_request(self, websocket, strdata):
        """
        handle the websocket request
        """
        # first save the spv_pk and websocket connection map
        data = utils.json_to_dict(strdata)
        spv_pk = utils.get_public_key(data["Sender"])
        self.ws_pk_dict[spv_pk] = websocket
        # data = {}
        msg_type = data.get("MessageType")
        # build map bettween spv pk_key with websocket connection
        if msg_type == "AddChannel":
            # pass the message to wallet to handle
            Network.send_msg_with_jsonrpc("AddChannel", data)
        elif msg_type == "CombinationTransaction":
            pass
        elif msg_type == "PaymentLink":
            # to send to wallet
            Network.send_msg_with_jsonrpc("TransactionMessage", data)
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
                nids = node["route_graph"].find_shortest_path_decide_by_fee(node["route_graph"].nid, receiver_ip_port)
                # next_jump = nids.index()
                full_path = []
                for nid in nids:
                    node_object = node["route_graph"]._graph.nodes(nid)
                    url = node_object.get("Pblickkey") + "@" + node_object.get("Ip")
                    fee = node_object.get("Fee")
                    full_path.append((url, fee))
                if not len(full_path):
                    router = None
                else:
                    next_jump = full_path[0][0]
                    router = {
                        "FullPath": full_path,
                        "Next": next_jump
                    }
            message = MessageMake.make_ack_router_info_msg(router)
            Network.send_msg_with_wsocket(websocket, message)
            
    def handle_wallet_request(self, method, params):
        # print(params)
        print(type(params))
        # print(params)
        if type(params) == str:
            data = json.loads(params)
        else:
            data = params
        msg_type = data.get("MessageType")
        if method == "ShowNodeList":
            message = MessageMake.make_ack_show_node_list(node_list)
            return json.dumps(message)
        if method == "JoinNet":
            if data.get("ip"):
                Network.send_msg_with_tcp(
                    data.get("Receiver"),
                    MessageMake.make_join_net_msg(node["wallet_info"]["url"])
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
                "fee": body["Fee"],
                "balance": body["Balance"],
                "name": body["Alias"]
            }
            # todo init self tree from local file or db
            self._init_or_update_self_graph()
            response = MessageMake.make_ack_sync_wallet_msg(node["wallet_info"]["url"])
            return json.dumps(response)
        # search chanenl router return the path
        elif method == "GetRouterInfo":
            receiver = data.get("Receiver")
            receiver_ip_port = utils.parse_url(receiver)[1]
            try:
                # search tree through ip_port(node identifier in the tree)
                nids = node["route_graph"].find_shortest_path_decide_by_fee(node["route_graph"].nid, receiver_ip_port)
            # receiver not in the tree
            except Exception:
                response = MessageMake.make_ack_router_info_msg(None)
                return json.dumps(response)
            # next_jump = nids.index()
            full_path = []
            for nid in nids:
                node_object = node["route_graph"]._graph.nodes[nid]
                url = node_object.get("Pblickkey") + "@" + node_object.get("Ip")
                fee = node_object.get("Fee")
                full_path.append((url, fee))
            next_jump = full_path[0][0]
            
            if not len(full_path):
                return json.dumps(MessageMake.make_ack_router_info_msg(None))
            else:
                router = {
                    "FullPath": full_path,
                    "Next": next_jump
                }
                return json.dumps(MessageMake.make_ack_router_info_msg(router))
        elif method == "TransactionMessage":
            if msg_type == "RegisterChannel":
                Network.send_msg_with_tcp(data.get("Receiver"), data)
            elif msg_type in Message.get_tx_msg_types():
                self.handle_transaction_message(data)
            elif msg_type in ["PaymentLinkAck", "PaymentAck"]:
                recv_pk = utils.get_public_key(data.get("Receiver"))
                connection = self.ws_pk_dict.get(recv_pk)
                if connection:
                    Network.send_msg_with_wsocket(connection,data)
                else:
                    wst_logger.info("the receiver is disconnected")
        elif method == "SyncBlock":
            # push the data to spvs
            pass
        elif method == "SyncChannel":
            self_url = node["wallet_info"]["url"]
            channel_founder = data["MessageBody"]["Founder"]
            channel_receiver = data["MessageBody"]["Receiver"]
            channel_peer = channel_receiver if channel_founder == self_url else channel_founder
            if msg_type == "AddChannel":
                route_graph = node["route_graph"]
                # only channel receiver as the broadcast source
                if channel_founder == self_url:
                    broadcast = True
                    print("{}and{}build channel,only {} broadcast channel graph".format(channel_founder, channel_peer, channel_peer))
                else:
                    broadcast = False
                # if route_graph.has_node(channel_peer):
                #     sync_type = "add_single_edge"
                sync_type = "add_whole_graph"
                
                message = MessageMake.make_sync_graph_msg(
                    sync_type,
                    self_url,
                    source=self_url,
                    target=channel_peer,
                    route_graph=route_graph,
                    broadcast=broadcast,
                    excepts=[]
                )
                Network.send_msg_with_tcp(channel_peer, message)

            elif msg_type == "UpdateChannel":
                # first update self's balance and sync with self's peers
                self_node = node["route_graph"].node
                self_node["Balance"] = data["MessageBody"]["Balance"]
                message = MessageMake.make_sync_graph_msg(
                    "update_node_data",
                    self_url,
                    source=self_url,
                    node=self_node,
                    excepts=[]
                )
                self.sync_channel_route_to_peer(message)
            elif msg_type == "DeleteChannel":
                # remove channel_peer and notification peers
                sid = utils.get_ip_port(self_url)
                tid = utils.get_ip_port(channel_peer)
                node["route_graph"].remove_edge(sid, tid)
                message = MessageMake.make_sync_graph_msg(
                    "remove_single_edge",
                    self_url,
                    source=self_url,
                    target=channel_peer,
                    excepts=[]
                )
                self.sync_channel_route_to_peer(message)
        
    def handle_spv_make_connection(self, websocket):
        if not node.get("wallet_info"):
            node["wallet_info"] = {
                "deposit": 5,
                "fee": 1,
                "name": "test",
                "balance": 15,
                "url": "03a6fcaac0e13dfbd1dd48a964f92b8450c0c81c28ce508107bc47ddc511d60e75@" + cg_public_ip_port
            }
            self._init_or_update_self_graph()
        message =  MessageMake.make_node_list_msg(node["route_graph"])
        Network.send_msg_with_wsocket(websocket, message)

    def handle_spv_lost_connection(self, websocket):
        pass
    
    def _init_or_update_self_graph(self):
        nid = utils.get_ip_port(node["wallet_info"]["url"])
        pk = utils.get_public_key(node["wallet_info"]["url"])
        spv_list = node["spv_table"].find(pk)
        self_nid =  node["route_graph"].nid
        data = {
            "Nid": nid,
            "Ip": nid,
            "Pblickkey": pk,
            "Name": node["wallet_info"]["name"],
            "Deposit": node["wallet_info"]["deposit"],
            "Fee": node["wallet_info"]["fee"],
            "Balance": node["wallet_info"]["balance"],
            "SpvList": [] if not spv_list else spv_list
        }
        if not self_nid:
            node["route_graph"].add_self_node(data)
        else:
            node["route_graph"].update_data(data)
            # todo sync to self's peers
        # node["route_graph"].draw_graph()

    def sync_channel_route_to_peer(self, message, path=None, except_peer=None):
        """
        :param except_peer: str type (except peer url)
        """
        if message.get("SyncType") == "add_whole_graph":
            message["MessageBody"] = node["route_graph"].to_json()
        # message["Path"] = path
        # nodes = message["Nodes"]
        # except_nid = None if not except_peer else utils.get_ip_port(except_peer)
        # source_nid = utils.get_ip_port(message["Source"])
        excepts = message["Excepts"]
        # excepts.append(utils.get_ip_port(node["wallet_info"]["url"]))
        set_excepts = set(excepts)
        set_neighbors = set(node["route_graph"]._graph.neighbors(node["route_graph"].nid))
        union_excepts_excepts = set_excepts.union(set_neighbors)
        union_excepts_excepts.add(utils.get_ip_port(node["wallet_info"]["url"]))
        for ner in set_neighbors:
            if ner not in set_excepts:
                receiver = node["route_graph"].node["Pblickkey"] + "@" + ner
                print("===============sync to the neighbors: {}=============".format(ner))
                message["Excepts"] = list(union_excepts_excepts)
                Network.send_msg_with_tcp(receiver, message)

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
                if full_path[len(full_path)-1][0] == next_jump:
                    # spv---node---spv siuation
                    if len(full_path) == 1:
                        # right active
                        message = MessageMake.make_trigger_transaction_msg(
                            sender=node["wallet_info"]["url"],
                            receiver=data["Receiver"],
                            asset_type="TNC",
                            amount=data["MessageBody"]["Value"] - node["wallet_info"]["fee"]
                        )
                        pk = utils.parse_url(data["Receiver"])[0]
                        Network.send_msg_with_wsocket(self.ws_pk_dict[pk], message)
                        # left active
                        message = MessageMake.make_trigger_transaction_msg(
                            sender=data["Sender"],
                            receiver=node["wallet_info"]["url"],
                            asset_type="TNC",
                            amount=data["MessageBody"]["Value"] - node["wallet_info"]["fee"]
                        )
                        Network.send_msg_with_jsonrpc("TransactionMessage", message)
                    # xx--node--node--..--xx siuation
                    else:
                        # to self's spv
                        if receiver_pk != self_pk:
                            message = MessageMake.make_trigger_transaction_msg(
                                sender=node["wallet_info"]["url"],
                                receiver=data["Receiver"],
                                asset_type="TNC",
                                amount=data["MessageBody"]["Value"] - node["wallet_info"]["fee"]
                            )
                            pk = utils.parse_url(data["Receiver"])[0]
                            Network.send_msg_with_wsocket(self.ws_pk_dict[pk], json.dumps(message))
                        # to self's wallet 
                        # previs hased send the transactions to this node
                        # do nothing to the origin mesg
                        else:
                            pass
                # go on pass msg
                else:
                    new_next_jump = full_path[full_path.index([next_jump, node["wallet_info"]["fee"]]) + 1][0]
                    data["RouterInfo"]["Next"] = new_next_jump
                    # node1--node2--xxx this for node1 siuation
                    if data["Sender"] == node["wallet_info"]["url"]:
                        message = MessageMake.make_trigger_transaction_msg(
                            sender=node["wallet_info"]["url"],
                            receiver=new_next_jump,
                            asset_type="TNC",
                            amount=data["MessageBody"]["Value"]
                        )
                        Network.send_msg_with_jsonrpc("TransactionMessage", message)
                    # pxxx---node----exxx for node
                    else:
                        # pxxx is spv
                        if utils.parse_url(data["Sender"])[1] == self_ip_port:
                            # left active
                            left_message = MessageMake.make_trigger_transaction_msg(
                                sender=data["Sender"],
                                receiver=node["wallet_info"]["url"],
                                asset_type="TNC",
                                amount=data["MessageBody"]["Value"]- node["wallet_info"]["fee"]
                            )
                            # right active
                            right_message = MessageMake.make_trigger_transaction_msg(
                                sender=node["wallet_info"]["url"],
                                receiver=new_next_jump,
                                asset_type="TNC",
                                amount=data["MessageBody"]["Value"]- node["wallet_info"]["fee"]
                            )
                            Network.send_msg_with_jsonrpc("TransactionMessage", left_message)
                            Network.send_msg_with_jsonrpc("TransactionMessage", right_message)
                        # pxxx is node
                        else:
                            message = MessageMake.make_trigger_transaction_msg(
                                sender=node["wallet_info"]["url"],
                                receiver=new_next_jump,
                                asset_type="TNC",
                                amount=data["MessageBody"]["Value"]- node["wallet_info"]["fee"]
                            )
                            Network.send_msg_with_jsonrpc("TransactionMessage", message)
                    # addr = utils.get_addr(new_next_jump)
                    Network.send_msg_with_tcp(new_next_jump, data)
            # invalid msg
            else:
                pass
        # no router info situation
        # send the msg to receiver directly
        else:
            if receiver_ip_port == self_ip_port:
                # to self's spv
                if receiver_pk != self_pk:
                    Network.send_msg_with_wsocket(self.ws_pk_dict[receiver_pk], data)
                # to self's wallet
                else:
                    Network.send_msg_with_jsonrpc("TransactionMessage", data)
            # to self's peer
            else:
                # addr = utils.get_addr(data["Receiver"])
                Network.send_msg_with_tcp(data.get("Receiver"), data)

    def resume_channel_from_db(self):
        node["wallet_info"] = {
            "url": "pk1@localhost:8089",
            "deposit": 1,
            "fee": 1,
            "balance": 10
        }
        self._init_or_update_self_graph()
        peer_list = ["pk2@localhost:8090","pk3@localhost:8091"]
        message = MessageMake.make_resume_channel_msg(node["wallet_info"]["url"])
        for peer in peer_list:
            Network.send_msg_with_tcp(peer, message)


gateway_singleton = Gateway()