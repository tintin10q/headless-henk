
import toml
from dataclasses import dataclass

with open("config.toml", "r") as config_file:
    config_dict = toml.load(config_file)


@dataclass
class Config:
    port: int
    ip: str


match config_dict:
    case {
        "port": int(port),
        "ip": str(ip)
    }:
        config = Config(port, ip)
    case _:
        raise ValueError(f"invalid configuration: {config_dict}, we need at least ip and port fields")

# clean up locals
del config_file
