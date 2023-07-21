import time

from client import Client
from config import load_config, Config
import asyncio


async def main():
    config = load_config()

    # make client
    client = Client(config)
    await client.connect()


def gaan():
    while True:

        try:
            asyncio.get_event_loop().run_until_complete(main())
        except Exception as e:
            print("Sometimg failed at the highest level", e)
            print("We are just going to wait a bit and then restart")
            time.sleep(1)







if __name__ == '__main__':
    gaan()
