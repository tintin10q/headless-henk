import asyncio
import json
import time
from io import BytesIO
from typing import List

import httpx
import ojson
import requests
from PIL import Image

import reddit
import websockets
from colors import *
import datetime

from config import load_config_without_auth


class LiveCanvas:
    """ A live connection which updates the same image in memory with the difference, this way we don't have to fetch the whole canvas every time"""
    final_canvas_width = 3000
    final_canvas_height = 2000

    # Create the final canvas image.
    __slots__ = "websocket", 'reddit_uri_wss', 'canvas_indexes', "authorization", "message_id", "canvas_parts", "show_canvas_updates", "full_canvas", "connected"

    def __init__(self, reddit_uri_wss: str, canvas_indexes: List[int]):
        self.websocket = None
        self.authorization = reddit.get_anon_authorization()
        self.message_id = 2

        self.reddit_uri_wss = reddit_uri_wss
        self.canvas_indexes = canvas_indexes

        self.canvas_parts = [None, None, None, None, None, None]

        self.show_canvas_updates = False
        self.full_canvas = Image.new('RGBA', (LiveCanvas.final_canvas_width, LiveCanvas.final_canvas_height))

        self.connected: bool = False

    async def connect(self):
        while True:
            try:
                async with websockets.connect(self.reddit_uri_wss, origin="https://garlic-bread.reddit.com") as websocket:
                    self.websocket = websocket
                    connection_init_message = {
                        "type": 'connection_init',
                        "payload": {
                            "Authorization": self.authorization
                        }
                    }

                    printc(self.now(), f"{GREEN}Live canvas connected!")
                    await websocket.send(json.dumps(connection_init_message))

                    result = await websocket.recv()  # This should be {"type":"connection_ack"}
                    printc(self.now(), f"{GREEN}Live canvas connected!!{RESET}{result}")

                    ask_for_canvases_routines = []
                    for canvas_id in self.canvas_indexes:
                        url_message = {
                            "id": str(self.message_id),
                            "type": "start",
                            "payload": {
                                "variables": {
                                    "input": {
                                        "channel": {
                                            "teamOwner": "GARLICBREAD",
                                            "category": "CANVAS",
                                            "tag": str(canvas_id)
                                        }
                                    }
                                },
                                "extension": {},
                                "operationName": "replace",
                                "query": """subscription replace($input: SubscribeInput!) {  subscribe(input: $input) {    id    ... on BasicMessage {      data {        __typename        ... on FullFrameMessageData {          __typename          name          timestamp        }        ... on DiffFrameMessageData {          __typename          name          currentTimestamp          previousTimestamp        }      }      __typename    }    __typename  }}"""
                            }
                        }
                        self.message_id += 1
                        ask_for_canvases_routines.append(websocket.send(json.dumps(url_message)))

                    await asyncio.gather(*ask_for_canvases_routines)

                    del canvas_id

                    async for message in self.websocket:

                        message = ojson.loads(message)

                        # print(message)

                        match message:
                            case {"payload": {"data": {"subscribe": {"data": {"__typename": "FullFrameMessageData", "name": full_canvas_url}}}}, "id": full_canvas_id}:
                                full_canvas_id = int(full_canvas_id) - 2
                                print(f"{self.now()} {GREEN}Live Canvas received full frame of canvas {AQUA}{full_canvas_id}{RESET}")

                                while not self.canvas_parts[full_canvas_id]:
                                    try:
                                        async with httpx.AsyncClient() as client:
                                            response = await client.get(full_canvas_url)
                                        # response = requests.get(full_canvas_url)
                                        self.canvas_parts[full_canvas_id] = Image.open(BytesIO(response.content))
                                        break
                                    except:
                                        print(f"{self.now()} {YELLOW}Could not fetch full canvas part {AQUA}{full_canvas_id}{YELLOW} {full_canvas_url}, trying again{R}")

                                if not self.connected and all(self.canvas_parts):
                                    self.connected = True

                            case {"payload": {"data": {"subscribe": {"data": {"__typename": "DiffFrameMessageData", "name": difference_url}}}}, "id": difference_canvas_id}:
                                if self.show_canvas_updates:
                                    print(f"{self.now()} {GREEN}Received canvas update for canvas {AQUA}{difference_canvas_id}{R}")

                                difference_canvas_id = int(difference_canvas_id) - 2

                                if not self.canvas_parts[difference_canvas_id]:
                                    print(f"{self.now()} {RED} Got canvas update for part {AQUA}{difference_canvas_id}{RED} but we don't have that canvas part yet? Ignoring it.{R}")
                                    continue

                                while True:
                                    try:
                                        async with httpx.AsyncClient() as client:
                                            response = await client.get(difference_url)
                                        # response = requests.get(difference_url)
                                        diff_img = Image.open(BytesIO(response.content)).convert("RGBA")
                                        # img.save(f"diffs/{difference_canvas_id}_{time.time()}.png")

                                        # Paste the image
                                        self.canvas_parts[difference_canvas_id].paste(diff_img, (0, 0), diff_img)

                                        break
                                    except Exception as e:
                                        print(f"{self.now()} {YELLOW}Could not fetch difference canvas part {AQUA}{difference_canvas_id}{YELLOW}, {difference_url} trying again, {e}{R}")
                                    except websocket.exceptions.ConnectionClosedError:
                                        print(f'{self.now()} {RED}Live canvas got disconnected!{RESET}')

                            case {"type": "ka"}:
                                pass
                            case _:
                                print(f"{self.now()} {RED}Could not match live canvas message{RESET}", message, type(message))
            except websockets.ConnectionClosedError as e:
                print(f"{self.now()} {YELLOW} Reddit closed the live canvas connection. Reconnecting!{RESET}")
                self.message_id = 0b10

    @property
    def canvas(self) -> Image:
        """ Property that rebuilds the full_canvas in memory from the parts """

        for i in range(6):  # There are 6 canvases
            canvas_part = self.canvas_parts[i]
            x = 1000 * i % 3000
            y = 1000 if i > 2 else 0
            # print(i, x,y)
            self.full_canvas.paste(canvas_part, (x, y))

        return self.full_canvas

    def now(self):
        return f"{WHITE}[{datetime.datetime.now().strftime('%H:%M:%S')} Live Canvas]{RESET}"

    async def is_connected(self, delay=3):

        while True:
            await asyncio.sleep(delay)
            if self.connected:
                return


if __name__ == '__main__':
    config = load_config_without_auth()
    livecanvas = LiveCanvas(config.reddit_uri_wss, config.canvas_indexes)

    asyncio.get_event_loop().run_until_complete(livecanvas.connect())
