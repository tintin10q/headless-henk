
from client import Client
from config import load_config, Config
import asyncio


async def main():
    config = load_config()

    # make client
    client = Client(config)
    await client.connect()


def gaan():
    asyncio.get_event_loop().run_until_complete(main())





if __name__ == '__main__':
    gaan()
