import json
import asyncio
import websockets
from channels.generic.websocket import AsyncWebsocketConsumer

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

        # Connect to the external WebSocket server
        uri = "ws://localhost:12345"
        async with websockets.connect(uri) as websocket:
            while True:
                message = await websocket.recv()
                await self.send(text_data=json.dumps({'message': message}))
