import asyncio
import sys
from aioconsole import ainput

class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.reader = None
        self.writer = None
        self.message_count = 0

    async def connect(self):
        self.reader, self.writer = await asyncio.open_connection(self.host, self.port)

    async def disconnect(self):
        self.writer.close()
        await self.writer.wait_closed()

    async def send_message(self, message):
        encoded_message = message.encode()
        length = len(encoded_message)
        self.writer.write(struct.pack('!I', length))
        self.writer.write(encoded_message)
        await self.writer.drain()
        self.message_count += 1

    async def receive_message(self):
        while True:
            try:
                length_data = await asyncio.wait_for(self.reader.readexactly(4), timeout=1)
            except (asyncio.IncompleteReadError, asyncio.TimeoutError):
                break
            except asyncio.LimitOverrunError:
                await self.reader.readexactly(self.reader._limit)
                continue
            length = struct.unpack('!I', length_data)[0]
            data = await self.reader.readexactly(length)
            message = data.decode().rstrip()
            print(message)
            self.message_count += 1


    async def handle_send(self):
        while True:
            message = await ainput('')
            await self.send_message(message)
            if self.message_count >= 2:
                await self.disconnect()
                await self.connect()
                self.message_count = 0

    async def handle_receive(self):
        while True:
            await self.receive_message()
            if self.message_count >= 2:
                await self.disconnect()
                await self.connect()
                self.message_count = 0

    async def run(self):
        while True:
            await self.connect()
            try:
                 await asyncio.gather(self.handle_send(), self.handle_receive())
            except:
                 await self.connect()

server = 'x.x.x.x'
port = 30
client = Client(server, port)
asyncio.run(client.run())
