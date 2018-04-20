# coding: utf-8
import json
import time
import asyncio
from aiohttp import web, ClientSession
from jsonrpcserver.aio import methods
from jsonrpcclient.aiohttp_client import aiohttpClient
from config import cg_local_jsonrpc_addr, cg_remote_jsonrpc_addr
from glog import rpc_logger

@methods.add
async def ShowNodeList(params):
    from gateway import gateway_singleton
    return gateway_singleton.handle_jsonrpc_request('ShowNodeList', params)

@methods.add
async def JoinNet(params):
    from gateway import gateway_singleton
    return gateway_singleton.handle_jsonrpc_request('JoinNet', params)

@methods.add
async def SyncWalletData(params):
    from gateway import gateway_singleton
    return gateway_singleton.handle_jsonrpc_request('SyncWalletData', params)

@methods.add
async def SyncChannel(params):
    from gateway import gateway_singleton
    return gateway_singleton.handle_jsonrpc_request('SyncChannel', params)

@methods.add
async def SyncBlock(params):
    from gateway import gateway_singleton
    return gateway_singleton.handle_jsonrpc_request('SyncBlock', params)

@methods.add
async def TransactionMessage(params):
    from gateway import gateway_singleton
    return gateway_singleton.handle_jsonrpc_request('TransactionMessage', params)

@methods.add
async def GetRouterInfo(params):
    from gateway import gateway_singleton
    return gateway_singleton.handle_jsonrpc_request('GetRouterInfo', params)

class AsyncJsonRpc():
    @staticmethod
    async def handle(request):
        request = await request.text()
        # print(request)
        response = await methods.dispatch(request)
        if response.is_notification:
            return web.Response()
        else:
            return web.json_response(response, status=response.http_status)

    @staticmethod
    async def start_jsonrpc_serv():
        app = web.Application()
        app.router.add_post('/', AsyncJsonRpc.handle)
        loop = asyncio.get_event_loop()
        server = await loop.create_server(app.make_handler(), cg_local_jsonrpc_addr[0], cg_local_jsonrpc_addr[1])
        rpc_logger.info("RPC server is serving on %s", cg_local_jsonrpc_addr)
        return server
        # web.run_app(app, host=cg_local_jsonrpc_addr[0], port=cg_local_jsonrpc_addr[1])
        
    @staticmethod
    async def jsonrpc_request(loop, method, params):
        async with ClientSession(loop=loop) as session:
            endpoint = 'http://' + cg_remote_jsonrpc_addr[0] + ":" + str(cg_remote_jsonrpc_addr[1])
            # endpoint = 'http://106.15.91.150:20556'
            client = aiohttpClient(session, endpoint)
            start_time = time.time()
            response = await client.request(method, params)
            ttl = time.time() - start_time
            print("++++++++gateway<----->wallet spend time{}+++++++++".format(ttl))
            from gateway import gateway_singleton
            gateway_singleton.handle_jsonrpc_response(method, response)

if __name__ == "__main__":
    message = {
        "MessageType": "FounderSign"
    }
    asyncio.get_event_loop().run_until_complete(
        AsyncJsonRpc.jsonrpc_request(asyncio.get_event_loop(), "TransactionMessage", message)
    )
    # AsyncJsonRpc.start_jsonrpc_serv()