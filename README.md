# Headless Henk

A headless [placeNL](https://github.com/PlaceNL/Chief) client written in [python](https://www.python.org/) 3.10.

# Configuration

You can configure Henk with using a [toml](https://toml.io/) file or using env vars.

## Toml Config File

You can set the options in a toml configuration file. By default, this file is [config.toml](config.toml) in the same
directory as the program.
You can also change where this file is located using the `--config` flag.

If you start the program without a config file present a basic config file will be created for you.

This is what the default file looks like:

```toml
reddit_username = 'YOUHAVETOADDTHIS'
reddit_password = 'YOUHAVETOADDTHIS'
chief_host = "chief.placenl.nl"
reddit_uri_https = 'https://gql-realtime-2.reddit.com/query'
reddit_uri_wss = 'wss://gql-realtime-2.reddit.com/query'
canvas_indexes = ["0", "1", "2", "3", "4", "5"]  # Canvas indexes to download, Toml has no null we use 'None' 
stats = false   # Wether to subscribe to stats updates from chief
pingpong = false   # Whether the client should show ping and pong messages.
```

### Using an auth token instead of username

Instead of having `reddit_username` and `reddit_password` you can also have:

```toml
auth_token = "INSERT TOKEN HERE"
```

But if you do not have `reddit_username` and `reddit_password` then the token will not refresh, and you have to replace it every 24 hours.

See the `How to get a reddit jwt token` section for information on how to get a reddit jwt token. 

> Note that in the toml file the `canvas_indexes` are all strings. In the env var this different and it is a json array
> of numbers and null.

## Env Vars

To use env vars you first have to set either the `PLACENL_AUTH_TOKEN` or both `PLACENL_REDDIT_USERNAME` and `PLACENL_REDDIT_PASSWORD`.
If the `PLACENL_AUTH_TOKEN` or both `PLACENL_REDDIT_USERNAME` and `PLACENL_REDDIT_PASSWORD` env var are set then any config.toml file is ignored, and you can set the other vars as
described in this table:

| Name                     | Default                                 | Description                                                                                                                                                    |   
|--------------------------|-----------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------|
| PLACENL_AUTH_TOKEN       |                                         | The reddit jwt token to use. See the `How to get reddit jwt` section                                                                                           |
| PLACENL_REDDIT_USERNAME  |                                         | The reddit username you want to use                                                                                                                            |
| PLACENL_REDDIT_PASSWORD  |                                         | The reddit password you want to use                                                                                                                            | 
| PLACENL_CHIEF_HOST       | chief.placenl.nl                        | The host of the PlaceNL chief instance                                                                                                                         |
| PLACENL_REDDIT_URI_HTTPS | https://gql-realtime-2.reddit.com/query | The reddit https gql api endpoint                                                                                                                              | 
| PLACENL_REDDIT_URI_WSS   | wss://gql-realtime-2.reddit.com/query   | The reddit websocket gql api endpoint                                                                                                                          | 
| PLACENL_CANVAS_INDEXES   | [0, 1, 2, 3, 4, 5]                      | The canvas indexes to download, should be a json list with either 0-5 or null of exactly 6 elements                                                            | 
| PLACENL_SUBSCRIBE_STATS  | false                                   | Whether the client should subscribe to stats updates from chief. Stats are always shown once on startup. Valid values are t, true, f, false (case insensitive) |
| PLACENL_PINGPONG         | false                                   | Whether the client should show ping and pong messages.                                                                                                         |

Because of the defaults you only have to set `PLACENL_AUTH_TOKEN`.

Here is a bash script which sets default env vars

```bash
export PLACENL_REDDIT_USERNAME="ADD USERNAME HERE" 
export PLACENL_REDDIT_PASSWORD="ADD PASSWORD HERE" 
export PLACENL_CHIEF_HOST="chief.placenl.nl"
export PLACENL_REDDIT_URI_HTTPS="https://gql-realtime-2.reddit.com/query"
export PLACENL_REDDIT_URI_WSS="wss://gql-realtime-2.reddit.com/query"
export PLACENL_CANVAS_INDEXES="[0, 1, 2, 3, 4, 5]"
export PLACENL_SUBSCRIBE_STATS="false"
export PLACENL_PINGPONG="false"
```

# Runnning Henk

You can run henk in 3 ways. Using [poetry](https://python-poetry.org/docs/), [pip](https://pypi.org/project/pip/)
or [docker](https://www.docker.com/).

## Poetry

To install the dependencies run `poetry install`

### Instaling poetry 

If you don't have [poetry](https://python-poetry.org/docs/) then install it with:

> **Linux Debian/Ubuntu based**:  `apt install python3-poetry`
 
> **Linux other** `curl -sSL https://install.python-poetry.org | python3 -`

> **Windows**: `(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -`

If you have problems with poetry just delete `poetry.lock` and try again.

**Start the client with `poetry run gaanmetdiebanaan`**

## Docker

There is also a docker available at: [ghcr.io/tintin10q/headless-henk:latest](ghcr.io/tintin10q/headless-henk:latest).
This docker supports every linux architecture you can imagine, so you can use your (old) Raspberry Pi as wel!

For easy use, use docker compose:

`docker compose up -d`

edit the `config/config.toml` with you config. After editing, run `docker compose restart`.

To stop the compose, run `docker compose down`

## Using Pip

If you do not want to use poetry you can also just make a virtual environment yourself. Ensure you are
running `python3.10`, run `python --version`. Henk won't work with lower python than 3.10.

```bash
python -m venv .venv
. .venv/bin/activate
python gaanmetdiebanaan.py
```


# How to get reddit jwt?

The easiest way is to just run `login.py` to get a token. This will also automatically add the token to the `config.toml`.
You can also run `login.py` by doing `poetry run login`. These also support the --config flag.

You can also go to the website:

1. Go to r/place
2. Open dev tools by pressing `ctrl+shift+i`
3. Click on the network tab
4. Locate the pause button but do not press it, it looks like a stop button on chrome.
4. Now in the list of request find a `post` request to `https://gql-realtime-2.reddit.com/query`
5. Press the pause button to stop new request from coming in
6. Click on the post request in the list
7. Click on `headers`
8. Find the Authorization header
9. Copy the value of the authorization header. It should start with `Bearer ` and then a bunch of letters seperated.

> Realize that these tokens are valid for about 1440 minutes. There is no auto token refresh functionality yet. This is
> also because I don't know how reddit refreshes their tokens. Let me know if you konw.

**Be sure to not share this jwt with others!**


# Downloading the Canvas

As a bonus feature you can run

```bash
poetry run downloadcanvas
``` 

to download the canvas. You don't have to put your auth token in `config.toml` for this to work.

<br>
<br>
<br>

[Disclaimer](./disclaimer.md)