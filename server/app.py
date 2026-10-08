"""Same-origin static game hosting and isolated authoritative room workers."""
import asyncio
import os
import secrets
import socket
import time
from pathlib import Path
from aiohttp import web, ClientSession, WSMsgType

ROOT = Path(__file__).resolve().parents[1]
rooms = {}
lock = asyncio.Lock()

async def create_room(request):
    try:
        data = await request.json()
        capacity = int(data.get('capacity', 8))
        if capacity not in range(2, 9):
            raise ValueError()
    except (ValueError, TypeError, AttributeError):
        raise web.HTTPBadRequest(text='Capacity must be 2 through 8')
    async with lock:
        if len(rooms) >= 8:
            raise web.HTTPServiceUnavailable(text='All rooms occupied')
        code = secrets.token_hex(3).upper()
        while code in rooms:
            code = secrets.token_hex(3).upper()
        with socket.socket() as sock:
            sock.bind(('127.0.0.1', 0))
            port = sock.getsockname()[1]
        process = await asyncio.create_subprocess_exec(
            os.environ.get('GODOT_BIN', 'godot'), '--headless', '--audio-driver', 'Dummy',
            '--path', str(ROOT / 'godot'), '--script', 'three_d/dedicated_server.gd',
            '--', str(port), str(capacity), stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT)
        async def ready():
            while line := await process.stdout.readline():
                if b'RESERKA_ROOM_READY' in line:
                    return
            raise RuntimeError('Room worker failed')
        try:
            await asyncio.wait_for(ready(), 30)
        except (TimeoutError, RuntimeError):
            if process.returncode is None:
                process.terminate()
            await process.wait()
            raise web.HTTPServiceUnavailable(text='Room failed to start')
        async def drain():
            while line := await process.stdout.readline():
                print("room", code, line.decode(errors="replace").rstrip(), flush=True)
        rooms[code] = {'process': process, 'port': port, 'last': time.monotonic(),
                       'connections': 0, 'drain': asyncio.create_task(drain())}
    return web.json_response({'code': code, 'socket': f'/rooms/{code}/socket'})

async def find_room(request):
    code = request.match_info['code'].upper()
    room = rooms.get(code)
    if not room or room['process'].returncode is not None:
        raise web.HTTPNotFound(text='Room expired or unknown')
    return web.json_response({'code': code, 'socket': f'/rooms/{code}/socket'})

async def proxy(request):
    code = request.match_info['code'].upper()
    room = rooms.get(code)
    if not room or room['process'].returncode is not None:
        raise web.HTTPNotFound()
    # Godot's WebSocket multiplayer protocol negotiates the binary subprotocol.
    protocols = tuple(x.strip() for x in request.headers.get('Sec-WebSocket-Protocol', '').split(',') if x.strip())
    async with ClientSession() as client:
        async with client.ws_connect(f"http://127.0.0.1:{room['port']}", protocols=protocols) as upstream:
            downstream = web.WebSocketResponse(protocols=protocols, max_msg_size=1024*1024)
            await downstream.prepare(request)
            room['connections'] += 1
            async def relay(source, target):
                async for message in source:
                    room['last'] = time.monotonic()
                    if message.type == WSMsgType.BINARY:
                        await target.send_bytes(message.data)
                    elif message.type == WSMsgType.TEXT:
                        await target.send_str(message.data)
                    else:
                        break
            tasks = [asyncio.create_task(relay(downstream, upstream)),
                     asyncio.create_task(relay(upstream, downstream))]
            try:
                await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
            finally:
                for task in tasks:
                    task.cancel()
                await asyncio.gather(*tasks, return_exceptions=True)
                room['connections'] -= 1
                room['last'] = time.monotonic()
                await downstream.close()
            return downstream

async def lifecycle(app):
    async def reap():
        while True:
            await asyncio.sleep(15)
            for code, room in list(rooms.items()):
                if room['process'].returncode is not None or (room['connections'] == 0 and time.monotonic()-room['last'] > 1200):
                    if room['process'].returncode is None:
                        room['process'].terminate()
                    await room['process'].wait()
                    del rooms[code]
    task = asyncio.create_task(reap())
    yield
    task.cancel()
    await asyncio.gather(task, return_exceptions=True)
    for room in rooms.values():
        if room['process'].returncode is None:
            room['process'].terminate()
        await room['process'].wait()

app = web.Application(client_max_size=4096)
app.cleanup_ctx.append(lifecycle)
app.router.add_post('/api/rooms', create_room)
app.router.add_get('/api/rooms/{code}', find_room)
app.router.add_get('/rooms/{code}/socket', proxy)
app.router.add_get('/', lambda request: web.FileResponse(ROOT / 'web/index.html'))
app.router.add_static('/', ROOT / 'web', show_index=False)
if __name__ == '__main__':
    web.run_app(app, host=os.environ.get('HOST', '0.0.0.0'), port=int(os.environ.get('PORT', '8080')))
