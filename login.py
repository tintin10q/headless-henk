import base64
import getpass
import os.path
import sys

import config

import requests
import time
import json

import toml
from bs4 import BeautifulSoup

from colors import RED, GREEN, printc, RESET, YELLOW, AQUA
from now import now_usr

REDDIT_URL = "https://www.reddit.com"
LOGIN_URL = REDDIT_URL + "/login"
INITIAL_HEADERS = {
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en",
    "content-type": "application/x-www-form-urlencoded",
    "origin": REDDIT_URL,
    # # these headers seem to break the login
    # "sec-ch-ua": '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
    # "sec-ch-ua-mobile": "?0",
    # "sec-ch-ua-platform": '"Windows"',
    # "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}


def get_reddit_token(username: str, password: str) -> str | None:
    print(f"{now_usr()} {GREEN}Logging into {RED}reddit{GREEN} with {AQUA}{username}{RESET}")
    s = requests.session()
    s.headers.update(INITIAL_HEADERS)

    s.get(REDDIT_URL)
    time.sleep(0.5)

    # Get csrf token from login page
    printc(f"{now_usr(username=username)} {GREEN}Getting CSRF token...")
    r = s.get(LOGIN_URL)
    soup = BeautifulSoup(r.content, "html.parser")
    csrf_token = soup.find("input", {"name": "csrf_token"})["value"]
    time.sleep(0.5)

    # Login
    printc(f"{now_usr(username=username)} {GREEN}Logging in...")
    r = s.post(LOGIN_URL, data={
        "username": username,
        "password": password,
        "dest": REDDIT_URL,
        "csrf_token": csrf_token
    })
    time.sleep(0.5)
    if r.status_code != 200:
        try:
            response_json = r.json()
            if "explanation" in response_json:
                printc(f"{now_usr(username=username)} {YELLOW}{response_json['explanation']}{RESET}")
            elif "reason" in response_json:
                printc(f"{now_usr(username=username)} {response_json['reason']}")
        except:
            printc(f"{now_usr(username=username)} {RED}Login failed! Most likely you've entered an invalid password.")
        return None
    else:
        printc(f"{now_usr(username=username)} {GREEN}Login successful!")

    # Get new access token
    printc(f"{now_usr(username=username)} {GREEN}Getting {RED}reddit{GREEN} access token...")
    r = s.get(REDDIT_URL)
    soup = BeautifulSoup(r.content, features="html.parser")
    try:
        data_str = soup.find("script", {"id": "data"}).contents[0][len("window.__r = "):-1]
    except AttributeError:
        printc(f"{now_usr(username=username)} {RED}Login failed! Reddit did not return what we needed. It could help to set your reddit to the new ui")
        return None
    data = json.loads(data_str)
    token = 'Bearer ' + data["user"]["session"]["accessToken"]

    return token


def cli():
    username = input("usename:")
    password = getpass.getpass('password:')
    token = get_reddit_token(username, password)
    if not token:
        return

    print(token, file=sys.stderr)

    if input(f"Do you want to add this token to {config.configfilepath} (y/n):").lower() in ('y',):
        if not os.path.exists(config.configfilepath):
            config.create_default_config(config.configfilepath)

        with open(config.configfilepath, 'r') as config_file:
            configdata = toml.load(config_file)

        configdata['auth_token'] = token
        if 'reddit_username' in configdata:
            del configdata['reddit_username']
        if 'reddit_password' in configdata:
            del configdata['reddit_password']

        with open(config.configfilepath, 'w') as config_file:
            toml.dump(configdata, config_file)
        print(f"{now_usr(username=username)} Token added to config file!")


def base64url_decode(data):
    # Add padding if the data length is not a multiple of 4
    padding_needed = len(data) % 4
    if padding_needed:
        data += b'=' * (4 - padding_needed)

    return base64.urlsafe_b64decode(data)


def decode_jwt_and_get_expiry(jwt_token: str):
    if jwt_token.startswith("Bearer "):
        jwt_token = jwt_token[7:]

    try:
        # JWT consists of three parts: header, payload, and signature
        header, payload, _ = jwt_token.split('.')

        # Decode the payload
        decoded_payload = base64url_decode(payload.encode('utf-8'))

        # Convert the decoded payload to a JSON object
        payload_data = json.loads(decoded_payload)

        # Extract the expiration time (exp) from the payload
        expiration_time = payload_data.get('exp')
        return expiration_time
    except (ValueError, IndexError) as e:
        print(f"{now_usr()} {RED} Token does not have an expiry date!")
        # Raised when decoding or parsing the JWT fails
        raise e


def is_expired(auth_token_expires_at: float) -> bool:
    return auth_token_expires_at and auth_token_expires_at < time.time()


def refresh_token_if_needed(config_object: config.Config):
    if is_expired(config_object.auth_token_expires_at):
        print(f"{now_usr(username=config_object.reddit_username)} {YELLOW}Auth token is expired!", RESET)
        if config_object.reddit_username and config_object.reddit_password:
            print(f"{now_usr(username=config_object.reddit_username)} {GREEN}Trying to refresh token we will try 5 times{RESET}")
            for _ in range(5):
                new_token = get_reddit_token(config_object.reddit_username, config_object.reddit_password)
                if new_token:
                    config.auth_token = new_token
                    break
            else:
                print(f"{now_usr(username=config_object.reddit_username)} {RED}Could not refresh reddit token after 5 tries there is nothing we can do'", RESET)
                raise CouldNotRefreshToken()
        else:
            print(f"{now_usr(username=config_object.reddit_username)} {RED}No username and passwort so there is nothing we can do'", RESET)
            raise CouldNotRefreshToken()


class CouldNotRefreshToken(Exception):
    pass


if __name__ == '__main__':
    cli()
