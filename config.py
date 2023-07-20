import toml
from dataclasses import dataclass
from typing import TypedDict

with open("config.toml", "r") as config_file:
    config_dict = toml.load(config_file)


class Brand(TypedDict):
    author: str
    version: str
    name: str


@dataclass
class Config:
    chief_host: str
    author: str = "quinten_cabo"
    version: str = '0.1.0'
    name: str = 'placeNL_headless'

    def get_brand_payload(self) -> Brand:
        brand = {
            "author": self.author,
            "name": self.name
        }
        if self.version:
            brand['version'] = self.version
        return brand


def load_config() -> Config:
    match config_dict:
        case {"chief_host": str(chief_host)}:
            return Config(chief_host)
        case _:
            raise ValueError(f"invalid configuration: {config_dict}, we need client_host fields")


# clean up locals
del config_file
