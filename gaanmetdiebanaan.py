
from client import Client
from config import load_config
import asyncio

from reddit import send_request, Coordinates

async def main():
    # make client
    client = Client(load_config())
    await client.connect()

    # coords = Coordinates(499, 999, 1)
    # config = load_config()
    # send_request(config.auth_token, coords)
    return

def gaan():
    asyncio.get_event_loop().run_until_complete(main())

if __name__ == '__main__':
    gaan()


