import trio
from trio_websocket import serve_websocket, ConnectionClosed


async def echo_server(request):
    ws = await request.accept()
    while True:
        try:
            await ws.get_message()
        except ConnectionClosed:
            break


async def main():
    await serve_websocket(echo_server, 'localhost', 8000, ssl_context=None)

trio.run(main)
