# coding: utf-8
import asyncio
from aiohttp import web, ClientSession
from jsonrpcserver.aio import methods
from jsonrpcclient.aiohttp_client import aiohttpClient
from jsonrpcclient.http_client import HTTPClient
from glog import rpc_logger

@methods.add
async def ShowNodeList(params):
    from gateway import gateway_singleton
    return gateway_singleton.handle_wallet_request('ShowNodeList', params)

@methods.add
async def JoinNet(params):
    from gateway import gateway_singleton
    return gateway_singleton.handle_wallet_request('JoinNet', params)

@methods.add
async def Search(params):
    from gateway import gateway_singleton
    return gateway_singleton.handle_wallet_request('Search', params)

@methods.add
async def SyncWalletData(params):
    from gateway import gateway_singleton
    return gateway_singleton.handle_wallet_request('SyncWalletData', params)

@methods.add
async def SyncChannel(params):
    from gateway import gateway_singleton
    return gateway_singleton.handle_wallet_request('SyncChannel', params)

@methods.add
async def SyncBlock(params):
    from gateway import gateway_singleton
    return gateway_singleton.handle_wallet_request('SyncBlock', params)

@methods.add
async def TransactionMessage(params):
    from gateway import gateway_singleton
    return gateway_singleton.handle_wallet_request('TransactionMessage', params)

@methods.add
async def GetRouterInfo(params):
    from gateway import gateway_singleton
    return gateway_singleton.handle_wallet_request('GetRouterInfo', params)

@methods.add
async def CloseWallet(params):
    from gateway import gateway_singleton
    return gateway_singleton.handle_wallet_request("CloseWallet", params)
    
class AsyncJsonRpc():
    @staticmethod
    async def handle(request):
        request = await request.text()
        response = await methods.dispatch(request)
        if response.is_notification:
            return web.Response()
        else:
            return web.json_response(response, status=response.http_status)

    @classmethod
    async def create_server_coro(cls, addr):
        """
        the coro for create jsonrpc server\n
        return an instance of asyncio Server 
        """
        app = web.Application()
        app.router.add_post('/', cls.handle)
        loop = asyncio.get_event_loop()
        server = await loop.create_server(app.make_handler(), addr[0], addr[1])
        rpc_logger.info("RPC server is serving on %s", addr)
        return server
        # web.run_app(app, host=cg_local_jsonrpc_addr[0], port=cg_local_jsonrpc_addr[1])
        
    @staticmethod
    async def jsonrpc_request(method, params, addr):
        async with ClientSession() as session:
            endpoint = 'http://' + addr[0] + ":" + str(addr[1])
            client = aiohttpClient(session, endpoint)
            rpc_logger.info("--> send msg to wallet_cli{}".format(addr))
            response = await client.request(method, params)
            from gateway import gateway_singleton
            gateway_singleton.handle_wallet_response(method, response)

    @staticmethod
    def jsonrpc_request_sync(method, params, addr):
        try:
            endpoint = 'http://' + addr[0] + ":" + str(addr[1])
            client = HTTPClient(endpoint)
            rpc_logger.info("--> sender to {}\n : {}".format(addr,params))
            res = client.request(method, params)
            rpc_logger.info("<-- receiver from {}\n : {}".format(addr,res))
        except Exception as e:
            res = None
        finally:
            return res

if __name__ == "__main__":
    addr = ("0.0.0.0", 8077)
    import json
    AsyncJsonRpc.jsonrpc_request_sync("Search", json.dumps({}), addr)
    # message = {
    #     "MessageType": "FounderSign"
    # }
    # asyncio.get_event_loop().run_until_complete(
    #     AsyncJsonRpc.jsonrpc_request(asyncio.get_event_loop(), "TransactionMessage", message)
    # )
    # AsyncJsonRpc.start_jsonrpc_serv()