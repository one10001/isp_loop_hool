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
        self.writer.write((message + '\n').encode())
        await self.writer.drain()
        self.message_count += 1

#    async def receive_message(self):
#        data = await self.reader.readline()
#        print(data.decode().rstrip())
#        self.message_count += 1

#    async def receive_message(self):
#        data = await self.reader.read(-1)
#        messages = data.decode().split('\n')
#        for message in messages:
#            if message:  # Ignore empty lines
#                print(message.rstrip())
#                self.message_count += 1
    async def receive_message(self):
        while True:
            try:
                data = await asyncio.wait_for(self.reader.readuntil(b'\n'), timeout=1)
            except (asyncio.IncompleteReadError, asyncio.TimeoutError):
                break
            except asyncio.LimitOverrunError:
                await self.reader.readexactly(self.reader._limit)
                continue
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

server = '141.145.199.199'
port = 30
client = Client(server, port)
asyncio.run(client.run())
