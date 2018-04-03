# coding: utf-8
"""
消息类型主要分三大类：
1.gateway<-->gateway  GG开头
2.gateway--->wallet   GW开头
3.gateway<--->spv     GS开头
消息样例
{
    type: 0x000001
    body: ........
}
{
    type: 0x000002
    body: ........
}
"""
# GG 类型消息
GG_JOIN_NET = 0x1001
GG_TRADE = 0x1002
GG_NET_TOP_CHANGED = 0x1003
GG_HB = 0x1004
GG_ALIVE = 0x1005

# GW 类型消息
GW_TRADE = 0x2001

# GS 类型消息
GS_TRADE_REQUEST = 0x3001
GS_PUSH_TRADE_INFO = 0x3002


# msg bettwin node
join_msg = {
    "MessageType": "JoinNet",
    "Sender":"03dc2841ddfb8c2afef94296693315a234026fa8f058c3e4259a04f8be6d540049@11.11.11.11:2222",
    "Receiver":"03dc2841ddfb8c2afef94296693315a234026fa8f058c3e4259a04f8be6d540049@11.11.11.11:2222",
    # "MessageBody": {
    #     "Asstes":"TNC",
    #     "Deposit":"100"
    # }
}

ack_join_msg = {
    "MessageType": "AckJoinNet",
    "Sender":"03dc2841ddfb8c2afef94296693315a234026fa8f058c3e4259a04f8be6d540049@11.11.11.11:2222",
    "Receiver":"03dc2841ddfb8c2afef94296693315a234026fa8f058c3e4259a04f8be6d540049@11.11.11.11:2222",
    "WebList": [
        "03dc2841ddfb8c2afef94296693315a234026fa8f058c3e4259a04f8be6d540049@11.11.11.11:2222"
    ]
}


# push spv msg type
msg = {
    "type": "block_info",
    "body": {
        "content": "This is a push message triggered by timer",
        "blance": random.randint(1000, 9000)
    }
}

msg = {
    "type": "sync_state",
    "body": {
        "content": "This is a push message triggered by peer state changed",
        "state": "other spv disconnectioned"
    }
}

# spv msg AddChannel
msg = {
    "MessageType": "AddChannel",
    "Sender":"03dc2841ddfb8c2afef94296693315a234026fa8f058c3e4259a04f8be6d540049@11.11.11.11:2222",
    "Receiver":"03dc2841ddfb8c2afef94296693315a234026fa8f058c3e4259a04f8be6d540049@11.11.11.11:2222",
    "MessageBody": {
        "Asstes":"TNC",
        "Deposit":"100"
    }
}

message = {
    "MessageType":"SyncWallet",
    "MesssgeBody":{
        "Publickey":publickey,
        "CommitMinDeposit":Configure["Channel"]["CommitMinDeposit"]
        "Fee":Configure["Fee"]
    }
}

SyncChannel = {
    "MessageType":"SyncChannel",
    "Self": "url"
    "Peers": {
        "Url": "url",
        "CommitMinDeposit",
        "Name": 
        "Fee"
    }
    "Action": "add/remove"
}