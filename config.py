import toml
from dataclasses import dataclass
from typing import TypedDict

from colors import RED, RESET, BLUE, PURPLE, YELLOW

import os

if not os.path.exists('./config.toml'):
    print(PURPLE, 'config.toml', RESET + YELLOW + "file not found. Created empty config file please fill it in auth_token", RESET)
    with open('config.toml', 'w+') as config_file:
        starter_config = {"auth_token": 'ENTER TOKEN HERE!', 'chief_host': 'chief.placenl.nl'}
        toml.dump(starter_config, config_file)
    exit(0)


class Brand(TypedDict):
    author: str
    version: str
    name: str


default_reddit_uri = 'https://gql-realtime-2.reddit.com/query'
default_chief_host = 'chief.placenl.nl'


@dataclass
class Config:
    auth_token: str
    chief_host: str = default_chief_host
    author: str = "Quinten-C"
    version: str = '0.1.0'
    name: str = 'Headless-Henk'
    reddit_uri: str = default_reddit_uri
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


def load_config() -> Config:
    global __config

    if __config is not None:
        return __config

    with open("config.toml", "r") as config_file:
        config_dict = toml.load(config_file)

        chief_host = config_dict.get("chief_host", default_chief_host)
        reddit_uri = config_dict.get("reddit_uri", default_reddit_uri)
        auth_token = config_dict.get("auth_token", None)
        stats = config_dict.get("stats", False)  # Subscribe to stats or not, default is not, they are always shown at the start once

        if auth_token and reddit_uri and chief_host:
            print(BLUE, "Starting with chief host:", RESET, PURPLE, chief_host, RESET, YELLOW + "Custom chief host be careful" + RESET if chief_host != default_chief_host else "")
            print(BLUE, "Starting with reddit api host:", RESET, PURPLE, reddit_uri, RESET, YELLOW + "Custom reddit host be careful" + RESET if reddit_uri != default_reddit_uri else "")
            if not auth_token.startswith("Bearer "):
                print(RED, "Invalid auth token, it should begin with 'Bearer '", RESET)
                exit(1)
            __config = Config(auth_token=auth_token, chief_host=chief_host, stats=stats, reddit_uri=reddit_uri)
            return __config
        else:
            print(RED, "Missing auth_token ")
            exit(1)
