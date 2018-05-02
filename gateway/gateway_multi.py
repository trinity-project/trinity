# coding: utf-8
import pprint
import os
import json
import utils
from wallet import Wallet
from routertree import SPVHashTable
from routergraph import RouterGraph
from network import Network
from message import Message, MessageMake
from glog import tcp_logger, wst_logger
from config import cg_public_ip_port

class Gateway():
    """
    gateway class
    """
    def __init__(self):
        # the wallet dict
        self.wallets = {}
        self.pk_ws = {}
        self.pk_tcp = {}

    def start(self):
        Network.create_servers()
        print("###### Trinity Gateway Start Successfully! ######")
        Network.run_servers_forever()

    def clearn(self):
        Network.clearn_servers()

    def close(self):
        Network.loop.close()
        print("###### Trinity Gateway Closed ######")

    def handle_node_request(self, protocol, bdata):
        pass

    def handle_spv_request(self, websocket, strdata):
        pass

    def handle_wallet_request(self, method, params):
        data = params
        if type(data) == str:
            data = json.loads(data)
        msg_type = data.get("MessageType")
        if method == "SyncWalletData":
            print("Get the wallet sync data\n", data)
            body = data.get("MessageBody")
            Wallet.add_or_update_wallet(
                self.wallets,
                **utils.make_kwargs_for_wallet(body)
            )
            url = self.wallets.get(body.get("Publickey")).url
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
            channel_peer = utils.select_channel_peer(channel_founder, channel_receiver, self.wallets)
            channel_self = channel_founder if channel_peer == channel_receiver else channel_receiver
            asset_type = data["MessageBody"]["Balance"][channel_self]
            router_graph = self.wallets.get(utils.get_public_key(channel_self)).assets.get(asset_type).router_graph
            if msg_type == "AddChannel":
                message = MessageMake.make_sync_graph_msg(
                    "add_whole_graph",
                    channel_self,
                    source=channel_self,
                    target=channel_peer,
                    route_graph=router_graph,
                    broadcast=True,
                    excepts=[channel_founder, channel_receiver]
                )
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