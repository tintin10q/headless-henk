import toml
from dataclasses import dataclass
from typing import TypedDict, List, Literal

from colors import BOLD, RESET

import argparse
import sys

parser = argparse.ArgumentParser(description="Headless Henk", epilog=f"The headless {BOLD}placeNL{RESET} autoplacer writen in python.")
parser.add_argument('--config', help="Location of the toml config file", default='config.toml')
args = parser.parse_args()

configfilepath = args.config

from colors import RED, RESET, BLUE, PURPLE, YELLOW, GREEN

import os

if not os.path.exists(configfilepath):
    print(PURPLE, configfilepath, RESET + YELLOW + "file not found. Try to create empty config file please fill it in with your auth_token", RESET)
    with open(configfilepath, 'w+') as config_file:
        starter_config = {"auth_token": 'ENTER TOKEN HERE!', 'chief_host': 'chief.placenl.nl', 'stats': False}
        toml.dump(starter_config, config_file)
    exit(0)


class Brand(TypedDict):
    author: str
    version: str
    name: str


default_chief_host = 'chief.placenl.nl'

default_reddit_uri_https = 'https://gql-realtime-2.reddit.com/query'
default_reddit_uri_wss = 'wss://gql-realtime-2.reddit.com/query'


@dataclass
class Config:
    auth_token: str
    # image_ids (list): A list of canvas IDs representing the available parts. Use None for missing parts.
    canvas_indexes: List[Literal[0, 1, 2, 3, 4, 5, None]]
    chief_host: str = default_chief_host
    author: str = "Quinten-C"
    version: str = '0.1.0'
    name: str = 'Headless-Henk'
    reddit_uri_https: str = default_reddit_uri_https
    reddit_uri_wss: str = default_reddit_uri_wss
    stats: bool = False

    def get_brand_payload(self) -> Brand:
        brand = {
            "author": self.author,
            "name": self.name
        }
        if self.version:
            brand['version'] = self.version
        return brand


__config = None


def load_config(ignore_missing_auth: bool = False) -> Config:
    global __config

    if __config is not None:
        return __config

    with open(configfilepath, "r") as config_file:
        config_dict = toml.load(config_file)

        chief_host = config_dict.get("chief_host", default_chief_host)
        reddit_uri_https = config_dict.get("reddit_uri_https", default_reddit_uri_https)
        reddit_uri_wss = config_dict.get("reddit_uri_wss", default_reddit_uri_wss)
        auth_token = config_dict.get("auth_token", None)
        stats = config_dict.get("stats", False)  # Subscribe to stats or not, default is not, they are always shown at the start once
        canvas_ids = config_dict.get("canvas_indexes", [None, 1, 3, None, 4, 5])  # The canvas ids to watch

        if (ignore_missing_auth or auth_token) and reddit_uri_wss and reddit_uri_https and chief_host:
            print(BLUE, "Starting with chief host:", RESET, PURPLE, chief_host, RESET, YELLOW + "Custom chief host be careful" + RESET if chief_host != default_chief_host else "")
            print(BLUE, "Starting with reddit api host:", RESET + PURPLE + reddit_uri_https, BLUE + "and", PURPLE + reddit_uri_wss, RESET,
                  YELLOW + "Custom reddit host be careful" + RESET if reddit_uri_https != reddit_uri_https or reddit_uri_wss != default_reddit_uri_wss else "")

            if not ignore_missing_auth and not auth_token.startswith("Bearer "):
                print(RED, "Invalid auth token, it should begin with 'Bearer '", RESET)
                exit(1)
            __config = Config(auth_token=auth_token, chief_host=chief_host, stats=stats, reddit_uri_wss=reddit_uri_wss, reddit_uri_https=reddit_uri_https, canvas_indexes=canvas_ids)
            return __config
        else:
            print(RED, "Missing auth_token ")
            exit(1)
