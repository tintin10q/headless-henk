import time

import websockets

import reddit
from client import Client
from config import load_config, Config
import asyncio

from now import now
from reddit import Coordinates


async def metdiebanaan():
    config = load_config()
    # make client
    client = Client(config)

    while True:
        try:
            await client.connect()
        except (TimeoutError, asyncio.exceptions.TimeoutError):
            print(f"{now()} We got disconnected. Lets try connect again in 4 seconds")
            if client.place_timer:
                client.place_timer.cancel()
            if client.pong_timer:
                client.pong_timer.cancel()
            time.sleep(4)
        except (websockets.InvalidStatusCode):
            print(f"{now()} Server rejected connection. Lets try connect again in 10 seconds")
            if client.place_timer:
                client.place_timer.cancel()
            if client.pong_timer:
                client.pong_timer.cancel()
            time.sleep(10)
        except (websockets.WebSocketException):
            print(f"{now()} Websocket error. Lets try connect again in 10 seconds")
            if client.place_timer:
                client.place_timer.cancel()
            if client.pong_timer:
                client.pong_timer.cancel()
            time.sleep(10)
        else:  # If another error happened then just let it die
            break


def gaan():
    asyncio.get_event_loop().run_until_complete(metdiebanaan())


if __name__ == '__main__':
    gaan()
