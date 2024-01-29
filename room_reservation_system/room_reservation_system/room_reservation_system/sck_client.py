import asyncio
import websockets

class WebSocketClient:
    def __init__(self, uri):
        self.uri = uri

    async def send_messages(self, message):
        async with websockets.connect(self.uri) as websocket:
            print("Connected to server sending messages")

            await websocket.send(message)

    async def client(self):
        async with websockets.connect(self.uri) as websocket:
            print("Connected to server client")

            # Input loop
            while True:
                user_input = await asyncio.get_event_loop().run_in_executor(None, input, "\nEnter a message (or 'exit' to quit): ")

                if user_input.lower() == 'exit':
                    break

                # Send the user input to the server
                await websocket.send(user_input)

            print("Closing connection")

    async def receive_notifications(self):
        async with websockets.connect(self.uri) as websocket:
            print("Connected to server for receiving notifications")

            try:
                while True:
                    # Receive and print notifications
                    notification = await websocket.recv()
                    print(f"Received notification: {notification}")
            except websockets.exceptions.ConnectionClosedOK:
                print("Server connection closed")

    async def main(self):
        await asyncio.gather(self.client(), self.receive_notifications())

if __name__ == "__main__":
    client = WebSocketClient("ws://localhost:12345")
    asyncio.run(client.main())