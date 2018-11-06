# coding: utf-8
"""
the mudule for  message
"""

class Message:
    """
    the class for message
    """
    # staticmethods
    @staticmethod
    def get_tx_msg_types():
        """
        :return: all transaction msg type
        """
        tx_types = [
            "Rsmc",
            "FounderSign",
            "Founder",
            "RsmcSign",
            "FounderFail",
            "Settle",
            "SettleSign",
            "SettleFail",
            "RsmcFail",
            "Htlc",
            "HtlcSign",
            "HtlcFail",
            "RResponseAck",
            "RResponse",
            "RegisterChannelFail"
        ]
        return tx_types
    
    @staticmethod
    def get_payment_msg_types():
        """
        :return: all payment msg type
        """
        payment_types = [
            "PaymentLinkAck", 
            "PaymentAck"
        ]
        return payment_types

    # classmethods
    @classmethod
    def get_valid_msg_types(cls):
        """
        :return: all valid message type between nodes
        """
        valid_types = [
            "RegisterChannel",
            "RegisterKeepAlive",
            "SyncChannelState",
            "ResumeChannel"
        ]
        valid_types = valid_types + cls.get_tx_msg_types()
        return valid_types

    @classmethod
    def check_message_is_valid(cls, data, origin="node"):
        """
        :param data: dict type \n
        :param origin: node|wallet|spv
        """
        is_valid = True
        msg_type = data.get("MessageType")
        if type(data) != dict:
            is_valid = False
        elif not msg_type:
            is_valid = False
        if origin == "node" and msg_type != "RegisterKeepAlive":
            if msg_type not in cls.get_valid_msg_types():
                is_valid = False
            elif not data.get("Sender"):
                return False
        return is_valid


class MessageMake:
    """
    the class for make message
    """
    @staticmethod
    def _make_common_msg_head(**kwargs):
        message = {}
        for param_name, param_value in kwargs.items():
            message[param_name] = param_value
        return message
    ###### message for wallet begin ########
    @classmethod
    def make_trigger_transaction_msg(cls, msg_type="CreateChannelMessage", **kwargs):
        """
        :param kwargs: \n
        "sender": xxx@yyy \n
        "receiver": xxx@yyy \n
        "asset_type": TNC/ETH/, \n
        "amount": 4
        """
        message = {
            "Sender": kwargs.get("sender"),
            "MessageType": msg_type,
            "Receiver": kwargs.get("receiver"),
            "MessageBody": {
                "AssetType": kwargs.get("asset_type"),
                "Value": kwargs.get("amount")
            }
        }
        message.update(
            cls._make_common_msg_head(
                Sender=kwargs.get("sender"), 
                Receiver=kwargs.get("receiver")
            )
        )
        return message

    @staticmethod
    def make_search_target_wallet(spv_pk, asset_type, magic):
        message= {
            "MessageType": "SearchWallet",
            "AssetType": asset_type,
            "NetMagic": magic,
            "Publickey": spv_pk
        }
        return message

    @staticmethod
    def make_ack_search_target_wallet(wallet_pks):
        message= {
            "MessageType": "AckSearchWallet",
            "Wallets": wallet_pks
        }
        return message

    @staticmethod
    def make_ack_search_spv(data):
        message= {
            "MessageType": "AckSearchSpv",
            "Wallets": data
        }
        return message

    @staticmethod
    def make_join_net_msg(sender):
        message = {
            "MessageType": "JoinNet",
            "Sender": sender
        }
        return message

    @staticmethod
    def make_ack_show_node_list(node_list):
        message = {
            "MessageType": "AckShowNodeList",
            "NodeList": list(node_list)
        }
        return message
    
    @staticmethod
    def make_ack_sync_wallet_msg(url, spv_ip_port):
        message = {
            "MessageType": "AckSyncWallet",
            "MessageBody": {
                "Url": url,
                "Spv": spv_ip_port
            }
        }
        return message
    ###### message for wallet end ########

    ###### message for spv begin ########
    @staticmethod
    def make_node_list_msg(channel_graph):
        message = {
            "MessageType": "NodeList",
            "Nodes": channel_graph.to_json()
        }
        return message
    
    @staticmethod
    def make_ack_channel_info(peers):
        message = {
            "MessageType": "ChannelInfo",
            "Peers": peers
        }
        return message
    ###### message for spv end ########

    ###### message for node begin ########
    @staticmethod
    def make_recover_channel_msg(sender, receiver, asset_type, magic):
        message = {
            "MessageType": "ResumeChannel",
            "AssetType": asset_type,
            "NetMagic": magic,
            "Sender": sender,
            "Receiver": receiver
        }
        return message

    @staticmethod
    def make_ack_node_join_msg(sender, receiver, node_list):
        message = {
            "MessageType": "AckJoin",
            "Sender": sender,
            "Receiver": receiver,
            "NodeList": list(node_list)
        }
        return message

    @staticmethod
    def make_sync_graph_msg(sync_type, sender, msg_type="SyncChannelState" ,**kwargs):
        """
        :param sync_type: add_single_edge|remove_single_edge|update_node_data|add_whole_graph \n
        :param kwargs: {route_graph,source,target,node,broadcast,excepts}
        """
        message = {
            "MessageType": msg_type,
            "SyncType": sync_type,
            "Sender": sender,
            "AssetType": kwargs.get("asset_type"),
            "NetMagic": kwargs.get("magic"),
            "Broadcast": kwargs.get("broadcast"),
            "Source": kwargs.get("source"),
            "Target": kwargs.get("target"),
            "Excepts": kwargs.get("excepts")
        }
        if sync_type == "add_whole_graph":
            message["MessageBody"] = kwargs["route_graph"].to_json()
        elif sync_type == "add_single_edge":
            pass
        elif sync_type == "remove_single_edge":
            pass
        elif sync_type == "update_node_data":
            message["MessageBody"] = kwargs["node"]
        return message
    ###### message for node end ########

    @staticmethod
    def make_ack_router_info_msg(router):
        message = {
            "MessageType": "AckRouterInfo",
            "RouterInfo": router
        }
        return message

    @staticmethod
    def make_error_msg(msg_type="ErrorMessage", **kwargs):
        """
        :param kwargs: \n
        sender: "xxx@yyy" \n
        receiver: "xxx@yyy" \n
        reason: the description about error
        """
        message = {
            "Sender": kwargs.get("sender"),
            "Receiver": kwargs.get("receiver"),
            "MessageType": msg_type,
            "Reason": kwargs.get("reason")
        }
        return message