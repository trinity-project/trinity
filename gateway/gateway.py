# coding: utf-8
import time
import os
import json
import utils
from _wallet import WalletClient
from topo import Nettopo
from network import Network
from message import Message, MessageMake
from glog import tcp_logger, wst_logger, rpc_logger
from config import cg_public_ip_port, cg_wsocket_addr

class Gateway:
    """
    gateway class
    """
    def __init__(self):
        self.wallet_detect_timestamp = int(time.time())
        self.wallet_detect_interval = 60
        self.wallet_clients = {}
        self.net_topos = {}
        self.ws_pk_dict = {}
        self.tcp_pk_dict = {}

    def start(self):
        Network.create_servers()
        print("###### Trinity Gateway Start Successfully! ######")
        self.notifica_walelt_clis_on_line()
        Network.run_servers_forever()

    def clearn(self):
        Network.clearn_servers()

    def close(self):
        Network.loop.close()
        print("###### Trinity Gateway Closed ######")

    def handle_spv_request(self, websocket, strdata):
        data = utils.json_to_dict(strdata)
        sender = data.get("Sender")
        if not utils.check_is_spv(sender): return
        receiver = data.get("Receiver")
        msg_type = data.get("MessageType")
        asset_type = data.get("MessageBody").get("AssetType")
        spv_pk = utils.get_public_key(sender)
        self.ws_pk_dict[spv_pk] = websocket
        if msg_type == "RegisterChannel":
            owned, wallet_state = utils.check_is_owned_wallet(receiver, self.wallet_clients)
            if not (owned and wallet_state): return
            wallet_addr = utils.get_wallet_addr(receiver, self.wallet_clients)
            Network.send_msg_with_jsonrpc("TransactionMessage", wallet_addr, data)
        # first check the receiver is self or not
        if msg_type == "PaymentLink":
            if not asset_type:
                asset_type = data.get("MessageBody").get("Parameter").get("Assets")

            owned, wallet_state = utils.check_is_owned_wallet(receiver, self.wallet_clients)
            if not (owned and wallet_state): return
            wallet_addr = utils.get_wallet_addr(receiver, self.wallet_clients)
            Network.send_msg_with_jsonrpc("TransactionMessage", wallet_addr, data)
        elif msg_type in Message.get_tx_msg_types():
            self.handle_transaction_message(data)
        elif msg_type == "CombinationTransaction":
            pass
        elif msg_type == "GetRouterInfo":
            magic = data.get("Magic")
            net_topo = self.net_topos.get(utils.asset_type_magic_patch(asset_type, magic))
            source = data.get("MessageBody").get("NodeList")
            route = utils.search_route_for_spv(sender, source, receiver, net_topo, asset_type, magic)
            message = MessageMake.make_ack_router_info_msg(route)
            Network.send_msg_with_wsocket(websocket, message)
        elif msg_type == "GetNodeList":
            magic = data.get("Magic")
            net_topo = self.net_topos.get(utils.asset_type_magic_patch(asset_type, magic))
            if net_topo:
                message =  MessageMake.make_node_list_msg(net_topo)
                Network.send_msg_with_wsocket(websocket, message)
            else:
                message = {
                    "MessageType": "NodeList",
                    "Nodes": None
                }
                Network.send_msg_with_wsocket(websocket, message)
        elif msg_type == "GetChannelInfo":
            magic = data.get("Magic")
            net_topo = self.net_topos.get(utils.asset_type_magic_patch(asset_type, magic))
            spv_peers = net_topo.spv_table.find_keys(spv_pk) if net_topo else []
            message = MessageMake.make_ack_channel_info(spv_peers)
            Network.send_msg_with_wsocket(websocket, message)
        elif msg_type == "UpdateChannel":
            wallet_addr = utils.get_wallet_addr(receiver, self.wallet_clients)
            Network.send_msg_with_jsonrpc("TransactionMessage", wallet_addr, data)

    def handle_node_request(self, protocol, bdata):
        try:
            data = utils.decode_bytes(bdata)
        except UnicodeDecodeError:
            return utils.request_handle_result.get("invalid")
        else:
            if not Message.check_message_is_valid(data):
                return utils.request_handle_result.get("invalid")
            else:
                msg_type = data.get("MessageType")
                if msg_type == "RegisterKeepAlive":
                    protocol.is_wallet_cli = True
                    protocol.wallet_ip = data.get("Ip")
                    if not len(self.net_topos.keys()):
                        ip, port = protocol.wallet_ip.split(":")
                        addr = (ip, int(port))
                        Network.send_msg_with_jsonrpc("GetChannelList", addr, {})
                    return
                peername = protocol.transport.get_extra_info('peername')
                peer_ip = "{}".format(peername[0])
                # check sender is peer or not
                # because 'tx message pass on siuatinon' sender may not peer
                if peer_ip == utils.get_ip_port(data["Sender"]).split(":")[0]:
                    sed_pk = utils.get_public_key(data["Sender"])
                    self.tcp_pk_dict[sed_pk] = protocol
                if msg_type == "RegisterChannel":
                    receiver = data.get("Receiver")
                    wallet_addr = utils.get_wallet_addr(receiver, self.wallet_clients)
                    Network.send_msg_with_jsonrpc("TransactionMessage", wallet_addr, data)
                elif msg_type in Message.get_tx_msg_types():
                    self.handle_transaction_message(data)
                    return utils.request_handle_result.get("correct")
                elif msg_type == "ResumeChannel":
                    asset_type = data.get("AssetType")
                    magic = data.get("Magic")
                    if not asset_type: return
                    net_topo = self.net_topos.get(utils.asset_type_magic_patch(asset_type, magic))
                    if not net_topo: return
                    sender = data.get("Sender")
                    receiver = data.get("Receiver")
                    if not sender or not receiver: return
                    message = MessageMake.make_sync_graph_msg(
                        "add_whole_graph",
                        receiver,
                        source=receiver,
                        target=sender,
                        asset_type=asset_type,
                        magic=magic,
                        route_graph=net_topo,
                        broadcast=False
                    )
                    message["Receiver"] = sender
                    Network.send_msg_with_tcp(sender, message)
                elif msg_type == "SyncChannelState":
                    receiver = data.get("Receiver")
                    asset_type = data.get("AssetType")
                    magic = data.get("Magic")
                    if receiver and asset_type and magic:
                        net_topo = self.net_topos.get(utils.asset_type_magic_patch(asset_type, magic))
                        sync_type = data.get("SyncType")
                        # for solve node sync msg ahead wallet_cli sync msg
                        if sync_type == "add_whole_graph":
                            tpk = utils.get_public_key(data.get("Target"))
                            wallet = utils.get_all_active_wallet_dict(self.wallet_clients).get(tpk)
                            if wallet:
                                Nettopo.add_or_update(self.net_topos, asset_type, magic, wallet)
                                net_topo = self.net_topos.get(utils.asset_type_magic_patch(asset_type, magic))
                        elif not net_topo: return
                        net_topo.sync_channel_graph(data)
                        if sync_type == "add_whole_graph":
                            for nid in net_topo.get_nodes():
                                node = net_topo.get_node_dict(nid)
                                wallet_cli = self.wallet_clients.get(node["WalletIp"])
                                opened_wallet = wallet_cli.opened_wallet if wallet_cli else None
                                if node["Ip"] == cg_public_ip_port and not node["Status"] and opened_wallet:
                                    node["Status"] = 1
                                    sync_node_data_to_peer(node, net_topo)
                        tcp_logger.info("sync graph from peer successful")
                        tcp_logger.info("**********number of edges is: {}**********".format(net_topo.get_number_of_edges()))
                        if data.get("Broadcast"):
                            data["Sender"] = receiver
                            self.sync_channel_route_to_peer(data)
                            return utils.request_handle_result.get("correct")
                    else:
                        tcp_logger.error("!!!!!! the receiver or asset_type or magic not provied in the sync channel msg !!!!!!")
                        return

    def handle_node_off(self, peername):
        ip = str(peername[0])
        for key in self.net_topos:
            net_topo = self.net_topos[key]
            for nid in net_topo.get_nodes():
                node = net_topo.get_node_dict(nid)
                if node["Ip"].split(":")[0] == ip:
                    node["Status"] = 0
                    sync_node_data_to_peer(node, net_topo)

    def handle_wallet_request(self, method, params):
        data = params
        if type(data) == str:
            data = json.loads(data)
        # rpc_logger.info("<-- receiver data : {}".format(data))
        msg_type = data.get("MessageType")
        if method == "Search":
            public_key = data.get("Publickey")
            asset_type = data.get("AssetType")
            net_topo = self.net_topos.get(utils.asset_type_magic_patch(asset_type, data))
            # print("********", net_topo)
            if not net_topo or not public_key: return
            if msg_type == "SearchWallet":
                wallet_pks = []
                # first check the spv is on-line
                print("***********", net_topo.spv_table.find_keys(public_key))
                print("***********", self.ws_pk_dict.get(public_key))
                # if self.ws_pk_dict.get(public_key):
                for key in net_topo.spv_table.find_keys(public_key):
                    # check the wallet is on-line
                    if net_topo.get_node_dict(key)["Status"]:
                        wallet_pks.append(key)
                message = MessageMake.make_ack_search_target_wallet(wallet_pks)
            elif msg_type == "SearchSpv":
                data = net_topo.spv_table.to_json()
                message = MessageMake.make_ack_search_spv(data)
            return json.dumps(message)
        if method == "SyncWalletData":
            rpc_logger.info("Get the wallet sync data:\n{}".format(data))
            body = data.get("MessageBody")
            magic = data.get("Magic") if data.get("Magic") else ""
            wallet, last_opened_wallet_pk, add = WalletClient.add_or_update(
                self.wallet_clients,
                **utils.make_kwargs_for_wallet(body)
            )
            if add: utils.save_wallet_cli(self.wallet_clients)
            self.handle_wallet_cli_on_line(wallet, last_opened_wallet_pk, magic)
            spv_ip_port = "{}:{}".format(cg_wsocket_addr[0], cg_wsocket_addr[1])
            response = MessageMake.make_ack_sync_wallet_msg(wallet.url, spv_ip_port)
            # self.detect_wallet_client_status()
            return json.dumps(response)
        elif method == "SyncBlock":
            sender = data.get("Sender")
            owned, wallet_state = utils.check_is_owned_wallet(sender, self.wallet_clients)
            if owned and wallet_state:
                Network.add_event_push_web_task(data)
                # self.detect_wallet_client_status()
            return "OK"
        elif method == "GetRouterInfo":
            rpc_logger.info("Get the wallet router info request:\n{}".format(data))
            sender = data.get("Sender")
            receiver = data.get("Receiver")
            body = data.get("MessageBody")
            asset_type = body.get("AssetType")
            tx_amount = body.get("Value")
            magic = data.get("Magic")
            # check the wallet is attached this gatway
            # if not do nothing
            owned, wallet_state = utils.check_is_owned_wallet(sender, self.wallet_clients)
            if not (owned and wallet_state):
                return "wallet public key check failed"
            net_topo = self.net_topos.get(utils.asset_type_magic_patch(asset_type, magic))
            route = utils.search_route_for_wallet(sender, receiver, net_topo, asset_type, magic)
            return json.dumps(MessageMake.make_ack_router_info_msg(route))
        elif method == "TransactionMessage":
            rpc_logger.info("Get the wallet tx message: {}".format(msg_type))
            rev = data.get("Receiver")
            rev_pk, rev_ip_port = utils.parse_url(rev)
            if msg_type == "RegisterChannel":
                if utils.check_is_spv(rev):
                    Network.send_msg_with_wsocket(self.ws_pk_dict.get(rev_pk), data)
                else:
                    Network.send_msg_with_tcp(rev, data)
            elif msg_type in Message.get_tx_msg_types():
                self.handle_transaction_message(data)
            elif msg_type in Message.get_payment_msg_types():
                Network.send_msg_with_wsocket(self.ws_pk_dict.get(rev_pk), data)
        elif method == "SyncChannel":
            rpc_logger.info("Get the wallet sync channel message:\n{}".format(data))
            channel_founder = data["MessageBody"]["Founder"]
            channel_receiver = data["MessageBody"]["Receiver"]
            asset_type = list(data["MessageBody"]["Balance"][channel_founder].items())[0][0]
            channel_name = data["MessageBody"]["ChannelName"]
            magic = data.get("Magic")
            net_topo = self.net_topos.get(utils.asset_type_magic_patch(asset_type, magic))
            # founder and receiver are attached the same gateway
            if utils.check_is_same_gateway(channel_founder, channel_receiver):
                fid = utils.get_public_key(channel_founder)
                rid = utils.get_public_key(channel_receiver)
                if msg_type == "AddChannel":
                    wallets = utils.get_all_active_wallet_dict(self.wallet_clients)
                    receiver_wallet = wallets[rid]
                    founder_wallet = wallets[fid]
                    receiver_wallet.channel_balance[channel_name] = data["MessageBody"]["Balance"][channel_receiver][asset_type]
                    founder_wallet.channel_balance[channel_name] = data["MessageBody"]["Balance"][channel_founder][asset_type]
                    Nettopo.add_or_update(self.net_topos, asset_type, magic, founder_wallet)
                    Nettopo.add_or_update(self.net_topos, asset_type, magic, receiver_wallet)
                    # net_topo = self.net_topos[asset_type]
                    net_topo = self.net_topos.get(utils.asset_type_magic_patch(asset_type, magic))
                    net_topo.add_edge(fid, rid)
                    message = MessageMake.make_sync_graph_msg(
                        "add_whole_graph",
                        [channel_founder, channel_receiver],
                        source=channel_founder,
                        target=channel_receiver,
                        asset_type=asset_type,
                        magic=magic,
                        route_graph=net_topo,
                        broadcast=True,
                        # excepts=[fid, rid]
                        excepts = list(net_topo.nids)
                    )
                    self.sync_channel_route_to_peer(message)
                elif msg_type == "UpdateChannel":
                    if not net_topo: return
                    founder_balance = data["MessageBody"]["Balance"][channel_founder][asset_type]
                    founder_node = net_topo.get_node_dict(fid)
                    receiver_balance = data["MessageBody"]["Balance"][channel_receiver][asset_type]
                    receiver_node = net_topo.get_node_dict(rid)
                    if founder_balance != founder_node["Balance"][channel_name]:
                        founder_node["Balance"][channel_name] = founder_balance
                        receiver_node["Balance"][channel_name] = receiver_balance
                        message = MessageMake.make_sync_graph_msg(
                            "update_node_data",
                            [channel_founder, channel_receiver],
                            source=channel_founder,
                            asset_type=asset_type,
                            magic=magic,
                            node=[founder_node, receiver_node],
                            broadcast=True,
                            excepts = list(net_topo.nids)
                        )
                        self.sync_channel_route_to_peer(message)
                elif msg_type == "DeleteChannel":
                    result = net_topo.remove_edge(fid, rid)
                    if result:
                        message = MessageMake.make_sync_graph_msg(
                            "remove_single_edge",
                            [channel_founder, channel_receiver],
                            broadcast=True,
                            asset_type=asset_type,
                            magic=magic,
                            source=channel_founder,
                            target=channel_receiver,
                            excepts = list(net_topo.nids)
                        )
                        self.sync_channel_route_to_peer(message)
            else:
                channel_peer, channel_source = utils.select_channel_peer_source(channel_founder, channel_receiver)
                sid = utils.get_public_key(channel_source)
                tid = utils.get_public_key(channel_peer)
                if msg_type == "AddChannel":
                    wallets = utils.get_all_active_wallet_dict(self.wallet_clients)
                    s_wallet = wallets[sid]
                    s_wallet.channel_balance[channel_name] = data["MessageBody"]["Balance"][channel_source][asset_type]
                    Nettopo.add_or_update(self.net_topos, asset_type, magic, s_wallet)
                    net_topo = self.net_topos.get(utils.asset_type_magic_patch(asset_type, magic))
                # peer is spv
                if utils.check_is_spv(channel_peer):
                    if msg_type == "AddChannel":
                        net_topo.spv_table.add(sid, tid)
                    elif msg_type == "UpdateChannel":
                        # in general the spv trust the route node
                        pass
                    elif msg_type == "DeleteChannel":
                        net_topo.spv_table.remove(sid, tid)
                    Network.send_msg_with_wsocket(self.ws_pk_dict.get(tid), data)
                    return "OK"
                if msg_type == "AddChannel":
                    message = MessageMake.make_sync_graph_msg(
                        "add_whole_graph",
                        channel_source,
                        source=channel_source,
                        target=channel_peer,
                        asset_type=asset_type,
                        magic=magic,
                        route_graph=net_topo,
                        broadcast=True,
                        excepts = [tid] + list(net_topo.nids)
                    )
                    message["Receiver"] = channel_peer
                    Network.send_msg_with_tcp(channel_peer, message)
                elif msg_type == "UpdateChannel":
                    if not net_topo: return
                    source_balance = data["MessageBody"]["Balance"][channel_source][asset_type]
                    peer_balance = data["MessageBody"]["Balance"][channel_peer][asset_type]
                    source_node = net_topo.get_node_dict(sid)
                    if source_node["Balance"][channel_name] != source_balance:
                        source_node["Balance"][channel_name] = source_balance
                        message = MessageMake.make_sync_graph_msg(
                            "update_node_data",
                            channel_source,
                            source=channel_source,
                            asset_type=asset_type,
                            magic=magic,
                            node=source_node,
                            broadcast=True,
                            excepts = [tid] + list(net_topo.nids)
                        )
                        self.sync_channel_route_to_peer(message)
                elif msg_type == "DeleteChannel":
                    result = net_topo.remove_edge(sid, tid)
                    if result:
                        message = MessageMake.make_sync_graph_msg(
                            "remove_single_edge",
                            channel_source,
                            broadcast=True,
                            asset_type=asset_type,
                            magic=magic,
                            source=channel_source,
                            target=channel_peer,
                            excepts = [tid] + list(net_topo.nids)
                        )
                        self.sync_channel_route_to_peer(message)
        elif method == "CloseWallet":
            cli_ip = data.get("Ip")
            magic = data.get("Magic") if data.get("Magic") else ""
            self.handle_wallet_cli_off_line(cli_ip, magic=magic)

    def handle_wallet_response(self, method, response):
        if method == "GetChannelList":
            rpc_logger.info("Get the wallet channel list message:\n{}".format(response))
            if type(response) == str:
                response = json.loads(response)
            self.handle_channel_list_message(response)

    def handle_spv_make_connection(self, websocket):
        pass

    def handle_spv_lost_connection(self, websocket):
        pass

    def sync_channel_route_to_peer(self, message):
        """
        :param except_peer: str type (except peer url)
        """
        asset_type = message.get("AssetType")
        magic = message.get("Magic")
        net_topo = self.net_topos.get(utils.asset_type_magic_patch(asset_type, magic))
        sender = message.get("Sender")
        if message.get("SyncType") == "add_whole_graph":
            message["MessageBody"] = net_topo.to_json()
        # wallets in the same gateway first call(call in handle_wallet_request)
        set_neighbors = set()
        for nid in net_topo.nids:
            set_nid_neighbors = net_topo.get_neighbors_set(nid)
            set_neighbors = set_neighbors.union(set_nid_neighbors)
        set_neighbors = set_neighbors.difference(net_topo.nids)
        set_excepts = set(message.get("Excepts"))
        set_excepts = set_excepts.union(net_topo.nids)
        union_excepts = set_excepts.union(set_neighbors)
        if message.get("Receiver"):
            union_excepts.add(utils.get_public_key(message["Receiver"]))

        for ner in set_neighbors:
            if ner not in set_excepts:
                receiver = ner + "@" + net_topo.get_node_dict(ner)["Ip"]
                tcp_logger.info("=== sync to the neighbor: {} ===".format(ner))
                message["Excepts"] = list(union_excepts)
                message["Receiver"] = receiver
                Network.send_msg_with_tcp(receiver, message)

    def resume_channel_from_db(self):
        for pk, wallet in self.wallets.items():
            channels = utils.get_channels_form_db(wallet.url)
            if channels:
                message = MessageMake.make_recover_channel_msg(wallet.url)
                for channel in channels:
                    peer = channel.dest_addr if channel.src_addr == wallet.url else channel.src_addr
                    if utils.get_ip_port(peer) != cg_public_ip_port:
                        Network.send_msg_with_tcp(peer, message)

    def handle_transaction_message(self, data):
        """
        :param data: bytes type
        """
        receiver = data.get("Receiver")
        sender = data.get("Sender")
        asset_type = data.get("MessageBody").get("AssetType")
        receiver_pk = utils.get_public_key(receiver)
        # to spv
        if utils.check_is_spv(receiver):
            Network.send_msg_with_wsocket(self.ws_pk_dict.get(receiver_pk), data)
        # to self's wallet(wallets that attached this gateway)
        else:
            owned, wallet_state = utils.check_is_owned_wallet(receiver, self.wallet_clients)
            if wallet_state:
                # pk = utils.get_public_key(receiver)
                wallet_addr = utils.get_wallet_addr(receiver, self.wallet_clients)
                Network.send_msg_with_jsonrpc("TransactionMessage", wallet_addr, data)
            elif owned:
                # drop this message because the wallet is closed or exit.
                tcp_logger.warn('Drop message because wallet is not on OPENED state.')
                tcp_logger.debug('Drop Message: {}'.format(data))
            # to peer
            else:
                Network.send_msg_with_tcp(receiver, data)

    def _handle_switch_wallets(self, last_pk, magic):
        if not last_pk: return
        for key in self.net_topos:
            net_topo = self.net_topos[key]
            if magic in key and last_pk in net_topo.nids:
                node = net_topo.get_node_dict(last_pk)
                if not node["Status"]: return
                node["Status"] = 0
                sync_node_data_to_peer(node, net_topo)

    def handle_wallet_cli_on_line(self, wallet, last_opened_wallet_pk, magic):
        """
        cli on_line just mean:\n
        the cli call the `open wallet xxx` command\n
        as it may `switch in diffrent wallets` so need check and handle that case\n 
        """
        cli_ip = wallet.cli_ip
        if not len(self.net_topos.keys()):
            ip, port = cli_ip.split(":")
            addr = (ip, int(port))
            Network.send_msg_with_jsonrpc("GetChannelList", addr, {})
        # wallet cli on-line
        
        pk = wallet.public_key
        self.wallet_clients[cli_ip].on_line()
        # self._handle_switch_wallets(last_opened_wallet_pk, magic)
        for key in self.net_topos:
            net_topo = self.net_topos[key]
            if magic in key and net_topo.has_node(pk):
                node = net_topo.get_node_dict(pk)
                if node["Status"]: return
                net_topo.nids.add(pk)
                node["Status"] = 1
                node["Ip"] = cg_public_ip_port
                sync_node_data_to_peer(node, net_topo)

    def handle_wallet_cli_off_line(self, protocol, magic=""):
        """
        cli off_line include these cases:\n
        no.1: the cli program close\n
        no.2: the cli call the `close` command\n
        pk is the public key of wallet_client's (off-line) opened wallet\n
        and the pk may in multi net_topo(every opened wallet has multi asset_type)\n
        so traversal the net_topos and check the wallet is in there or not\n
        """
        # if the cli_ip is none do nothing
        cli_ip = protocol if isinstance(protocol, str) else protocol.wallet_ip
        if not self.wallet_clients.get(cli_ip): return
        pk = self.wallet_clients[cli_ip].off_line()
        del self.wallet_clients[cli_ip]
        # if the client not yet opened wallet do nothing
        if not pk: return
        for key in self.net_topos:
            net_topo = self.net_topos[key]
            # first check the wallet in the net_topo
            if magic in key and pk in net_topo.nids:
                node = net_topo.get_node_dict(pk)
                # check the wallet status is active
                if not node["Status"]: return
                node["Status"] = 0
                sync_node_data_to_peer(node, net_topo)
                net_topo.nids.remove(pk)

    def handle_channel_list_message(self, data):
        if data.get("MessageType") != "GetChannelList": return
        wallet_data = data.get("MessageBody").get("Wallet")
        channel_list = data.get("MessageBody").get("Channel")
        if not wallet_data or not channel_list: return
        wallet, last_opened_wallet_pk, add = WalletClient.add_or_update(
            self.wallet_clients,
            **utils.make_kwargs_for_wallet(wallet_data)
        )
        asset_peers = {}
        # for k in wallet.fee:
        #     asset_peers[k] = []
        for channel in channel_list:
            founder = channel.get("Founder")
            receiver = channel.get("Receiver")
            magic = channel.get("Magic")
            channel_name = channel.get("ChannelName")
            channel_peer = founder if wallet.url == receiver else receiver
            asset_type, channel_balance = list(channel["Balance"][wallet.public_key].items())[0]
            asset_type_magic = "{}-{}".format(asset_type, magic)
            if not asset_peers.get(asset_type_magic):
                asset_peers[asset_type_magic] = []
            asset_peers[asset_type_magic].append((channel_peer, channel_name, channel_balance))
        for key in asset_peers:
            asset_type, magic = key.split("-")
            spv_list = []
            for channel_tuple in asset_peers[key]:
                channel_peer, channel_name, channel_balance = channel_tuple
                wallet.channel_balance[channel_name] = channel_balance
                if utils.check_is_spv(channel_peer):
                    spv_list.append(utils.get_public_key(channel_peer))
                    continue

                owned, wallet_state = utils.check_is_owned_wallet(channel_peer, self.wallet_clients)
                if not owned:
                    message = MessageMake.make_recover_channel_msg(wallet.url, channel_peer, asset_type, magic)
                    Network.send_msg_with_tcp(channel_peer, message)
            if len(wallet.channel_balance.keys()):
                Nettopo.add_or_update(self.net_topos, asset_type, magic, wallet)
                for spv in spv_list:
                    self.net_topos[utils.asset_type_magic_patch(asset_type, magic)].spv_table.add(wallet.public_key, spv)

    
    def notifica_walelt_clis_on_line(self):
        try:
            clis = utils.get_wallet_clis()
        except Exception:
            clis = []
        # clis.append("47.254.39.10:20556")
        for cli in clis:
            try:
                ip, port = cli.split(":")
                addr = (ip, int(port))
            except Exception:
                continue
            else:
                Network.send_msg_with_jsonrpc("GetChannelList", addr, {})

gateway_singleton = Gateway()

def sync_node_data_to_peer(node, net_topo):
    url = node["Publickey"] + "@" + cg_public_ip_port
    message = MessageMake.make_sync_graph_msg(
        "update_node_data",
        url,
        source=url,
        asset_type=node["AssetType"],
        magic=net_topo.magic,
        node=node,
        broadcast=True,
        excepts = list(net_topo.nids)
    )
    gateway_singleton.sync_channel_route_to_peer(message)