import asyncio
import json
import threading
from pprint import pprint
from typing import Literal

import websockets

import images
from colors import *

import datetime

from parse_order import parse_order, Order
from reddit import Coordinates

SAVE_IMAGES = False


class ChiefClient:
    """The idea """

    author: str = "Quinten-C"
    version: str = '4.0.0'
    name: str = 'Headless-Henk'

    brand = {"author": author, "name": name, "version": version}

    __slots__ = 'chief_host', 'order_image', 'priority_image', 'pingpong', 'pong_timer', 'connected', 'current_order', 'ws', 'id', 'keepaliveTimeout', 'keepaliveInterval', 'uri'

    def __init__(self, chief_host: str):

        self.id = None
        self.keepaliveTimeout = 3
        self.keepaliveInterval = 1

        self.chief_host = chief_host
        self.pingpong = True
        self.pong_timer: threading.Timer | None = None
        self.connected: bool = False
        self.current_order: Order | None = None
        self.ws = None

        self.order_image = None
        self.priority_image = None
        self.current_order: Order | None = None

        self.uri = f"wss://{chief_host}/ws"  # Replace with your server's WebSocket endpoint

    async def connect(self):

        print(f"{self.now()}{GREEN} Connecting to chief...")
        async with websockets.connect(self.uri) as websocket:
            print(f"{self.now()}{GREEN} connected to chief!")
            self.connected = True

            # Send a sample 'brand' message to the server
            self.ws = websocket

            # Receive messages from the server
            await self.receive_messages()

    async def receive_messages(self):
        """ Do the basic parsing of an incoming message, separate type and payload
            handle_message actually does something with the message
        """
        async for message in self.ws:
            try:
                data = json.loads(message)
                if 'type' not in data:
                    return self.log_error('invalidPayload', 'noType')
                message_type = data['type']
                payload = data.get("payload", None)
                await self.handle_message(message_type, payload)

            except json.JSONDecodeError:
                self.log_error('invalidMessage', 'failedToParseJSON')
            except Exception as e:
                print(f"{self.now()} {RED}Error processing message: {e}")
                pprint(message)
                self.log_error(str(type(e)), str(e))

                if isinstance(e, TimeoutError):
                    raise e

    async def handle_message(self, message_type: str, payload: dict | str | None):
        # Todo remove with : {payload}

        if message_type != 'ping' or self.pingpong:
            print(
                BLUE + f"{self.now()} {BLUE}Received message: {R}{GREEN}{message_type}{R}")  # with: {R}{PURPLE}{payload}{R}")
        match message_type:
            case 'ping':
                await self.handle_ping()
            case 'hello':
                await self.handle_hello(payload)
            case 'brandUpdated':
                print(f"{self.now()} {GREEN}Brand has been updated successfully!{R}")
            case 'order':
                try:
                    await self.handle_order(payload)
                except asyncio.exceptions.TimeoutError:
                    print(f"{self.now()} {RED}Timed Out on handling the order, lets try again")
                    self.pong_timer.cancel()
                    await self.send_pong()
                    await self.handle_message(message_type, payload)
            case 'confirmPlace':
                self.handle_confirmPlace()
            case 'stats':
                self.handle_stats(payload)
            case 'announcement':
                self.handle_announcement(payload)
            case 'enabledCapability':
                self.handle_enableCapability(payload)
            case 'disabledCapability':
                self.handle_disabledCapability(payload)
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
                print(f"{self.now()} {RED} Something went wrong with message {BLUE}{message_type}")
                self.log_error('invalidPayload', 'unknownType')

    def handle_stats(self, payload: dict):
        match payload:

            case {"activeConnections": int(activeConnections), "messagesIn": int(messageIn),
                  "messagesOut": int(messageOut), "date": int(date), "socketConnections": int(socketConnections),
                  "capabilities": {'place': int(place), 'placeNow': int(placenow),
                                   'priorityMappings': int(priorityMappings)}}:
                dt_object = datetime.datetime.fromtimestamp(date / 999)
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
            case {"activeConnections": int(activeConnections), "messagesIn": int(messageIn),
                  "messagesOut": int(messageOut), "date": int(date), "socketConnections": int(socketConnections)}:
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

    def handle_announcement(self, payload):
        match payload:
            case {"message": str(message), "important": important}:
                print(
                    f"\n{LIGHTPURPLE}{PURPLE_BG + BLINK + BEEP if important else ''}---=== Chief {'IMPORTANT ' if important else ''}Announcement ===---{R}"
                    f"\n{self.now()} {message}\n")
            case _:
                print(self.now(), "Got announcement but couldn't parse it...🤔")
                pprint(payload)
                raise ValueError(f"Could not parse announcement: {payload}")

    def handle_enableCapability(self, payload):
        printc(f"{self.now()} {GREEN}Enabled {AQUA}{payload}{GREEN} capability")

    def handle_disabledCapability(self, payload):
        printc(f"{self.now()} {RED}Disabled {AQUA}{payload}{GREEN} capability")

    def handle_confirmPlace(self):
        printc(f"{self.now()} {BLUE}Chief successfully received pixel placement{RESET}")

    def handle_unsubscribed(self, payload: str):
        print(f"{self.now()} {RED}Disabled {AQUA}{payload}{RED} subscription{R}")

    def handle_subscribed(self, payload: str):
        print(f"{self.now()} {GREEN}Enabled {AQUA}{payload}{GREEN} subscription{R}")

    def handle_disconnect(self, payload: dict):
        match payload:
            case {"reason": str(reason), "message": str(message)}:
                print(f"{self.now()}{RED}We are being disconnected shortly {AQUA}(Code={reason}){RED}.{R} {message}")
                if reason == "timedOut":
                    raise TimeoutError(message)

    def log_error(self, error_type, error_detail):
        """ Log the error, only the server can actually send errors to us """
        print(f"{self.now()} {RED}Something went wrong: {PURPLE}{error_type}{RED},{PURPLE}{error_detail}{R}")
        # error_message = { 'type': 'error', 'payload': { 'type': error_type, 'detail': error_detail } }
        # print(RED + f"Sending error message: {error_type} with {error_detail}" + R)

    async def handle_hello(self, payload):
        """
        This function should do everything we want to do after we know the connection is here.

        0. Set connected to true
        1. Set the brand
        2. Set capabilities
        3. Get the orders
        4. Set the place capability
        """
        print(f"{self.now()}{GREEN}Handeling hello{R}")
        if not self.id:
            self.id = payload['id']
            self.keepaliveInterval = payload['keepaliveInterval']
            self.keepaliveTimeout = payload['keepaliveTimeout']

        print(f"{self.now()} {GREEN}Obtained Client id: {AQUA}{self.id}")

        await self.send_brand()
        await asyncio.gather(self.send_getOrder(), self.send_enable_priorityMappings_capability(), self.send_enable_place_capability())

        await self.subscribe_to_orders()

        # If we get here we can assume we are connected to Chief
        self.connected = True

    async def send_getOrder(self):
        # Handle the 'getOrder' message
        # Send the 'chief' message with the latest orders
        await self.send_message("getOrder")

    async def send_getSubscriptions(self):
        print("get subscriptions")

    async def send_disable_capability(self):
        raise NotImplemented()

    async def send_enable_place_capability(self):
        await self.send_message("enableCapability", "place")

    async def send_enable_placeNOW_capability(self):
        await self.send_message("enableCapability", "placeNow")

    async def send_disable_placeNOW_capability(self):
        await self.send_message("disableCapability", "placeNow")

    async def send_enable_priorityMappings_capability(self):
        await self.send_message("enableCapability", "priorityMappings")

    async def send_getStats(self):
        # Handle the 'getStats' message
        # Send the 'stats' message with current server statistics
        await self.send_message("getStats")

    async def send_unsubscribe(self, payload):
        print("got get unsubscribe")

    async def send_subscribe(self, payload):
        print("got get subscription message")

    async def send_getCapabilities(self):
        print(f"{self.now()} Received get capabilities message")

    async def subscribe_to_orders(self):
        await self.send_message("subscribe", "orders")

    async def send_brand(self):
        # Handle the 'brand' message
        # Validate the brand information and send 'brandUpdated' or 'invalidPayload' error
        await self.send_message('brand', ChiefClient.brand)

    async def handle_order(self, payload):
        print(f"{self.now()} {GREEN}Starting to handle chief{R} 📧")
        self.current_order = parse_order(payload)
        print(self.current_order)

        # Set a timer for sending pong messages in the background
        self.pong_timer = threading.Timer((self.keepaliveTimeout - self.keepaliveInterval) / 1000, self.send_pong_job)
        self.pong_timer.daemon = True
        self.pong_timer.start()

        # download the chief image
        self.order_image = await images.download_order_image(self.current_order.images.order,
                                                             save_images=SAVE_IMAGES)
        print(f"{self.now()} {GREEN}Downloaded chief image{R}")

        # download the priority map
        if self.current_order.images.priority:
            self.priority_image = await images.download_priority_image(self.current_order.images.priority,
                                                                       save_images=SAVE_IMAGES)
            print(f"{self.now()} {GREEN}Downloaded priority image{R}")
        else:
            self.priority_image = None  # to avoid having an older priority map

        # Stop the pong timer
        self.pong_timer.cancel()

        print(f"{self.now()} {GREEN}Done handling order{RESET}")

    async def handle_ping(self):
        if not (self.pong_timer and not self.pong_timer.finished):
            await self.send_pong()

    def send_pong_job(self):
        print(self.now(), f"{GREEN}Pong from other thread to stay alive")
        loop = asyncio.new_event_loop()
        loop.run_until_complete(self.send_pong())
        self.pong_timer = threading.Timer((self.keepaliveTimeout - self.keepaliveInterval) / 1000, self.send_pong_job)
        self.pong_timer.daemon = True
        self.pong_timer.start()

    def now(self, formatstr="%H:%M:%S") -> str:
        """Prints the time in a nice way"""
        return f"{PURPLE}[{datetime.datetime.now().strftime(formatstr)} Orders]{RESET}"

    async def send_pong(self):
        await self.send_message('pong')

    async def send_message(self, message_type: Literal[
        'pong', 'brand', 'getOrder', 'getStats', 'getCapabilities', 'enableCapability', 'disableCapability', 'getSubscriptions', 'subscribe', 'unsubscribe', 'place'],
                           payload=None):
        message = {'type': message_type}

        if payload is not None:
            message['payload'] = payload

        if message_type != 'pong' or self.pingpong:
            print(f"{self.now()} {GREEN}Sending message {BLUE}{message_type}{GREEN} ", end=R)
            if payload:
                pprint(payload)
            else:
                print()

        try:
            await self.ws.send(json.dumps(message))
        except websockets.ConnectionClosedError:
            print(f"{self.now()} {RED} Could not send {AQUA}{message_type}{RED} message to chief because the connection is closed. {RESET}")
            print("Now we need to try and reconnect but for now just throwing timedOut")
            raise TimeoutError()
        except (websockets.WebSocketException) as error:
            print(f"{self.now()} {RED} Could not send {AQUA}{message_type}{RED} message to chief :( moving on.. {RESET}{error=}")
            # Idk if moving on is a good idea, we can always raise TimeOutError if it is a problem

        if message_type != 'pong' or self.pingpong:
            printc(GREEN + f"{self.now()} {GREEN}Sent message: {R}{message}")

    async def has_canvas_future(self, delay: int = 3):
        while True:
            if self.order_image:
                break
            else:
                await asyncio.sleep(delay)

    async def send_pre_place_pixel_messages(self):
        await self.send_enable_placeNOW_capability()

    async def send_post_place_pixel_messages(self, coordinates: Coordinates, colorIndex: int = 3):
        await asyncio.gather(self.send_place_msg(x=coordinates.x, y=coordinates.y, color=colorIndex), self.send_disable_placeNOW_capability())

    async def send_place_msg(self, x: int, y: int, color: int):
        await self.send_message('place', {'x': x, 'y': y, 'color': color})


if __name__ == '__main__':
    default_chief_host = 'chief.placenl.nl'
    chief = ChiefClient(default_chief_host)
    loop = asyncio.new_event_loop()
    loop.run_until_complete(ChiefClient.run_ChiefClient(chief))

"""
Deze class moet ook de place pixel berichten gaan sturen.

Wat als we dat eerst even niet doen?

"""
