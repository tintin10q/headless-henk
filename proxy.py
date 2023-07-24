import os
from typing import Tuple

from colors import GREEN, AQUA, RESET
from config import parse_env_bool, configfilepath

import toml

from now import now

"""

You can configure a proxy in two ways. 

Using the config.toml or using env vars.
You have to set use_proxy to true for it to work

"""

# @dataclass
# class Proxy:
#    use: bool = False
#    ip: str = None
#    username: str = None
#    password: str = None

use = False
ip: str | None = None  # maybe this should be a list
username: str | None = None
password: str | None = None
use_https: bool | None

proxy_dict = None

proxy_auth: Tuple[str, str] | None = None

if not proxy_dict:
    if 'PLACENL_USE_PROXY' in os.environ:
        use = parse_env_bool(os.environ['PLACENL_USE_PROXY'], False, 'PLACENL_USE_PROXY')
        ip = os.environ.get("PLACENL_PROXY_IP", None)
        username = os.environ.get("PLACENL_PROXY_USERNAME", None)
        password = os.environ.get("PLACENL_PROXY_PASSWORD", None)
        use_https = parse_env_bool("PLACENL_PROXY_USE_HTTPS", False, 'PLACENL_PROXY_USE_HTTPS')

        protocol = 'https' if use_https else 'http'
        proxy_dict = {
            'https': 'https://' if use_https else 'http://' + ip,
            'http': 'http://' + ip
        }
        print(f"{now()} {GREEN}Using proxy: {AQUA}{protocol}://{ip}{RESET}")
        if username and password:
            proxy_auth = (username, password)
    else:
        if os.path.exists(configfilepath):
            # Using config.toml
            with open(configfilepath) as configfile:
                config_dict = toml.load(configfile)

                use = config_dict.get("use_proxy", False)
                if use:
                    ip = os.environ.get("proxy_ip", None)
                    username = os.environ.get("proxy_username", None)
                    password = os.environ.get("proxy_password", None)
                    use_https = os.environ.get("proxy_use_https", None)

                    protocol = 'https' if use_https else 'http'

                    print(f"{now()} {GREEN}Using proxy: {AQUA}{protocol}://{ip}{RESET}")

                    proxy_dict = {
                        'https': 'https://' if use_https else 'http://' + ip,
                        'http': 'http://' + ip
                    }
                    if username and password:
                        print(f"{now()} {GREEN}Proxy username: {AQUA}{username}{RESET}")
                        print(f"{now()} {GREEN}Proxy password: {AQUA}{'*' * len(password)}{RESET}")
                        proxy_auth = (username, password)
