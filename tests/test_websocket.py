import asyncio
import websockets

async def test_ws():
    uri = "ws://127.0.0.1:8000/api/v1/tickers/ws"
    async with websockets.connect(uri) as websocket:
        print("WebSocket connected!")
        response = await websocket.recv()
        print("Received:", response)

asyncio.run(test_ws())