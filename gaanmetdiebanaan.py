import os.path
import time

import websockets

import reddit
from client import Client
from colors import GREEN, RED, RESET, AQUA
from config import load_config, load_accounts, accountsfilepath, load_config_without_auth_without_cache
import asyncio

from now import now

import login


async def run_with_accounts_toml():
    print(f"{now()} {GREEN}Detected {accountsfilepath}")

    accounts = load_accounts()
    configs = []

    for account in accounts:
        config = load_config_without_auth_without_cache()

        config.reddit_username = account.reddit_username
        config.reddit_password = account.reddit_password

        config.auth_token = login.get_reddit_token(account.reddit_username, account.reddit_password)

        if config.auth_token == None:  # try one more time
            print(f"{now()} {RED}Could not login for {AQUA}{account.reddit_username}{RED} trying one more time", RESET)
            config.auth_token = login.get_reddit_token(account.reddit_username, account.reddit_password)
        if config.auth_token == None:  # try one more time
            print(f"{now()} {RED}Could not login for {AQUA}{account.reddit_username}{RESET}")
            continue

        configs.append(config)

    clients = [Client(config) for config in configs]

    if not clients:
        print(f"{now()} {RED}There were no valid clients in {AQUA}{accountsfilepath}{RESET}. Make sure you have the right password. Change the accounts and try again.")
        return

    run_client_coreroutines = [Client.run_client(client, delay=index * 30) for index, client in enumerate(clients)]

    await asyncio.gather(*run_client_coreroutines)


async def metdiebanaan():
    if os.path.exists(accountsfilepath):
        await run_with_accounts_toml()
    else:
        config = load_config()
        # make client
        client = Client(config)
        await Client.run_client(client)


def gaan():
    asyncio.get_event_loop().run_until_complete(metdiebanaan())


if __name__ == '__main__':
    gaan()
