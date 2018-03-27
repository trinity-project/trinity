# coding: utf-8
"""
node state manage
"""
import utils
import asyncio


node_list = []

class StatusManage:
    """
    node 状态管理类
    """
    @staticmethod
    def add_node(connection, address):
        node = {
            "con": connection,
            "addr": address
        }
        node_list.append(node)

    @staticmethod
    def remove_node(connection, address):
        node = {
            "con": connection,
            "addr": address
        }
        node_list.remove(node)

    @staticmethod
    def check_node_alive():
        """
        长连接heartbeat检测
        """
        pass
        # bdata = b"hb"
        # for node in node_list:
        #     node["con"].send(bdata)
        # for node in node_list:
        #     try:
        #         reply = node["con"].recv(1024)
        #         if not reply:
        #             # connection broken
        #             Status.remove_node(node["con"], node["addr"])
        #     except timeout:
        #         # timeout except conenction broken
        #         Status.remove_node(node["con"], node["addr"])
    
    @staticmethod
    def sync_node_info(connection):
        connection.send(utils.encode_bytes(node_list))

    @staticmethod
    async def coro():
        await asyncio.sleep(3)
        print("I am the new task")
        return "new task done"