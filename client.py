import asyncio
import time
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
import login
import reddit
from colors import *
from now import now_usr
from parse_order import parse_order, Order, Image
from config import Config, load_config
from images import ImageDiff

R = RESET


class Client:
    """
    The place NL client

    Create it by passing a Config object, or don't, and it will try to load a config from config.toml

    Its simple, we receive messages in receive_message and then the handle_message function handles them.

    """
    __slots__ = 'chief_host', 'uri', 'websocket', 'config', 'current_order', 'differences', 'place_cooldown', 'can_place', 'id', 'keepaliveTimeout', 'keepaliveInterval', 'place_timer', 'pong_timer', 'priority_image', 'order_image', 'connected', 'rate_limited', 'not_connected_times', 'try_connect_again'

    place_delay = 3

    def __init__(self, config: Config = None):
        if config is None:
            config = load_config()
        uri = f"wss://{config.chief_host}/ws"  # Replace with your server's WebSocket endpoint
        self.chief_host = config.chief_host
        self.uri = uri
        self.websocket: websockets.legacy.client.WebSocketClientProtocol | None = None
        self.config: Config = config
        self.current_order: Order | None = None
        self.differences = []

        # False when not connected to chief
        self.connected = False

        self.place_cooldown = 0
        self.can_place = False

        # Set after hello has been sent
        self.id: str | None = None
        self.keepaliveTimeout: int | None = None
        self.keepaliveInterval: int | None = None

        self.place_timer: threading.Timer | None = None
        self.pong_timer: threading.Timer | None = None

        self.priority_image: Image | None = None
        self.order_image: Image | None = None

        # Set this to the number (or just true) it was rate limited to throw reddit.RateLimitLimitReached when the next ping message comes in
        self.rate_limited: int = False
        self.try_connect_again: int = False

        self.not_connected_times = 0

    async def connect(self):
        printc(f"{self.now()} {GREEN}Checking reddit token...")

        self.place_cooldown = reddit.get_place_cooldown(self.config.auth_token)
        self.can_place = self.place_cooldown is not None  # If this is none the token is not valid

        if not self.can_place:
            printc(f"{self.now()} {RED}This reddit jwt token can not place pixels!")
            raise CanNotPlace()

        # start place timer with delay so that we have time to connect to chief
        self.place_timer = threading.Timer(self.place_cooldown + Client.place_delay, self.place_pixel)
        self.place_timer.daemon = True
        self.place_timer.start()

        printc(
            f"{self.now()} {GREEN}Placing pixel in {AQUA}{self.place_cooldown + Client.place_delay}{RESET} {GREEN}seconds")

        async with websockets.connect(self.uri) as websocket:
            print(f"{now_usr(username=self.config.reddit_username)} {GREEN} connected to chief!")
            self.connected = True

            # Send a sample 'brand' message to the server
            self.websocket = websocket

            # Receive messages from the server
            await self.receive_messages()

    def place_pixel(self):
        """ Actually place a pixel hype"""
        printc(f"{self.now()} {AQUA}== Starting to place pixel =={RESET}")

        if not self.id:  # this may be out of date after a disconnect.
            self.not_connected_times += 1
            print(f"{self.now()} {GREEN}Never yet connected to chief (we dont have an id yet!) trying again in {Client.place_delay} seconds")
            print(f"{self.order_image}")
            self.not_connected_times += 1

            if self.not_connected_times > 5:
                print(f"{self.now()} {GREEN}Restarting client not yet connected reason")
                self.try_connect_again = True


            self.place_timer = threading.Timer(Client.place_delay, self.place_pixel)
            self.place_timer.daemon = True
            self.place_timer.start()
            return  # Silent return if we do not have an id yet

        loop2 = asyncio.new_event_loop()

        if not self.order_image:  # It can happen that we do not have an chief image yet
            print(f"{self.now()} {GREEN}No order image for some reason? Downloading it again{RESET}")

            if not self.current_order:  # If we have no chief we can not place a pixel
                print(f"{self.now()} {YELLOW}The client has no order yet. Sending getOrder message!{RESET}")
                if self.connected:
                    loop2.run_until_complete(self.send_getOrder())
                    print(f"{self.now()} {GREEN}Send chief message! Trying to place pixel again in {AQUA}30{GREEN} seconds{RESET}")
                else:
                    print(f"{self.now()} {RED}The client is currently not connected to chief. Schedule place pixel again in {AQUA}30{RED} seconds{STOP}")
                self.place_timer = threading.Timer(30, self.place_pixel)
                self.place_timer.daemon = True
                self.place_timer.start()
                return

            self.order_image = loop2.run_until_complete(
                images.download_order_image(self.current_order.images.order, save_images=self.config.save_images,
                                            username=self.config.reddit_username))

        try:
            self.differences = loop2.run_until_complete(
                images.get_pixel_differences_with_canvas_download(order=self.current_order,
                                                                  canvas_indexes=self.config.canvas_indexes,
                                                                  order_image=self.order_image,
                                                                  priority_image=self.priority_image,
                                                                  save_images=self.config.save_images,
                                                                  username=self.config.reddit_username))
        except (asyncio.CancelledError, asyncio.TimeoutError):
            print(f"{self.now()} {YELLOW}Timed while getting differences trying one more time!")
            try:
                self.differences = loop2.run_until_complete(
                    images.get_pixel_differences_with_canvas_download(order=self.current_order,
                                                                      canvas_indexes=self.config.canvas_indexes,
                                                                      order_image=self.order_image,
                                                                      priority_image=self.priority_image,
                                                                      save_images=self.config.save_images,
                                                                      username=self.config.reddit_username))
            except (asyncio.CancelledError, asyncio.TimeoutError):
                print(f"{self.now()} {YELLOW}Timed out while differences again! Giving up!")
                self.place_timer = threading.Timer(Client.place_delay, self.place_pixel)
                self.place_timer.daemon = True
                print(
                    f"{self.now()} {LIGHTGREEN}Placing next pixel in {AQUA}{Client.place_delay:2.2f}{LIGHTGREEN} seconds!{R}")
                self.place_timer.start()
                return

        print(f"{self.now()} {GREEN}Found {RED}{len(self.differences)} {R}differences!")

        if self.place_timer:
            self.place_timer.cancel()  # just in case

        if not self.differences:
            print(f"{self.now()} {LIGHTGREEN}No pixels have to be placed 🥳{R}")

            print(
                f"{self.now()} {LIGHTGREEN}Attempt to place pixel again in {AQUA}{Client.place_delay}{LIGHTGREEN} seconds!{R}")

            self.place_timer = threading.Timer(Client.place_delay, self.place_pixel)
            self.place_timer.daemon = True
            self.place_timer.start()
            return

        # Check if we have priority, otherwise pick a random pixel and place it
        random_index = random.randrange(len(self.differences))

        def weighted_sort(diff: ImageDiff):
            return diff.priority

        if self.priority_image:
            random_index = 0
            self.differences.sort(reverse=True, key=weighted_sort)

        difference = self.differences[random_index]

        global_x, global_y = difference.x, difference.y
        canvasIndex = canvas.xy_to_canvas_index(global_x, global_y)

        if canvasIndex is None:
            printc(RED, f"{self.now()}Canvas index is None!!!, x={global_x}, y={global_y}")
            return

        x_ui = global_x - 1500
        y_ui = global_y - 1000

        x = global_x % 1000
        y = global_y % 1000

        coords = reddit.Coordinates(x, y, canvasIndex)

        colorTuple = difference.template_pixel
        colorIndex = canvas.color_tuple_to_color_index(colorTuple)

        print(f"{self.now()} {GREEN}Difference:{RESET}", difference)

        hex_color = canvas.rgba_to_hex(colorTuple)
        color_name = canvas.color_index_to_name(colorIndex)
        print(f"{self.now()} {GREEN}HEX {RESET}{hex_color}, {GREEN}which is {RESET}{color_name}")

        print(
            f"{self.now()} {GREEN}Placing {RESET}{color_name}{GREEN} pixel with weight={YELLOW}{difference.priority}{GREEN} at x={AQUA}{x_ui}{GREEN}, y={AQUA}{y_ui}{GREEN} on the canvas {AQUA}{canvasIndex}, {RED}H{GREEN}Y{YELLOW}P{BLUE}E{PURPLE}!{R}")

        login.refresh_token_if_needed(self.config)

        actually_send_place_now = False
        if self.connected:
            loop2.run_until_complete(self.send_enable_placeNOW_capability())
            actually_send_place_now = True
        else:
            print(f"{self.now()} {YELLOW}The client is currently not connected to chief. Not sending placeNOW capability{STOP}")

        try:
            # actually place pixel
            reddit.place_pixel(self.config, coords, colorIndex)
        except reddit.RateLimitReached:
            if actually_send_place_now:  # still disable this if it was enabled, do not send coords!
                loop2.run_until_complete(self.send_disable_placeNOW_capability())
            self.place_cooldown = reddit.get_place_cooldown(self.config.auth_token)
            self.place_timer = threading.Timer(self.place_cooldown + Client.place_delay, self.place_pixel)
            self.place_timer.daemon = True
            print(f"{self.now()} {LIGHTGREEN}Placing next pixel in {AQUA}{self.place_cooldown + Client.place_delay}{LIGHTGREEN} seconds!{GREEN} (not sending coords because the rate limit was hit)")
            self.place_timer.start()
            return

        except reddit.RateLimitLimitReached as e:
            self.rate_limited = e.rate_limit_times
            print(f"{self.now()} {RED} Rate limit limit reached! Not starting new pixel timer for {self.config.reddit_username}. {GREEN}This client will exit with the next ping message from chief.{RESET}")
            # Don't start new place pixel thread
            return

        if actually_send_place_now:
            loop2.run_until_complete(self.send_disable_placeNOW_capability())

        if self.connected:
            print(f"{self.now()} {GREEN}Sending placed pixel to chief")
            loop2.run_until_complete(self.send_place_msg(global_x, global_y, colorIndex))
        else:
            print(f"{self.now()} {YELLOW}The client is currently not connected to chief. Not sending placed pixel to chief{STOP}")

        # Schedule the next timer
        self.place_cooldown = reddit.get_place_cooldown(self.config.auth_token)

        self.place_timer = threading.Timer(self.place_cooldown + Client.place_delay, self.place_pixel)
        self.place_timer.daemon = True
        print(f"{self.now()} {LIGHTGREEN}Placing next pixel in {AQUA}{self.place_cooldown + Client.place_delay}{LIGHTGREEN} seconds!{R}")
        self.place_timer.start()

    async def receive_messages(self):
        """ Do the basic parsing of an incoming message, separate type and payload
            handle_message actually does something with the message
        """
        async for message in self.websocket:

            if self.try_connect_again:
                raise TimeoutError("Try reconnect")

            try:
                data = json.loads(message)
                if 'type' not in data:
                    return self.log_error('invalidPayload', 'noType')
                message_type = data['type']
                payload = data.get("payload", None)
                await self.handle_message(message_type, payload)


            except json.JSONDecodeError:
                self.log_error('invalidMessage', 'failedToParseJSON')
            except reddit.RateLimitLimitReached as e:
                # This should come from the ping message if self.ratelimited = True, that happens if place pixel hits too many rate limits. We do it this way because place pixel is in another thread
                raise e
            except Exception as e:
                print(f"{self.now()} {RED}Error processing message: {e}")
                pprint(message)
                self.log_error(str(type(e)), str(e))

                if isinstance(e, TimeoutError):
                    raise e

    async def send_getCapabilities(self):
        print(f"{self.now()} Received get capabilities message")

    async def send_getOrder(self):
        # Handle the 'getOrder' message
        # Send the 'chief' message with the latest orders
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

    async def send_brand(self):
        # Handle the 'brand' message
        # Validate the brand information and send 'brandUpdated' or 'invalidPayload' error
        brand = self.config.get_brand_payload()
        await self.send_message('brand', brand)

    async def send_place_msg(self, x: int, y: int, color: int):
        await self.send_message('place', {'x': x, 'y': y, 'color': color})

    async def send_message(self, message_type: Literal[
        'pong', 'brand', 'getOrder', 'getStats', 'getCapabilities', 'enableCapability', 'disableCapability', 'getSubscriptions', 'subscribe', 'unsubscribe', 'place'],
                           payload=None):
        message = {'type': message_type}

        if payload is not None:
            message['payload'] = payload

        if message_type != 'pong' or self.config.pingpong:
            print(f"{self.now()} {GREEN}Sending message {BLUE}{message_type}{GREEN} ", end=R)
            if payload:
                pprint(payload)
            else:
                print()

        try:
            await self.websocket.send(json.dumps(message))
        except websockets.ConnectionClosedError:
            print(f"{self.now()} {RED} Could not send {AQUA}{message_type}{RED} message to chief because the connection is closed. {RESET}")
            print("Now we need to try and reconnect but for now just throwing timedOut")
            raise TimeoutError()
        except (websockets.WebSocketException) as error:
            print(f"{self.now()} {RED} Could not send {AQUA}{message_type}{RED} message to chief :( moving on.. {RESET}{error=}")
            # Idk if moving on is a good idea, we can always raise TimeOutError if it is a problem

        if message_type != 'pong' or self.config.pingpong:
            printc(GREEN + f"{self.now()} {GREEN}Sent message: {R}{message}")

    def log_error(self, error_type, error_detail):
        """ Log the error, only the server can actually send errors to us """
        print(f"{self.now()} {RED}Something went wrong: {PURPLE}{error_type}{RED},{PURPLE}{error_detail}{R}")
        # error_message = { 'type': 'error', 'payload': { 'type': error_type, 'detail': error_detail } }
        # print(RED + f"Sending error message: {error_type} with {error_detail}" + R)

    async def handle_message(self, message_type: str, payload: dict | str | None):
        # Todo remove with : {payload}

        if message_type != 'ping' or self.config.pingpong:
            print(
                BLUE + f"{self.now()} {BLUE}Received message: {R}{GREEN}{message_type}{R}")  # with: {R}{PURPLE}{payload}{R}")
        match message_type:
            case 'ping':
                await self.handle_ping()
            case 'hello':
                await self.handle_hello(payload)
            case 'brandUpdated':
                print(f"{self.now()} {GREEN}Brand has been updated successfully!{R}")
            case 'chief':
                try:
                    await self.handle_order(payload)
                except asyncio.exceptions.TimeoutError:
                    print(f"{self.now()} {RED}Timed Out on handeling the order, lets try again")
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
                self.log_error('invalidPayload', 'unknownType')

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

        await gather(self.send_brand(), self.send_getStats(),
                     self.send_getOrder() if self.can_place else asyncio.sleep(1), self.send_enable_place_capability(),
                     self.send_enable_priorityMappings_capability())

        await gather(self.subscribe_to_announcements(),
                     self.subscribe_to_orders() if self.can_place else asyncio.sleep(1),
                     self.subscribe_to_stats() if self.config.stats else asyncio.sleep(1))

        # If we get here we can assume we are connected to Chief
        self.connected = True

    async def handle_ping(self):
        if self.rate_limited:
            raise reddit.RateLimitLimitReached(rate_limit_times=self.rate_limited)
        if not (self.pong_timer and not self.pong_timer.finished):
            await self.send_pong()

    async def send_pong(self):
        await self.send_message('pong')

    def send_pong_job(self):
        print(self.now(), f"{GREEN}Pong from other thread to stay alive")
        loop = asyncio.new_event_loop()
        loop.run_until_complete(self.send_pong())
        self.pong_timer = threading.Timer((self.keepaliveTimeout - self.keepaliveInterval) / 1000, self.send_pong_job)
        self.pong_timer.daemon = True
        self.pong_timer.start()

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
                                                             save_images=self.config.save_images,
                                                             username=self.config.reddit_username)
        print(f"{self.now()} {GREEN}Downloaded chief image{R}")

        # download the priority map
        if self.current_order.images.priority:
            self.priority_image = await images.download_priority_image(self.current_order.images.priority,
                                                                       save_images=self.config.save_images,
                                                                       username=self.config.reddit_username)
            print(f"{self.now()} {GREEN}Downloaded priority image{R}")
        else:
            self.priority_image = None  # to avoid having an older priority map

        # Show time till next place
        login.refresh_token_if_needed(self.config)
        self.place_cooldown = reddit.get_place_cooldown(self.config.auth_token)

        printc(
            f"{self.now()} {GREEN}Placing pixel in {AQUA}{self.place_cooldown + Client.place_delay}{RESET} {GREEN}seconds")

        # Stop the pong timer
        self.pong_timer.cancel()

        print(f"{self.now()} {GREEN}Done handling chief ")

    @staticmethod
    def handle_announcement(payload):
        match payload:
            case {"message": str(message), "important": important}:
                print(
                    f"\n{LIGHTPURPLE}{PURPLE_BG + BLINK + BEEP if important else ''}---=== Chief {'IMPORTANT ' if important else ''}Announcement ===---{R}"
                    f"\n{now_usr()} {message}\n")
            case _:
                print(now_usr(), "Got announcement but couldn't parse it...🤔")
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
        print(f"{self.now()} {RED}Disabled {AQUA}{payload}{RED} subscription{R}")

    def handle_subscribed(self, payload: str):
        print(f"{self.now()} {GREEN}Enabled {AQUA}{payload}{GREEN} subscription{R}")

    def handle_disconnect(self, payload: dict):
        match payload:
            case {"reason": str(reason), "message": str(message)}:
                print(f"{self.now()}{RED}We are being disconnected shortly {AQUA}(Code={reason}){RED}.{R} {message}")
                if reason == "timedOut":
                    raise TimeoutError(message)

    def handle_enableCapability(self, payload):
        printc(f"{self.now()} {GREEN}Enabled {AQUA}{payload}{GREEN} capability")

    def handle_disabledCapability(self, payload):
        printc(f"{self.now()} {RED}Disabled {AQUA}{payload}{GREEN} capability")

    def handle_confirmPlace(self):
        printc(f"{self.now()} {BLUE}Chief successfully received pixel placement{RESET}")

    @staticmethod
    async def run_client(client: "Client", delay: int = None):
        if isinstance(delay, int) and delay > -1:
            delay += random.randint(-2, 5)
            print(
                f"{now_usr(username=client.config.reddit_username)} {GREEN}Starting {AQUA}{client.config.reddit_username or f'{GREEN}client'}{GREEN} in {AQUA}{delay}{AQUA}{GREEN} seconds{R}")
            await asyncio.sleep(delay)
        while True:
            try:
                await client.connect()
            except (TimeoutError, asyncio.exceptions.TimeoutError):
                print(
                    f"{now_usr(username=client.config.reddit_username)} {YELLOW}We got disconnected from chief. Lets try connect again in {AQUA}60{YELLOW} seconds.{BLUE} place timer should still be running!{R}")
                # if client.place_timer:
                #     client.place_timer.cancel()
                # Removed stopping place timer so that keeps going!
                client.connected = False
                if client.pong_timer:
                    client.pong_timer.cancel()
                time.sleep(60)  # Longer to give Chief time to restart
            except (websockets.InvalidStatusCode):
                print(
                    f"{now_usr(username=client.config.reddit_username)} Server rejected connection. Lets try connect again in 10 seconds")
                # if client.place_timer:
                #     client.place_timer.cancel()
                # Removed stopping place timer so that keeps going!
                client.connected = False
                if client.pong_timer:
                    client.pong_timer.cancel()
                time.sleep(10)
            except (websockets.WebSocketException):
                print(f"{now_usr(username=client.config.reddit_username)} Websocket error. Lets try connect again in 10 seconds")
                # if client.place_timer:
                #     client.place_timer.cancel()
                client.connected = False
                if client.pong_timer:
                    client.pong_timer.cancel()
                time.sleep(10)
            except (CanNotPlace):
                if client.place_timer:
                    client.place_timer.cancel()
                if client.pong_timer:
                    client.pong_timer.cancel()
                if client.config.reddit_username:
                    print(
                        f"{now_usr(username=client.config.reddit_username)} {client.config.reddit_username} can not place pixels")
                else:
                    print(f"{now_usr(username=client.config.reddit_username)} This account can not place pixels")
                return
            except (login.CouldNotRefreshToken):
                if client.place_timer:
                    client.place_timer.cancel()
                if client.pong_timer:
                    client.pong_timer.cancel()
                if client.config.reddit_username:
                    print(
                        f"{now_usr(username=client.config.reddit_username)} Could not refresh token for {AQUA}{client.config.reddit_username}{RESET} stopping {AQUA}{client.config.reddit_username}{RESET}")
                else:
                    print(f"{now_usr(username=client.config.reddit_username)} Could not refresh token for this account")
                return
            except reddit.RateLimitLimitReached:
                print(f"{PURPLE}Stopping {AQUA}{client.config.reddit_username}{GREEN} because it hit the rate limit limit which is {AQUA}{reddit.rate_limit_limit}{RESET}")
                break
            else:  # If no error happened, but we got here then just let it die
                print(f"{PURPLE}Stopping {AQUA}{client.config.reddit_username}{RESET}")
                break

    def now(self, formatstr="%H:%M:%S") -> str:
        """Prints the time in a nice way"""
        username = self.config.reddit_username
        return f"{WHITE}[{datetime.datetime.now().strftime(formatstr)}{' ' + username if username else ''}]{RESET}"


class CanNotPlace(Exception):
    pass
