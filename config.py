import json

import toml
from dataclasses import dataclass
from typing import TypedDict, List, Literal

from colors import BOLD, RESET, AQUA

import argparse
import sys
from colors import RED, RESET, BLUE, PURPLE, YELLOW, GREEN

import os

from now import now

parser = argparse.ArgumentParser(description="Headless Henk", epilog=f"The headless {BOLD}placeNL{RESET} autoplacer writen in python.")
parser.add_argument('--config', help="Location of the toml config file", default='config.toml')
args = parser.parse_args()

configfilepath = args.config


class Brand(TypedDict):
    author: str
    version: str
    name: str


default_chief_host = 'chief.placenl.nl'

default_reddit_uri_https = 'https://gql-realtime-2.reddit.com/query'
default_reddit_uri_wss = 'wss://gql-realtime-2.reddit.com/query'

default_canvas_indexes_json = '[0, 1, 2, 3, 4, 5]'
default_canvas_indexes: List[Literal[0, 1, 2, 3, 4, 5, None]] = [0, 1, 2, 3, 4, 5]
default_canvas_indexes_toml: List[Literal['0', '1', '2', '3', '4', '5', '6']] = ['0', '1', '2', '3', '4', '5']

default_stats = False
default_pingpong = False


@dataclass
class Config:
    auth_token: str
    reddit_username: str
    reddit_password: str
    #  A list of canvas IDs representing the available parts. Use None for missing parts.
    canvas_indexes: List[Literal[0, 1, 2, 3, 4, 5, None]]
    chief_host: str = default_chief_host
    author: str = "Quinten-C"
    version: str = '2.0.0'
    name: str = 'Headless-Henk'
    reddit_uri_https: str = default_reddit_uri_https
    reddit_uri_wss: str = default_reddit_uri_wss
    stats: bool = False
    pingpong: bool = False
    auth_token_expires_at: float = 0

    def get_brand_payload(self) -> Brand:
        brand = {
            "author": self.author,
            "name": self.name
        }
        if self.version:
            brand['version'] = self.version
        return brand


__config = None


def parse_canvas_index_json(canvas_indexes_json: str) -> List[Literal[0, 1, 2, 3, 4, 5, None]]:
    try:
        canvas_indexes: List[Literal[0, 1, 2, 3, 4, 5, None]] = json.loads(canvas_indexes_json)
        if len(canvas_indexes) != 6:
            print(f"{now()} {RED}Could not parse {AQUA}PLACENL_CANVAS_INDEXES{RED} env var. "
                  f"It should be a list of 6 elements only consisting out of 0-5 or null. "
                  f"Example: '{default_canvas_indexes_json}' "
                  f"{YELLOW}Using default canvas indexes instead = {default_canvas_indexes}")
            canvas_indexes = default_canvas_indexes

        for canvas_index in canvas_indexes:
            if canvas_index is not None and not canvas_index in (0, 1, 2, 3, 4, 5):
                print(f"{now()} {RED}Could not parse {AQUA}PLACENL_CANVAS_INDEXES{RED} env var. "
                      f"It should be a list of 6 elements only consisting out of 0-5 or null. "
                      f"Example: '{default_canvas_indexes_json}' "
                      f"{YELLOW}Using default canvas indexes instead = {default_canvas_indexes}")
                canvas_indexes = default_canvas_indexes
                break
    except json.JSONDecodeError:
        print(f"{now()} {RED}Could not parse {AQUA}PLACENL_CANVAS_INDEXES{RED} env var. It should be a list of 6 elements only consisting out of 0-5 or null. Going back to default: {default_canvas_indexes}")
        canvas_indexes = default_canvas_indexes

    return canvas_indexes


def load_config_from_env() -> Config:
    auth_token = os.environ.get('PLACENL_AUTH_TOKEN', None)
    reddit_username = os.environ.get('PLACENL_REDDIT_USERNAME', None)
    reddit_password = os.environ.get('PLACENL_REDDIT_PASSWORD', None)
    #  A list of canvas IDs representing the available parts. Use None for missing parts.
    canvas_indexes_json: str = os.environ.get('PLACENL_CANVAS_INDEXES', default_canvas_indexes_json)
    canvas_indexes = parse_canvas_index_json(canvas_indexes_json)

    chief_host: str = os.environ.get('PLACENL_CHIEF_HOST', default_chief_host)
    reddit_uri_https: str = os.environ.get("PLACENL_REDDIT_URI_HTTPS", default_reddit_uri_https)
    reddit_uri_wss: str = os.environ.get("PLACENL_REDDIT_URI_WSS", default_reddit_uri_wss)
    stats_str = os.environ.get("PLACENL_STATS", str(default_pingpong)).lower()  # Subscribe to stats or not, default is not, they are always shown at the start once

    match stats_str:
        case 't' | 'true':
            stats = True
        case 'f' | 'false':
            stats = False
        case _:
            print(f"{now()} invalid value for PLACENL_SUBSCRIBE_STATS, it should be t, true, f or false, it is also case insensitive. Using default = {default_stats}")
            stats = default_stats

    pingpong_str = os.environ.get("PLACENL_PINGPONG", str(default_pingpong)).lower()
    match pingpong_str:
        case 't' | 'true':
            pingpong = True
        case 'f' | 'false':
            pingpong = False
        case _:
            print(f"{now()} invalid value for PLACENL_PINGPONG, it should be t, true, f or false, it is also case insensitive. Using default = {default_stats}")
            pingpong = default_pingpong

    config = Config(auth_token=auth_token, reddit_username=reddit_username, reddit_password=reddit_password, chief_host=chief_host, stats=stats, reddit_uri_wss=reddit_uri_wss, reddit_uri_https=reddit_uri_https,
                    canvas_indexes=canvas_indexes, pingpong=pingpong)
    return config


