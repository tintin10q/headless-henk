import asyncio
import random
import datetime
import threading

import canvas
import images
import login
import reddit
from colors import *
from config import Config

from chief import ChiefClient

from live_canvas import LiveCanvas


class PixelClient:
    place_delay = 7

    def __init__(self, config: Config, chief: ChiefClient, live_canvas: LiveCanvas):
        self.config = config
        self.chief = chief
        self.place_cooldown = PixelClient.place_delay
        self.live_canvas = live_canvas
        self.differences = []

    async def place_pixel(self, *, after: int):
        """ Actually place a pixel hype"""
        print(
            f"{self.now()} {LIGHTGREEN}Placing next pixel in {AQUA}{PixelClient.place_delay:2.2f}{LIGHTGREEN} seconds!{R}")
        await asyncio.sleep(after)
        printc(f"{self.now()} {AQUA}== Starting to place pixel for {self.config.reddit_username}=={RESET}")
        self.differences = images.get_pixel_differences(order=self.chief.current_order, canvas=self.live_canvas.canvas, chief_template=self.chief.order_image, username=self.config.reddit_username)
        print(f"{self.now()} {GREEN}Found {RED}{len(self.differences)} {R}differences!")

        # Got differences
        if not self.differences:
            print(f"{self.now()} {LIGHTGREEN}No pixels have to be placed 🥳{R}")

            print(
                f"{self.now()} {LIGHTGREEN}Attempt to place pixel again in {AQUA}{PixelClient.place_delay}{LIGHTGREEN} seconds!{R}")
            return

        # Check if we have priority, otherwise pick a random pixel and place it
        random_index = random.randrange(len(self.differences))

        def weighted_sort(diff: images.ImageDiff):
            return diff.priority

        if self.chief.priority_image:
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
        if self.chief.connected:
            print(f"{self.now()} {GREEN}Sending place now{STOP}")
            await self.chief.send_enable_placeNOW_capability()
            actually_send_place_now = True
        else:
            print(f"{self.now()} {YELLOW}The client is currently not connected to chief. Not sending placeNOW capability{STOP}")

        try:
            # actually place pixel
            reddit.place_pixel(self.config, coords, colorIndex)
        except reddit.RateLimitReached:
            if actually_send_place_now and self.chief.connected:  # still disable this if it was enabled, do not send coords!
                await self.chief.send_disable_placeNOW_capability()
            self.place_cooldown = reddit.get_place_cooldown(self.config.auth_token)

            # Scheduled next place task
            print(f"{self.now()} {LIGHTGREEN}Placing next pixel in {AQUA}{self.place_cooldown + PixelClient.place_delay}{LIGHTGREEN} seconds!{GREEN} (not sending coords because the rate limit was hit)")
            return

        if actually_send_place_now:
            # Scheduled next place task
            print(f"{self.now()} {YELLOW}Not sending disable place now{STOP}")
            await self.chief.send_disable_placeNOW_capability()

        if self.chief.connected:
            print(f"{self.now()} {GREEN}Sending placed pixel to chief")
            await self.chief.send_place_msg(global_x, global_y, colorIndex)
        else:
            print(f"{self.now()} {YELLOW}The client is currently not connected to chief. Not sending placed pixel to chief{STOP}")

        print(f"{self.now()} {LIGHTGREEN}Placing next pixel in {AQUA}{self.place_cooldown + PixelClient.place_delay}{LIGHTGREEN} seconds!{R}")
        # Schedule the next timer
        return self.place_cooldown

    def now(self, formatstr="%H:%M:%S") -> str:
        """Prints the time in a nice way"""
        username = self.config.reddit_username
        return f"{WHITE}[{datetime.datetime.now().strftime(formatstr)}{' ' + username if username else ''}]{RESET}"

    @staticmethod
    async def run(client: 'PixelClient', delay=0):
        await client.live_canvas.is_connected()
        print(f"{client.now()} {GREEN}Live Canvas got connected!")
        await client.chief.has_canvas_future()
        print(f"{client.now()} {GREEN}Chief got connected! Starting {client.config.reddit_username} in {AQUA}{delay}{GREEN} seconds{R}")
        await asyncio.sleep(delay)
        while True:
            client.place_cooldown = reddit.get_place_cooldown(authorization=client.config.auth_token, username=client.config.reddit_username)

            try:
                await client.place_pixel(after=client.place_cooldown)
            except reddit.RateLimitLimitReached as e:
                print(f"{client.now()} {RED} Rate limit limit reached! Not starting again for {client.config.reddit_username}. {GREEN}This client will exit with the next ping message from chief.{RESET}")
                return
