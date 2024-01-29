import asyncio
import websockets

async def client():
    uri = "ws://localhost:12345"  # Replace with your server's host and port

    async with websockets.connect(uri) as websocket:
        print("Connected to server")

        # Input loop
        while True:
            user_input = await asyncio.get_event_loop().run_in_executor(None, input, "\nEnter a message (or 'exit' to quit): ")

            if user_input.lower() == 'exit':
                break

            # Send the user input to the server
            await websocket.send(user_input)

        print("Closing connection")

async def receive_notifications():
    uri = "ws://localhost:12345"  # Replace with your server's host and port

    async with websockets.connect(uri) as websocket:
        print("Connected to server for receiving notifications")

        try:
            while True:
                # Receive and print notifications
                notification = await websocket.recv()
                decoded_notification = notification.decode()
                print(f"Received notification: {decoded_notification}")
        except websockets.exceptions.ConnectionClosedOK:
            print("Server connection closed")

async def main():
    await asyncio.gather(client(), receive_notifications())

if __name__ == "__main__":
    asyncio.run(main())
