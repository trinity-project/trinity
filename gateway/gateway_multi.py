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
                public_key=body.get("Publickey"),
                name=body.get("alias"),
                deposit=body.get("CommitMinDeposit"),
                fee=body.get("Fee"),
                asset_type=list(body.get("Balance").items())[0][0],
                balance=list(body.get("Balance").items())[0][1]
            )
            url = self.wallets.get(body.get("Publickey")).url
            response = MessageMake.make_ack_sync_wallet_msg(url)
            return json.dumps(response)
        elif method == "TransactionMessage":
            if msg_type == "RegisterChannel":
                rev_ip_port = utils.get_ip_port(data.get("Receiver"))
                rev_pk = utils.get_public_key(data.get("Receiver"))
                
    gateway_singleton = Gateway()