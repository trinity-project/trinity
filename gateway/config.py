# coding: utf-8
"""
node gateway config module \n
every variable in this config module start as 'cg'
"""

###### Common ######
# tcp end of file don't modify
cg_end_mark = "/eof/"
cg_bytes_encoding = "utf-8"
###### Common ######


###### Gateway ######
cg_tcp_addr = ("0.0.0.0", 8093)
cg_wsocket_addr = ("0.0.0.0", 8770)
cg_local_jsonrpc_addr = ("0.0.0.0", 8081)
cg_remote_jsonrpc_addr = ("0.0.0.0", 20556)
cg_public_ip_port = "localhost:8093"
cg_node_name = "trinity1"
###### Gateway ######

# only for debug control
cg_debug = True