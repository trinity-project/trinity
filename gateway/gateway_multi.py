# coding: utf-8
import pprint
import os
import json
import utils
from _wallet import WalletClient
from routertree import SPVHashTable
from routergraph import RouterGraph
from network import Network
from message import Message, MessageMake
from glog import tcp_logger, wst_logger
from config import cg_public_ip_port

class Gateway:
    """
    gateway class
    """
    def __init__(self):
        # the wallet dict
        self.wallet_clients = {}
        self.ntopology = {}
        self.ws_pk_dict = {}
        self.tcp_pk_dict = {}

    def start(self):
        Network.create_servers()
        print("###### Trinity Gateway Start Successfully! ######")
        Network.run_servers_forever()

    def clearn(self):
        Network.clearn_servers()

    def close(self):
        Network.loop.close()
        print("###### Trinity Gateway Closed ######")

    def handle_spv_request(self, websocket, strdata):
        pass

    def handle_node_request(self, protocol, bdata):
        try:
            data = utils.decode_bytes(bdata)
        except UnicodeDecodeError:
            return utils.request_handle_result.get("invalid")
        else:
            if not Message.check_message_is_valid(data):
                return utils.request_handle_result.get("invalid")
            else:
                peername = protocol.transport.get_extra_info('peername')
                peer_ip = "{}".format(peername[0])
                # check sender is peer or not
                # because 'tx message pass on siuatinon' sender may not peer
                if peer_ip == utils.get_ip_port(data["Sender"]).split(":")[0]:
                    sed_pk = utils.get_public_key(data["Sender"])
                    self.tcp_pk_dict[sed_pk] = protocol
                pprint.pprint(self.tcp_pk_dict)
                msg_type = data.get("MessageType")
                if msg_type == "RegisterChannel":
                    pass
                elif msg_type == "ResumeChannel":
                    pass
                elif msg_type in Message.get_tx_msg_types():
                    pass
                elif msg_type == "SyncChannelState":
                    receiver = data.get("Receiver")
                    asset_type = data.get("AssetType")
                    if receiver and asset_type:
                        rev_pk = utils.get_public_key(receiver)
                        router_graph = self.wallets.get(rev_pk).assets.get(asset_type).router_graph
                        router_graph.sync_channel_graph(data)
                        tcp_logger.debug("sync graph from peer successful")
                        print("**********number of edges is: ",router_graph._graph.number_of_edges(),"**********")
                        print("**********",router_graph.show_edgelist(),"**********")
                        if data.get("Broadcast"):
                            data["Sender"] = receiver
                            self.sync_channel_route_to_peer(data)
                            return utils.request_handle_result.get("correct")
                    else:
                        print("!!!!!! the receiver and asset_type not provied in the sync channel msg !!!!!!")
                        return
                

    def handle_wallet_request(self, method, params):
        data = params
        if type(data) == str:
            data = json.loads(data)
        msg_type = data.get("MessageType")
        if method == "SyncWalletData":
            print("Get the wallet sync data\n", data)
            body = data.get("MessageBody")
            WalletClient.add_or_update(
                self.wallet_clients,
                **utils.make_kwargs_for_wallet(body)
            )
            url = self.wallet_clients[body.get("Ip")].wallets[body.get("Publickey")].url
            response = MessageMake.make_ack_sync_wallet_msg(url)
            return json.dumps(response)
        elif method == "GetRouterInfo":
            rev_pk, rev_ip_port = utils.parse_url(data.get("Receiver"))
            sed_pk, sed_ip_port = utils.parse_url(data.get("Sender"))
            # check the wallet is attached this gatway
            # if not do nothing
            if sed_ip_port != cg_public_ip_port:
                return "Invalid request"
            body = data.get("MessageBody")
            asset_type = body.get("AssetType")
            tx_amount = body.get("Value")
            router_graph = self.wallets[rev_pk].assets[asset_type].router_graph
            nids = router_graph.find_shortest_path_decide_by_fee(sed_ip_port, rev_ip_port)
            # the length of path is zero
            if not len(nids):
                return json.dumps(MessageMake.make_ack_router_info_msg(None))
            full_path = []
            total_fee = 0
            for nid in nids:
                node = router_graph._graph.nodes[nid]
                url = node.get("PublicKey") + "@" + node.get("Ip")
                fee = node.get("Fee")
                full_path.append((url, fee))
                index = nids.index(nid)
                if index > 0 and index < len(nids) - 1:
                    total_fee = total_fee + fee
            next_jump = full_path[0][0]
            router = {
                "FullPath": full_path,
                "Next": next_jump
            }
            return json.dumps(MessageMake.make_ack_router_info_msg(router))
        elif method == "TransactionMessage":
            rev = data.get("Receiver")
            rev_pk, rev_ip_port = utils.parse_url(rev)
            if msg_type == "RegisterChannel":
                if rev_ip_port == cg_public_ip_port:
                    Network.send_msg_with_wsocket(self.pk_ws.get(rev_pk), data)
                else:
                    Network.send_msg_with_tcp(rev, data)
            elif msg_type in Message.get_tx_msg_types():
                self.handle_transaction_message(data)
            elif msg_type in Message.get_payment_msg_types():
                Network.send_msg_with_wsocket(self.pk_ws.get(rev_pk), data)
        elif method == "SyncChannel":
            channel_founder = data["MessageBody"]["Founder"]
            channel_receiver = data["MessageBody"]["Receiver"]
            asset_type = list(data["MessageBody"]["Balance"][channel_founder].items())[0][0]
            # founder and receiver are attached the same gateway
            if utils.check_is_same_gateway(channel_founder, channel_receiver):
                fid = utils.get_public_key(channel_founder)
                rid = utils.get_public_key(channel_receiver)
                founder_router_graph = self.wallets.get(fid).assets.get(asset_type).router_graph
                receiver_router_graph = self.wallets.get(rid).assets.get(asset_type).router_graph
                if msg_type == "AddChannel":
                    message_founder = MessageMake.make_sync_graph_msg(
                        "add_whole_graph",
                        channel_founder,
                        source=channel_founder,
                        target=channel_receiver,
                        asset_type=asset_type,
                        route_graph=receiver_router_graph,
                        broadcast=True,
                        excepts=[fid, rid]
                    )
                    founder_router_graph.sync_channel_graph(message_founder)
                    self.sync_channel_route_to_peer(message_founder)
                    message_receiver = MessageMake.make_sync_graph_msg(
                        "add_whole_graph",
                        channel_receiver,
                        source=channel_receiver,
                        target=channel_founder,
                        asset_type=asset_type,
                        route_graph=founder_router_graph,
                        broadcast=True,
                        excepts=[fid, rid]
                    )
                    receiver_router_graph.sync_channel_graph(message_receiver)
                    self.sync_channel_route_to_peer(message_receiver)
                    pprint.pprint(self.wallets)
                elif msg_type == "UpdateChannel":
                    founder_balance = data["MessageBody"]["Balance"][channel_founder][asset_type]
                    founder_node = founder_router_graph.node
                    receiver_balance = data["MessageBody"]["Balance"][channel_receiver][asset_type]
                    receiver_node = receiver_router_graph.node
                    if founder_router_graph._graph.has_node(rid):
                        founder_router_graph._graph.nodes[rid]["Balance"] = receiver_balance
                    if founder_balance != founder_node["Balance"]:
                        founder_node["Balance"] = founder_balance
                        message = MessageMake.make_sync_graph_msg(
                            "update_node_data",
                            channel_founder,
                            source=channel_founder,
                            asset_type=asset_type,
                            node=founder_node,
                            broadcast=True,
                            excepts=[fid, rid]
                        )
                        self.sync_channel_route_to_peer(message)
                    if receiver_router_graph._graph.has_node(fid):
                        receiver_router_graph._graph.nodes[fid]["Balance"] = founder_balance
                    if receiver_balance != receiver_node["Balance"]:
                        receiver_node["Balance"] = receiver_balance
                        message = MessageMake.make_sync_graph_msg(
                            "update_node_data",
                            channel_receiver,
                            source=channel_receiver,
                            asset_type=asset_type,
                            node=receiver_node,
                            broadcast=True,
                            excepts=[fid, rid]
                        )
                        self.sync_channel_route_to_peer(message)
                elif msg_type == "DeleteChannel":
                    if founder_router_graph.has_edge(fid, rid):
                        founder_router_graph.remove_edge(fid, rid)
                        message = MessageMake.make_sync_graph_msg(
                            "remove_single_edge",
                            channel_founder,
                            broadcast=True,
                            asset_type=asset_type,
                            source=channel_founder,
                            target=channel_receiver,
                            excepts=[fid, rid]
                        )
                        self.sync_channel_route_to_peer(message)
                    if receiver_router_graph.has_edge(fid, rid):
                        receiver_router_graph.remove_edge(fid, rid)
                        message = MessageMake.make_sync_graph_msg(
                            "remove_single_edge",
                            channel_receiver,
                            broadcast=True,
                            asset_type=asset_type,
                            source=channel_receiver,
                            target=channel_founder,
                            excepts=[fid, rid]
                        )
                        self.sync_channel_route_to_peer(message)
            else:
                channel_peer = utils.select_channel_peer(channel_founder, channel_receiver, self.wallets)
                channel_source = channel_founder if channel_peer == channel_receiver else channel_receiver
                sid = utils.get_public_key(channel_source)
                tid = utils.get_public_key(channel_peer)
                router_graph = self.wallets.get(utils.get_public_key(channel_source)).assets.get(asset_type).router_graph
                if msg_type == "AddChannel":
                    message = MessageMake.make_sync_graph_msg(
                        "add_whole_graph",
                        channel_source,
                        source=channel_source,
                        target=channel_peer,
                        # source=channel_peer,
                        # target=channel_source,
                        asset_type=asset_type,
                        route_graph=router_graph,
                        broadcast=True,
                        excepts=[sid, tid]
                    )
                    message["Receiver"] = channel_peer
                    Network.send_msg_with_tcp(channel_peer, message)
                elif msg_type == "UpdateChannel":
                    source_balance = data["MessageBody"]["Balance"][channel_source][asset_type]
                    peer_balance = data["MessageBody"]["Balance"][channel_peer][asset_type]
                    source_node = router_graph._graph.nodes(sid)
                    if router_graph._graph.has_node(tid):
                        router_graph._graph.nodes[tid]["Balance"] = peer_balance
                    if source_node["Balance"] != source_balance:
                        source_node["Balance"] = source_balance
                        message = MessageMake.make_sync_graph_msg(
                            "update_node_data",
                            channel_source,
                            source=channel_source,
                            asset_type=asset_type,
                            node=source_node,
                            broadcast=True,
                            excepts=[sid, tid]
                        )
                        self.sync_channel_route_to_peer(message)
                elif msg_type == "DeleteChannel":
                    router_graph.remove_edge(sid, tid)
                    message = MessageMake.make_sync_graph_msg(
                        "remove_single_edge",
                        channel_source,
                        broadcast=True,
                        asset_type=asset_type,
                        source=channel_source,
                        target=channel_peer,
                        excepts=[sid, tid]
                    )
                    self.sync_channel_route_to_peer(message)

    def handle_wallet_response(self, method, response):
        if method == "SyncWallet":
            if type(response) == str:
                response = json.loads(response)
            if not response.get("MessageBody"):
                return
            Wallet.add_or_update_wallet(
                self.wallets,
                **utils.make_kwargs_for_wallet(response.get("MessageBody"))
            )
            self.resume_channel_from_db()

    def sync_channel_route_to_peer(self, message):
        """
        :param except_peer: str type (except peer url)
        """
        asset_type = message.get("AssetType")
        # the caller is neighbors(passon sync msg situation)
        if message.get("Receiver"):
            pk = utils.get_public_key(message["Receiver"])
            router_graph = self.wallets.get(pk).assets.get(asset_type).router_graph
            if message.get("SyncType") == "add_whole_graph":
                message["MessageBody"] = router_graph.to_json()
        # the caller is source(first caller)
        else:
            pk = utils.get_public_key(message["Source"])
            router_graph = self.wallets.get(pk).assets.get(asset_type).router_graph
        excepts = message["Excepts"]
        set_excepts = set(excepts)
        set_neighbors = set(router_graph._graph.neighbors(router_graph.nid))
        union_excepts = set_excepts.union(set_neighbors)
        union_excepts.add(router_graph.nid)
        print("set_neighbors: ",set_neighbors, "set_excepts: ", set_excepts)
        for ner in set_neighbors:
            if ner not in set_excepts:
                receiver = ner + "@" + router_graph._graph.nodes[ner]["Ip"]
                print("===============sync to the neighbors: {}=============".format(ner))
                message["Excepts"] = list(union_excepts)
                message["Receiver"] = receiver
                Network.send_msg_with_tcp(receiver, message)

    def resume_channel_from_db(self):
        for pk, wallet in self.wallets.items():
            channels = utils.get_channels_form_db(wallet.url)
            if channels:
                message = MessageMake.make_resume_channel_msg(wallet.url)
                for channel in channels:
                    peer = channel.dest_addr if channel.src_addr == wallet.url else channel.src_addr
                    if utils.get_ip_port(peer) != cg_public_ip_port:
                        Network.send_msg_with_tcp(peer, message)


gateway_singleton = Gateway()