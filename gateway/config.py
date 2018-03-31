# coding: utf-8
"""
node 节点配置文件
该模块下的所有变量以cg开头
"""

###### Common ######

# tcp数据结束标识符
cg_end_mark = "eof"
# tcp从socket读取数据包的缓存大小 字节单位
cg_tcp_buffersize = 1024

###### Common ######


###### Gateway ######

# 设置socket连接wallet的超时 单位秒
# cg_connect_wallet_timeout = 5.0
# 发生超时的情况socket连接wallet的最多次数
# cg_try_connect_wallet_times = 3
cg_tcp_addr = ("0.0.0.0", 8089)
cg_wsocket_addr = ("0.0.0.0", 8766)
cg_local_jsonrpc_addr = ("0.0.0.0", 8077)
cg_remote_jsonrpc_addr = ("0.0.0.0", 5001)
cg_public_ip_port = "106.15.91.150:8089"
###### Gateway ######


###### Wallet ######

# wallet曝露给gateway的通信端口
cg_wg_port = 8088
# wallet允许待处理gateway数量
cg_wg_backlog = 5

###### Wallet ######

cg_debug = False
seed = True