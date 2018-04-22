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
            "HtlcFail"
        ]
        return tx_types
    
    # classmethods
    @classmethod
    def get_valid_msg_types(cls):
        """
        :return: all valid message type between nodes
        """
        valid_types = [
            "RegisterChannel",
            "SyncChannelState",
            "ResumeChannel"
        ]
        valid_types = valid_types + cls.get_tx_msg_types()
        return valid_types

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
    def make_trigger_transaction_msg(cls, **kwargs):
        """
        :param kwargs:\n
        "sender": "xxx@yyy"\n
        "receiver": "xxx@yyy"\n
        "asset_type": "TNC/ETH/",\n
        "amount": 4
        """
        message = {
            "Sender": kwargs.get("sender"),
            "MessageType": "CreateChannelMessage",
            "Receiver": kwargs.get("receiver)",
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
    def make_ack_sync_wallet_msg(url):
        message = {
            "MessageType": "AckSyncWallet",
            "MessageBody": {
                "Url": url
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
    
    ###### message for spv end ########

    ###### message for node begin ########
    @staticmethod
    def make_resume_channel_msg(sender):
        message = {
            "MessageType": "ResumeChannel",
            "Sender": sender
        }
        return message

    @staticmethod
    def make_sync_graph_msg(sync_type, sender, **kwargs):
        """
        :param sync_type: "add_single_edge|remove_single_edge|update_node_data|add_whole_graph"\n
        :param kwargs: {route_graph,source,target,node}
        """
        message = {
            "MessageType": "SyncChannelState",
            "SyncType": sync_type,
            "Sender": sender,
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
    def make_error_msg(**kwargs):
        message = {
            "Sender": kwargs.get("sender"),
            "Receiver": kwargs.get("receiver"),
            "MessageType": "ErrorMessage",
            "Reason": kwargs.get("reason")
        }
        return message