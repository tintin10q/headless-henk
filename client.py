from asyncio import gather

import websockets
from typing import Literal
from pprint import pprint
import json
import datetime

from colors import *
from now import now
from parse_order import parse_order, Order
from config import Config, load_config

R = RESET


class Client:
    """
    The place NL client

    Create it by passing a Config object, or don't, and it will try to load a config from config.toml

    Its simple, we receive messages in receive_message and then the handle_message function handles them.

    """

    def __init__(self, config: Config = None):
        if config is None:
            configuration = load_config()
        uri = f"wss://{config.chief_host}/ws"  # Replace with your server's WebSocket endpoint
        self.chief_host = config.chief_host
        self.uri = uri
        self.websocket: websockets.legacy.client.WebSocketClientProtocol | None = None
        self.config: Config = config
        self.current_order: Order | None = None

        # Set after hello has been sent
        # self.id: str = None
        # self.keepaliveTimeout: int = None
        # self.keepaliveInterval: int = None

    async def connect(self):
        async with websockets.connect(self.uri) as websocket:
            # Send a sample 'brand' message to the server
            self.websocket = websocket

            # Receive messages from the server
            await self.receive_messages()
        self.websocket = None

    async def receive_messages(self):
        """ Do the basic parsing of an incoming message, separate type and payload
            handle_message actually does something with the message
        """
        async for message in self.websocket:
            try:
                data = json.loads(message)
                if 'type' not in data:
                    return await self.log_error('invalidPayload', 'noType')
                message_type = data['type']
                payload = data.get("payload", None)
                await self.handle_message(message_type, payload)

            except json.JSONDecodeError:
                await self.log_error('invalidMessage', 'failedToParseJSON')
            except Exception as e:
                print(f"Error processing message: {e}")
                await self.log_error(str(type(e)), str(e))

    async def send_getCapabilities(self):
        print("Received get capabilities message")

    async def send_getOrder(self):
        # Handle the 'getOrder' message
        # Send the 'order' message with the latest orders
        await self.send_message("getOrder")

    async def send_getStats(self):
        # Handle the 'getStats' message
        # Send the 'stats' message with current server statistics
        await self.send_message("getStats")

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

        print(f"{now()} {GREEN}Sending message {BLUE}{message_type}{GREEN} ", end=R)
        pprint(payload)
        await self.websocket.send(json.dumps(message))
        printc(GREEN + f"{now()} {GREEN}Sent message: {R}{message}")

    async def log_error(self, error_type, error_detail):
        """ Log the error, only the server can actually send errors to us """
        print(f"{now()} {RED}Something went wrong: {PURPLE}{error_type}{RED},{PURPLE}{error_detail}{R}")
        # error_message = { 'type': 'error', 'payload': { 'type': error_type, 'detail': error_detail } }
        # print(RED + f"Sending error message: {error_type} with {error_detail}" + R)
        # await self.websocket.send(json.dumps(error_message))

    async def handle_message(self, message_type: str, payload: dict | str | None):
        # Todo remove with : {payload}
        print(BLUE + f"{now()} {BLUE}Received message: {R}{GREEN}{message_type}{R}")  # with: {R}{PURPLE}{payload}{R}")
        match message_type:
            case 'ping':
                await self.handle_pong()
            case 'hello':
                await self.handle_hello(payload)
            case 'brandUpdated':
                print(f"{now()} {GREEN}Brand has been updated successfully!{R}")
            case 'order':
                self.handle_order(payload)
            case 'stats':
                self.handle_stats(payload)
            case 'announcement':
                self.handle_announcement(payload)
            case 'subscribed':
                self.handle_subscribed(payload)
            case 'unsubscribed':
                self.handle_unsubscribed(payload)
            case 'disconnect':
                self.handle_disconnect(payload)
            case 'error':
                print(RED, "Got error from the server!", R, end="")
                pprint(payload)
            case _:
                await self.log_error('invalidPayload', 'unknownType')

    async def handle_hello(self, payload):
        """
        This function should do everything we want to do after we know the connection is here.

        1. Set the brand
        2. Set capabilities
        3. Get the orders

        """
        self.id = payload['id']
        self.keepaliveInterval = payload['keepaliveInterval']
        self.keepaliveTimeout = payload['keepaliveTimeout']
        print(f"{now()} {GREEN}Obtained Client id: {AQUA}{self.id}")

        await self.send_brand()
        await self.send_getOrder()
        await self.send_getStats()

        await gather(self.subscribe_to_announcements(), self.subscribe_to_orders(), self.subscribe_to_stats() if self.config.stats else None)

    async def handle_pong(self):
        await self.send_ping()

    async def send_ping(self):
        await self.send_message('pong')

    def handle_stats(self, payload: dict):
        match payload:

            case {"activeConnections": int(activeConnections), "messagesIn": int(messageIn), "messagesOut": int(messageOut), "date": int(date), "socketConnections": int(socketConnections),
                  "capabilities": {'place': int(place), 'placeNow': int(placenow), 'priorityMappings': int(priorityMappings)}}:
                dt_object = datetime.datetime.fromtimestamp(date / 1000)
                nice_date = dt_object.strftime('%Y %b %d %H:%M:%S')
                print(f"""{PURPLE}--== Server Stats ==--
{GREEN}Time: {AQUA}{nice_date}{RESET}
{GREEN}Incoming  messages: {AQUA}{messageIn}
{GREEN}Outgoing  messages: {AQUA}{messageOut}{RESET}
{GREEN}Socket Connections: {AQUA}{socketConnections}
{GREEN}Active Connections: {AQUA}{activeConnections}
{PURPLE}--== Capability Stats ==--
{GREEN}Able to place: {AQUA}{place}/{activeConnections}{RESET}
{GREEN}Able to place now: {AQUA}{placenow}/{activeConnections}{RESET}
{GREEN}Understands priority mappings: {AQUA}{priorityMappings}/{activeConnections}{RESET}
                """)
            case {"activeConnections": int(activeConnections), "messagesIn": int(messageIn), "messagesOut": int(messageOut), "date": int(date), "socketConnections": int(socketConnections)}:
                dt_object = datetime.datetime.fromtimestamp(date / 1000)
                nice_date = dt_object.strftime('%Y-%d %H:%M:%S')
                print(f"""{PURPLE}--== Stats ==--
{GREEN}Active Connections: {AQUA}{activeConnections}
{GREEN}Socket Connections: {AQUA}{socketConnections}
{GREEN}Incoming  messages: {AQUA}{messageIn}
{GREEN}Outgoing  messages: {AQUA}{messageOut}{RESET}
{GREEN}Date: {AQUA}{RESET}
""")
            case _:
                raise ValueError("Invalid stats message from server")

    def handle_order(self, payload):
        print(f"{now()} {GREEN}Received order{R} 📧")
        self.current_order = parse_order(payload)
        print(self.current_order)

    @staticmethod
    def handle_announcement(payload):
        match payload:
            case {"message": str(message), "important": important}:
                print(f"\n{LIGHTPURPLE}{PURPLE_BG + BLINK + BEEP if important else ''}---=== Chief {'IMPORTANT ' if important else ''}Announcement ===---{R}"
                      f"\n{now()} {message}\n")
            case _:
                print(now(), "Got announcement but couldn't parse it...🤔")
                pprint(payload)
                raise ValueError(f"Could not parse announcement: {payload}")

    async def subscribe_to_announcements(self):
        await self.send_message("subscribe", "announcements")

    async def subscribe_to_orders(self):
        await self.send_message("subscribe", "orders")

    async def subscribe_to_stats(self):
        await self.send_message("subscribe", "stats")

    async def unsubscribe_to_announcements(self):
        await self.send_message("unsubscribe", "announcements")

    async def unsubscribe_to_orders(self):
        await self.send_message("unsubscribe", "orders")

    async def unsubscribe_to_stats(self):
        await self.send_message("unsubscribe", "stats")

    def handle_unsubscribed(self, payload: str):
        print(f"{now()} {RED}Disabled {AQUA}{payload}{RED} subscription{R}")

    def handle_subscribed(self, payload: str):
        print(f"{now()} {GREEN}Enabled {AQUA}{payload}{GREEN} subscription{R}")

    def handle_disconnect(self, payload: dict):
        match payload:
            case {"reason": str(reason), "message": str(message)}:
                print(f"{now()}{RED}We are being disconnected shortly (Code={reason}).{R} {message}")


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
