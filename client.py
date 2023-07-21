import asyncio
from asyncio import gather

import websockets
from typing import Literal
from pprint import pprint
import json
import datetime
import threading
import random

import canvas
import images
import reddit
from colors import *
from now import now
from parse_order import parse_order, Order, Image
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
        self.differences = []

        self.place_cooldown = 0
        self.can_place = False

        # Set after hello has been sent
        self.id: str | None = None
        self.keepaliveTimeout: int | None = None
        self.keepaliveInterval: int | None = None

        self.place_timer: threading.Timer | None = None
        self.pong_timer: threading.Timer | None = None

        self.order_image: Image | None

    async def connect(self):
        printc(f"{now()} {GREEN}Checking reddit token...")

        self.place_cooldown = reddit.get_place_cooldown(self.config.auth_token)
        self.can_place = self.place_cooldown is not None  # If this is none the token is not valid

        if not self.can_place:
            printc(f"{now()} {RED}This reddit jwt token can not place pixels!")
            exit(0)

        async with websockets.connect(self.uri) as websocket:
            # Send a sample 'brand' message to the server
            self.websocket = websocket

            # Receive messages from the server
            await self.receive_messages()
        self.websocket = None  # why

    def place_pixel(self):
        """ Actually place a pixel hype"""
        delay = 10

        loop = asyncio.get_event_loop()

        self.differences = loop.run_until_complete(images.get_pixel_differences_with_canvas_download(order=self.current_order, canvas_indexes=self.config.canvas_indexes, order_image=self.order_image))

        if not self.id:
            self.place_timer = threading.Timer(delay, self.place_pixel)
            self.place_timer.start()
            return  # Silent return if we do not have an id yet

        if not self.differences:
            print(f"{now()} {LIGHTGREEN}No pixels have to be placed 🥳{R}")

            self.place_cooldown = reddit.get_place_cooldown(self.config.auth_token)
            print(f"{now()} {LIGHTGREEN}Attempt to place pixel again in {AQUA}{self.place_cooldown + delay}{LIGHTGREEN} seconds!{R}")

            self.place_timer = threading.Timer(self.place_cooldown + delay, self.place_pixel)
            self.place_timer.start()
            return

        # pick a random pixel and place it
        random_index = random.randrange(len(self.differences))
        difference = self.differences[random_index]

        x, y = difference[0], difference[1]
        canvasIndex = canvas.xy_to_canvasIndex(x, y)

        if canvasIndex is None:
            printc(RED, f"Canvas index is None!!!, x={x}, y={y}")
            return

        x = x % 1000
        y = y % 1000


        print("canvasIndex", canvasIndex)
        coords = reddit.Coordinates(x, y, canvasIndex)

        colorTuple = difference[2]
        colorIndex = canvas.colorTuple_to_colorIndex(colorTuple)

        print(f"{now()} {GREEN}Placing pixel at x={AQUA}{x}{GREEN}, y={AQUA}{y}{GREEN} on canvas {AQUA}{canvasIndex} {RED}H{GREEN}Y{YELLOW}P{BLUE}E{PURPLE}!{R}")

        reddit.place_pixel(self.config, coords, colorIndex)

        # Schedule the next timer
        self.place_cooldown = reddit.get_place_cooldown(self.config.auth_token)
        print(f"{now()} {LIGHTGREEN}Attempt to place pixel again in {AQUA}{self.place_cooldown + delay}{LIGHTGREEN} seconds!{R}")

        self.place_timer = threading.Timer(self.place_cooldown + delay, self.place_pixel)
        print(f"{now()} {LIGHTGREEN}Placing next pixel in {AQUA}{self.place_cooldown + delay / 60:2.2f}{LIGHTGREEN} seconds!{R}")
        self.place_timer.start()

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
                print(f"{now()} {RED}Error processing message: {e}")
                pprint(message)
                await self.log_error(str(type(e)), str(e))

                if isinstance(e, TimeoutError):
                    raise e

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

    async def send_enable_place_capability(self):
        await self.send_message("enableCapability", "place")

    async def send_enable_placeNOW_capability(self):
        await self.send_message("enableCapability", "placeNow")

    async def send_disable_placeNOW_capability(self):
        await self.send_message("disableCapability", "placeNow")

    async def send_enable_priorityMappings_capability(self):
        await self.send_message("enableCapability", "priorityMappings")

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
                await self.handle_ping()
            case 'hello':
                await self.handle_hello(payload)
            case 'brandUpdated':
                print(f"{now()} {GREEN}Brand has been updated successfully!{R}")
            case 'order':
                try:
                    await self.handle_order(payload)
                except asyncio.exceptions.TimeoutError:
                    print(f"{now()} {RED}Timed Out on handeling the order, lets try again")
                    self.pong_timer.cancel()
                    await self.send_pong()
                    await self.handle_message(message_type, payload)
            case 'stats':
                self.handle_stats(payload)
            case 'announcement':
                self.handle_announcement(payload)
            case 'enabledCapability':
                self.handle_enableCapability(payload)
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
        4. Set the place capability
        """
        self.id = payload['id']
        self.keepaliveInterval = payload['keepaliveInterval']
        self.keepaliveTimeout = payload['keepaliveTimeout']

        print(f"{now()} {GREEN}Obtained Client id: {AQUA}{self.id}")

        await gather(self.send_brand(), self.send_getStats(), self.send_getOrder() if self.can_place else asyncio.sleep(1), self.send_enable_place_capability())

        await gather(self.subscribe_to_announcements(), self.subscribe_to_orders() if self.can_place else asyncio.sleep(1), self.subscribe_to_stats() if self.config.stats else asyncio.sleep(1))

    async def handle_ping(self):
        if not (self.pong_timer and not self.pong_timer.finished):
            await self.send_pong()

    async def send_pong(self):
        await self.send_message('pong')

    def send_pong_job(self):
        print(now(), f"{GREEN}Pong from other thread to stay alive")
        loop = asyncio.new_event_loop()
        loop.run_until_complete(self.send_pong())
        self.pong_timer = threading.Timer((self.keepaliveTimeout - self.keepaliveInterval) / 1000, self.send_pong_job)
        self.pong_timer.start()

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

    async def handle_order(self, payload):
        print(f"{now()} {GREEN}Starting to handle order{R} 📧")
        self.current_order = parse_order(payload)
        print(self.current_order)

        # Set a timer for sending pong messages in the background
        self.pong_timer = threading.Timer((self.keepaliveTimeout - self.keepaliveInterval) / 1000, self.send_pong_job)
        self.pong_timer.start()

        # Stop the place timer if we had one
        if self.place_timer and not self.place_timer.finished:
            print(f"{now()} {GREEN}Stopped place timer while processing new order")
            self.place_timer.cancel()


        # handle the order
        self.order_image = await images.download_image(self.current_order.images.order)

        print(f"{now()} {GREEN}Got {RED}{len(self.differences)} {GREEN}differences{R}")

        self.place_cooldown = reddit.get_place_cooldown(self.config.auth_token)

        # Stop the pong timer
        self.pong_timer.cancel()

        # Start the place timer
        self.place_timer = threading.Timer(self.place_cooldown + 10, self.place_pixel)
        self.place_timer.start()

        print(f"{now()} {GREEN}Started place timer again")

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
                print(f"{now()}{RED}We are being disconnected shortly {AQUA}(Code={reason}){RED}.{R} {message}")
                if reason == "timedOut":
                    raise TimeoutError(message)

    def handle_enableCapability(self, payload):
        printc(f"{now()} {GREEN}Enabled {AQUA}{payload}{GREEN} capability")
        if payload == "placeNow":
            self.send_disable_placeNOW_capability()

    def handle_disabledCapability(self, payload):
        printc(f"{now()} {RED}Disabled {AQUA}{payload}{GREEN} capability")
