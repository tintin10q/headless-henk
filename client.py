from pprint import pprint
from typing import Literal

from config import Config, load_config
import websockets

from colors import *
import json
from dataclasses import dataclass

R = RESET

class Client:
    def __init__(self, config: "Config" = None):
        if config is None:
            config = load_config()
        uri = f"wss://{config.chief_host}/ws"  # Replace with your server's WebSocket endpoint
        self.chief_host = config.chief_host
        self.uri = uri
        self.websocket: websockets.legacy.client.WebSocketClientProtocol = None
        self.config: Config = config

        # Set after hello has been send
        self.id : str = None
        self.keepaliveTimeout: int = None
        self.keepaliveInterval: int = None

    async def connect(self):
        async with websockets.connect(self.uri) as websocket:
            # Send a sample 'brand' message to the server
            self.websocket = websocket

            # Receive messages from the server
            await self.receive_messages()
        self.websocket = None

    async def receive_messages(self):
        async for message in self.websocket:
            try:
                data = json.loads(message)
                if 'type' not in data:
                    return await self.send_error('invalidPayload', 'noType')
                message_type = data['type']
                payload = data.get("payload", None)
                await self.handle_message(message_type, payload)
            except json.JSONDecodeError:
                await self.send_error('invalidMessage', 'failedToParseJSON')
            except Exception as e:
                print(f"Error processing message: {e}")
                await self.send_error('unknownError', str(e))

    async def send_getCapabilities(self):
        print("Received get capabilities message")

    async def send_getOrder(self):
        # Handle the 'getOrder' message
        # Send the 'order' message with the latest orders
        print("Received 'getOrder' message")

    async def send_getStats(self):
        # Handle the 'getStats' message
        # Send the 'stats' message with current server statistics
        print("Received 'getStats' message")

    async def send_unsubscribe(self, payload):
        print("got get unsubscribe")

    async def send_subscribe(self, payload):
        print("got get subscription message")

    async def send_getSubscriptions(self):
        print("get subscriptions")

    async def send_disable_capability(self, payload):
        print("disable capability")

    async def send_brand(self):
        # Handle the 'brand' message
        # Validate the brand information and send 'brandUpdated' or 'invalidPayload' error
        brand = self.config.get_brand_payload()
        await self.send_message('brand', brand)

    async def send_message(self, message_type: Literal['pong', 'brand', 'getOrder', 'getStats', 'getCapabilities', 'enableCapability', 'disableCapability', 'getSubscriptions', 'subscribe', 'unsubscribe'], payload=None):
        message = {'type': message_type}

        if payload is not None:
            message['payload'] = payload
            print(YELLOW, "added payload", R)

        printgreen(f"Sending {message_type} message:", STOP, PURPLE, payload)
        await self.websocket.send(json.dumps(message))
        printc(YELLOW + f"Sent message: {R}{message}")

    async def send_error(self, error_type, error_detail):
        error_message = {
            'type': 'error',
            'payload': {
                'type': error_type,
                'detail': error_detail
            }
        }

        print(RED+ f"Sending error message: {error_type} with {error_detail}" + R)

        await self.websocket.send(json.dumps(error_message))

    async def handle_message(self, message_type: str, payload: dict | None):
        print(BLUE + f"handle message got: {R}{GREEN}{message_type}{BLUE} with: {R}{PURPLE}{payload}{R}")
        match message_type:
            case 'ping':
                await self.handle_pong()
            case 'hello':
                await self.handle_hello(payload)
            case 'brandUpdated':
                printc(GREEN, "Brand has been updated!")
            case 'error':
                print(RED, "Got error from the server!", R, end="")
                pprint(payload)
            case _:
                await self.send_error('invalidPayload', 'unknownType')

    async def handle_hello(self, payload):
        self.id = payload['id']
        self.keepaliveInterval = payload['keepaliveInterval']
        self.keepaliveTimeout = payload['keepaliveTimeout']

        await self.send_brand()

    async def handle_pong(self):
        await self.send_ping()

    async def send_ping(self):
        await self.send_message('pong')


def check_connected(self, method):
    if self.websocket is None:
        raise ValueError(f"Not connected to {self.host} call connect first")


# === Add colors.py to path ===
import sys
import os

# Assuming 'colors.py' is located in the same directory as 'side_package'
# If it's in a different location, provide the correct path accordingly.
colors_file_path = os.path.join(os.path.dirname(__file__), '../colors.py')

if colors_file_path not in sys.path:
    sys.path.insert(0, colors_file_path)
