import time

import reddit
from client import Client
from config import load_config, Config
import asyncio

from reddit import Coordinates


async def main():
    config = load_config()

    # make client
    client = Client(config)
    await client.connect()


def gaan():
    # config = load_config()
    # coords = Coordinates(3, 600, 1)
    # reddit.place_pixel(config, coords, 3)

    asyncio.get_event_loop().run_until_complete(main())


if __name__ == '__main__':
    gaan()
