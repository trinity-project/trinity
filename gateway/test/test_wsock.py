import asyncio
import websockets

def select_db():
    return "db result"

async def select_task(websocket):
    while True:
        await asyncio.sleep(15)
        data = select_db()
        if data == "db result":
            asyncio.ensure_future(push_task(websocket, data))
            break

async def push_task(websocket, msg):
    await websocket.send(msg)

async def handle(con, path):
    """
    处理所有来自客户端的websocket请求
    """
    # every client first connected the server
    print('client {} conected'.format(con.remote_address))
    while True:
        try:
            message = await con.recv()
            print(message)
            if message == "txid":
                asyncio.ensure_future(select_task(con))            
        except websockets.exceptions.ConnectionClosed:
            print('client {} disconected'.format(con.remote_address))
            break

serv_coro = websockets.serve(
    handle,
    "localhost",
    8677
)
loop = asyncio.get_event_loop()
wsocket_server = loop.run_until_complete(serv_coro)
loop.run_forever()