def create_default_config(filename: configfilepath):
    with open(filename, 'w+') as config_file:
        # starter_config = {"auth_token": 'ENTER TOKEN HERE!', 'chief_host': default_chief_host, 'stats': default_stats, 'reddit_uri_https': default_reddit_uri_https, 'reddit_uri_wss': default_reddit_uri_wss,
        #                   'default_canvas_indexes': default_canvas_indexes_toml, "pingpong": False}

        starter_config = {"reddit_username": 'ENTER USERNAME HERE!', "reddit_password": 'ENTERPASSWORD', 'chief_host': default_chief_host, 'stats': default_stats, 'reddit_uri_https': default_reddit_uri_https,
                          'reddit_uri_wss': default_reddit_uri_wss,
                          'default_canvas_indexes': default_canvas_indexes_toml, "pingpong": False}
        toml.dump(starter_config, config_file)
        print(GREEN + f"Created {filename} with default config. You still need to enter your reddit jwt into this file though! See README for how to get the jwt." + RESET)


def load_config_from_toml_file(filename: str = configfilepath) -> Config:
    # First try to read from env var"reddit_username": 'ENTER USERNAME HERE!'s

    if not os.path.exists(filename):
        print(PURPLE + configfilepath, RESET + RED + f"file not found!", RESET)
        print(YELLOW + f"Attempting to create {filename} with a default config.{RESET}")
        create_default_config(filename)

        exit(0)

    # If that did not work look for the config file
    with open(filename, "r") as config_file:
        config_dict = toml.load(config_file)

    auth_token = config_dict.get("auth_token", None)
    reddit_username = config_dict.get("reddit_username", None)
    reddit_password = config_dict.get("reddit_password", None)
    chief_host = config_dict.get("chief_host", default_chief_host)
    reddit_uri_https = config_dict.get("reddit_uri_https", default_reddit_uri_https)
    reddit_uri_wss = config_dict.get("reddit_uri_wss", default_reddit_uri_wss)
    stats = config_dict.get("stats", False)  # Subscribe to stats or not, default is not, they are always shown at the start once
    canvas_indexes = config_dict.get("canvas_indexes", default_canvas_indexes)  # The canvas indexes to download
    pingpong = config_dict.get("pingpong", default_pingpong)

    for i in range(len(canvas_indexes)):
        if canvas_indexes[i] in (-1, 'null', 'none', 'None', 'skip'):
            canvas_indexes[i] = None
        elif canvas_indexes[i] in ('0', '1', '2', '3', '4', '5'):
            canvas_indexes[i] = int(canvas_indexes[i])
    config = Config(auth_token=auth_token, reddit_username=reddit_username, reddit_password=reddit_password, chief_host=chief_host, stats=stats, reddit_uri_wss=reddit_uri_wss, reddit_uri_https=reddit_uri_https,
                    canvas_indexes=canvas_indexes, pingpong=pingpong)
    return config


def load_config(ignore_missing_auth: bool = False) -> Config:
    global __config

    if __config is not None:
        return __config

    import login  # circular import otherwise

    # if "PLACENL_REDDIT_USERNAME" in
    using_env = "PLACENL_AUTH_TOKEN" in os.environ or ("PLACENL_REDDIT_USERNAME" in os.environ and "PLACENL_REDDIT_PASSWORD" in os.environ)

    if using_env:
        __config = load_config_from_env()
    else:
        __config = load_config_from_toml_file()

    if (__config.reddit_username and __config.reddit_password):

        if __config.reddit_username == "ENTER USERNAME HERE!":
            print(f"{now()}{RED}You did not configure your username it is still 'ENTER USERNAME HERE!'", RESET)
            exit()

        __config.auth_token = login.get_reddit_token(__config.reddit_username, __config.reddit_password)
        if not __config.auth_token:
            print(f"{now()} {RED}Could not login trying one more time", RESET)
            __config.auth_token = login.get_reddit_token(__config.reddit_username, __config.reddit_password)
        if not __config.auth_token:
            exit()  # if it failed again just quit

    if not ignore_missing_auth and not __config.auth_token.startswith("Bearer "):
        print(f"{now()}RED, Invalid auth token, it should begin with 'Bearer '", RESET)
        exit(1)

    if "…" in __config.auth_token:
        print(f"{now()} You have '…' character in your auth token. This means your browser truncated the token. Try copying it again and make sure you get the whole token.")
        exit()

    __config.auth_token_expires_at = login.decode_jwt_and_get_expiry(__config.auth_token)

    login.refresh_token_if_needed(__config)

    if (ignore_missing_auth or __config.auth_token) and __config.reddit_uri_wss and __config.reddit_uri_https and __config.chief_host:
        print(BLUE, "Starting Henk with chief host:", RESET, PURPLE, __config.chief_host, RESET, YELLOW + "Custom chief host be careful" + RESET if __config.chief_host != default_chief_host else "")
        print(BLUE, "Starting Henk with reddit api host:", RESET + PURPLE + __config.reddit_uri_https, BLUE + "and", PURPLE + __config.reddit_uri_wss, RESET,
              YELLOW + "Custom reddit host be careful" + RESET if __config.reddit_uri_https != __config.reddit_uri_https or __config.reddit_uri_wss != default_reddit_uri_wss else "")

        return __config
    print(RED, f"Invalid configuration{RESET}")
    exit(1)
