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
    author: str = "quinten_c"
    version: str = '0.1.0'
    name: str = 'placeNL_headless'
    reddit_uri: str = default_reddit_uri

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

    match config_dict:
        # Deze heeft chief host, reddit_host en auth_token
        case {"chief_host": str(chief_host), "reddit_host": str(reddit_host), "auth_token": str(auth_token)}:
            print(BLUE, "Starting with chief host:", RESET, PURPLE, chief_host, RESET, YELLOW + "Custom chief host be careful" + RESET if chief_host != default_chief_host else "")
            print(BLUE, "Starting with reddit api host:", RESET, PURPLE, reddit_host, RESET, YELLOW + "Custom reddit host be careful" + RESET if reddit_host != default_reddit_uri else "")
            if not auth_token.startswith("Bearer "):
                print(RED, "Invalid auth token, it doesn't start with 'Bearer '", RESET)
                exit(1)
            __config = Config(auth_token=auth_token, chief_host=chief_host)
        # Deze heeft alleen chief host
        case {"chief_host": str(chief_host), "auth_token": str(auth_token)}:
            print(BLUE, "Starting with chief host:", RESET, PURPLE, chief_host, RESET, YELLOW + "Custom chief host be careful" + RESET if chief_host != default_chief_host else "")
            print(BLUE, "Starting with reddit api host:", RESET, PURPLE, default_reddit_uri, RESET)
            if not auth_token.startswith("Bearer "):
                print(RED, "Invalid auth token, it doesn't start with 'Bearer '", RESET)
                exit(1)
            __config = Config(auth_token=auth_token, chief_host=chief_host)
            return Config(auth_token=auth_token, chief_host=chief_host)
        case _:
            print(f"{RED}Invalid configuration: we need {RESET}{BLUE}chief_host{RESET} {RED}fields{RESET}")
            exit(1)
