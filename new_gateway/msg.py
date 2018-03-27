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


