# socat -d -d -v pty,rawer,echo=0,link=./reader pty,rawer,echo=0,link=./writer

import asyncio
import serial_asyncio
from websockets.server import serve
from queue import Queue

ws2ser = Queue()
ser2ws = Queue()
g_websocket = None


async def send_ws():
    global g_websocket
    while True:
        if ser2ws.qsize() > 0:
            msg = ser2ws.get()  # get_nowait
            print("send_ws msg: ", msg)
            await g_websocket.send(msg)
        await asyncio.sleep(0.01)


async def read_ws(websocket):
    global g_websocket
    g_websocket = websocket
    async for message in websocket:
        print(f"read_ws: {message}")
        ws2ser.put(message)


async def send_ser(writer):
    while True:
        if ws2ser.qsize() > 0:
            msg = ws2ser.get()  # get_nowait
            print("send_ser: ", msg)
            writer.write(bytearray(msg, 'utf-8'))
        await asyncio.sleep(0.01)


async def recv_ser(reader):
    while True:
        msg = await reader.readline() # .readuntil(b'\n')
        ser2ws.put(msg)
        print(f'recv_ser: {msg}')
        await asyncio.sleep(0.01)


async def main():
    print('starting')
    reader, writer = await serial_asyncio.open_serial_connection(url='./reader', baudrate=115200)
    print('serial connected')
    await asyncio.gather(
        send_ser(writer),
        recv_ser(reader),
        serve(read_ws, "localhost", 8765),
        send_ws()
    )
    print('asynced')
    # async with serve(read_ws, "localhost", 8765):
    #     await asyncio.Future()  # run forever


asyncio.run(main())
