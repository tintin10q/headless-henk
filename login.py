import argparse
import getpass
import os.path
import sys

import requests
import time
import json

import toml
from bs4 import BeautifulSoup

from colors import RED, GREEN, printc
from now import now

REDDIT_URL = "https://www.reddit.com"
LOGIN_URL = REDDIT_URL + "/login"
INITIAL_HEADERS = {
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en",
    "content-type": "application/x-www-form-urlencoded",
    "origin": REDDIT_URL,
    "sec-ch-ua": '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}


def get_reddit_token(username: str, password: str) -> str | None:
    s = requests.session()
    s.headers.update(INITIAL_HEADERS)

    s.get(REDDIT_URL)
    time.sleep(0.5)

    # Get csrf token from login page
    printc(f"{now()} {GREEN}Getting CSRF token...")
    r = s.get(LOGIN_URL)
    soup = BeautifulSoup(r.content, "html.parser")
    csrf_token = soup.find("input", {"name": "csrf_token"})["value"]
    time.sleep(0.5)

    # Login
    printc(f"{now()} {GREEN}Logging in...")
    r = s.post(LOGIN_URL, data={
        "username": username,
        "password": password,
        "dest": REDDIT_URL,
        "csrf_token": csrf_token
    })
    time.sleep(0.5)
    if r.status_code != 200:
        printc(f"{now()} {RED}Login failed! Most likely you've entered an invalid password.")
        return None
    else:
        printc(f"{now()} {GREEN}Login successful!")

    # Get new access token
    printc(f"{now()} {GREEN}Getting {RED}reddit{GREEN} access token...")
    r = s.get(REDDIT_URL)
    soup = BeautifulSoup(r.content, features="html.parser")
    data_str = soup.find("script", {"id": "data"}).contents[0][len("window.__r = "):-1]
    data = json.loads(data_str)
    token = 'Bearer ' + data["user"]["session"]["accessToken"]

    return token


import config


def cli():
    username = input("usename:")
    password = getpass.getpass('password:')
    token = get_reddit_token(username, password)
    if not token:
        return

    print(token, file=sys.stderr)

    if input(f"Do you want to add this token to {config.configfilepath} (y/n)").lower() in ('y',):
        if not os.path.exists(config.configfilepath):
            config.create_default_config(config.configfilepath)

        with open(config.configfilepath, 'r') as config_file:
            configdata = toml.load(config_file)

        configdata['auth_token'] = token

        with open(config.configfilepath, 'w') as config_file:
                toml.dump(configdata, config_file)
        print(f"{now()} Token added to config file!")


if __name__ == '__main__':
    cli()
