import os.path
import random

from PixelClient import PixelClient
from chief import ChiefClient
from client import Client
from colors import GREEN, RED, RESET, AQUA, YELLOW, LIGHTRED, BLUE, WHITE
from config import load_config, load_accounts, load_tokens_cache_toml, accountsfilepath, load_config_without_auth_without_cache, cache_auth_token
import asyncio

from live_canvas import LiveCanvas
from now import now

import login


async def run_with_accounts_toml():
    print(f"{now()} {GREEN}Detected {AQUA}{accountsfilepath}{RESET}")

    accounts = load_accounts()
    configs = []

    tokens_cache = load_tokens_cache_toml()

    for account in accounts:
        config = load_config_without_auth_without_cache()

        config.reddit_username = account.reddit_username
        config.reddit_password = account.reddit_password

        # Check if we have a valid token in the cache
        if config.reddit_username in tokens_cache:
            config.auth_token = tokens_cache[config.reddit_username]
            print(f"{now()} {GREEN}Using cached reddit token for {AQUA}{account.reddit_username}", RESET)
            expires_at = login.decode_jwt_and_get_expiry(config.auth_token)
            if login.is_expired(expires_at):
                print(f"{now()} {YELLOW}Cached token for {AQUA}{account.reddit_username}{YELLOW} is expired fetching a new one", RESET)
                config.auth_token = login.get_reddit_token(account.reddit_username, account.reddit_password)
                cache_auth_token(username=config.reddit_username, token=config.auth_token)
        else:
            # no valid token found in the cache fetch a new one and cache it
            config.auth_token = login.get_reddit_token(account.reddit_username, account.reddit_password)
            cache_auth_token(username=config.reddit_username, token=config.auth_token)

        # Check if we now have a valid token
        if config.auth_token == None:  # try one more time to login
            print(f"{now()} {RED}Could not login for {AQUA}{account.reddit_username}{RED} trying one more time", RESET)
            config.auth_token = login.get_reddit_token(account.reddit_username, account.reddit_password)
            cache_auth_token(username=config.reddit_username, token=config.auth_token)

        if config.auth_token == None:  # try one more time
            print(f"{now()} {RED}Could not login for {AQUA}{account.reddit_username}{RESET}")
            continue

        configs.append(config)


    if not configs:
        print(f"{now()} {LIGHTRED}There were no valid clients in {AQUA}{accountsfilepath}{RESET}. {BLUE}Make sure you have an internet connection and the right password. Change the accounts and try again.{RESET}")
        return

    # We actually have clients, make a connection to chief
    config = load_config_without_auth_without_cache()
    chief = ChiefClient(config.chief_host)
    live_canvas = LiveCanvas(config.reddit_uri_wss, config.canvas_indexes)
    clients = [PixelClient(config, chief, live_canvas) for config in configs]

    run_client_coreroutines = [PixelClient.run(client, delay=index * 5) for index, client in enumerate(clients)]

    await asyncio.gather(chief.connect(), live_canvas.connect(), *run_client_coreroutines)


async def metdiebanaan():
    # Delete reddit session here just in case, so it stays more fresh, we only fetch it once per run
    if os.path.exists('reddit_session.json') and random.randint(0, 10) == 4:
        os.remove('reddit_session.json')

    if os.path.exists(accountsfilepath):
        await run_with_accounts_toml()
    else:
        config = load_config()
        print(f"{WHITE}Henk {AQUA}V{config.version}{RESET}")
        # make client
        client = Client(config)
        await Client.run_client(client)


def gaan():
    asyncio.get_event_loop().run_until_complete(metdiebanaan())


if __name__ == '__main__':
    gaan()
