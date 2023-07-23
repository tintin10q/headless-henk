# Headless Henk

A headless [placeNL](https://github.com/PlaceNL/Chief) client written in [python](https://www.python.org/) 3.10.
This client has the advantage of using much less RAM than the headless firefox client.

# TLDR

The easies way to run Henk is using docker.

1. Create an `accounts.toml` file somewhere
2. In `accounts.toml` fill in your reddit accounts lke this:

```toml 
username1 = "password1"
username2 = "password2"
username3 = "password3"
```

3. Download the [docker-compose.yml](https://raw.githubusercontent.com/tintin10q/headless-henk/main/docker-compose.yml)
   file (wget https://raw.githubusercontent.com/tintin10q/headless-henk/main/docker-compose.yml) to the same directory
   as `accounts.toml`
3. Run `docker compose up -d`
4. Run `docker compose logs` to show Henk's logs
5. run `docker compose down` to stop Henk.

If you do not have docker installed run `curl -sSL https://get.docker.com/ | CHANNEL=stable bash` for
windows [use this guide](https://www.geeksforgeeks.org/how-to-install-docker-on-windows/)

If you have trouble running the docker check out Run Henk with Poetry below. That method is also pretty easy.

> This login method does not work with accounts with 2 factor authentication, disable it. If you have 2fa use the `auth_token` config.

# Runnning Henk

You can run henk in 3 ways. Using [poetry](https://python-poetry.org/docs/), [pip](https://pypi.org/project/pip/)
or [docker](https://www.docker.com/).

## Run Henk with Poetry

This is the easiest if you do not want to use docker.

0. Clone the repo `git clone https://github.com/tintin10q/headless-henk.git` and open it in a shell
1. Install the dependencies by running `poetry install`
2. run `poetry run gaanmetdiebanaan`

### Instaling poetry

If you don't have [poetry](https://python-poetry.org/docs/) then install it with:

> **Linux Debian/Ubuntu based**:  `apt install python3-poetry`

> **Linux other** `curl -sSL https://install.python-poetry.org | python3 -`

> **Windows**: `(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -`

If you have problems with poetry just delete `poetry.lock` and try again.

**Again, you start the client with `poetry run gaanmetdiebanaan`**

## Run Henk with Docker

There is also a docker available at: [ghcr.io/tintin10q/headless-henk:latest](ghcr.io/tintin10q/headless-henk:latest).
This docker supports every linux architecture you can imagine, so you can use your (old) Raspberry Pi as wel!

> To install docker run `curl -sSL https://get.docker.com/ | CHANNEL=stable bash`

Create your `accounts.toml` file

Run `docker compose up -d`

It should just run.

If you want to edit your config you can edit the `config/config.toml` with you config. After editing,
run `docker compose restart`.

To stop the compose, run `docker compose down`

## Run Henk Using Pip

If you do not want to use poetry you can also just make a virtual environment yourself. Ensure you are
running `python3.10`, run `python --version`. Henk won't work with lower python than 3.10.

First create `accounts.toml` as described and then run:

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python gaanmetdiebanaan.py
```

# Configuration

You can configure Henk with using a config [toml](https://toml.io/) file or using env vars.

**You can place 1 account in this configuration. If you want to use multiple accounts in the same process you have to
use an `accounts.toml`.**

- You can configure the name of the `accounts.toml` with the `--accounts` flag.
- You can configure the name of the `config.toml` with the `--config` flag.

## Accounts Toml File

The [accounts.toml](accounts.toml) file is very simple. It is just `username="password"` on every line. Like this:

```toml
username1 = "password1"
username2 = "password2"
username3 = "password3"
```

If you have weird characters in your username then this is also a valid accounts.toml:

```toml
"us.er.name1" = "password1"
"us er name2" = "password2"
username3 = "password3"
```

You can configure the name of the `accounts.toml` with the `--accounts` flag.

## Toml Config File

You can set the options in a toml configuration file. By default, this file is [config.toml](config.toml) in the same
directory as the program.
You can also change where this file is located using the `--config` flag.

If you start the program without a config file nor an accounts.toml present a basic config file will be created for you.

This is what the default file looks like:

```toml
reddit_username = 'ENTER USERNAME HERE!'
reddit_password = 'ENTER PASSWORD HERE!'
chief_host = "chief.placenl.nl"
reddit_uri_https = 'https://gql-realtime-2.reddit.com/query'
reddit_uri_wss = 'wss://gql-realtime-2.reddit.com/query'
canvas_indexes = ["0", "1", "2", "3", "4", "5"]  # Canvas indexes to download, Toml has no null we use 'None' 
stats = false   # Wether to subscribe to stats updates from chief
pingpong = false   # Whether the client should show ping and pong messages.
save_images = false   # Whether the client should save images, canvas.png prioritymap.png and chieftemplate.png
```

In the config file you can only use 1 account, if you want to use multiple accounts in one process use
an `accounts.toml`.

### Using an auth token instead of username

Instead of having `reddit_username` and `reddit_password` you can also have:

```toml
auth_token = "INSERT TOKEN HERE"
```

But if you do specify a `reddit_username` and `reddit_password` then the token will not refresh, and you have to replace
it every 24 hours. Whenever you replace the token it will work for another 24 hours.

See the [How to get a reddit jwt token](https://github.com/tintin10q/headless-henk#how-to-get-reddit-jwt) section for
information on how to get a reddit jwt token.

If you use the `auth_token` config it is still good to specify only `reddit_username` as this will still show up in the
logs. The auth token is still used as long as you do not specify a `reddit_password`.

## Env Vars

To use env vars you first have to set either the `PLACENL_AUTH_TOKEN` or both `PLACENL_REDDIT_USERNAME`
and `PLACENL_REDDIT_PASSWORD`.
If the `PLACENL_AUTH_TOKEN` or both `PLACENL_REDDIT_USERNAME` and `PLACENL_REDDIT_PASSWORD` env var are set then any
config.toml file is ignored, and you can set the other vars as
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
| PLACENL_SAVE_IMAGES      | false                                   | Whether the client should save images it receives. canvas.png, prioritymap.png and chieftemplate.png                                                           |

Because of the defaults you only have to set `PLACENL_AUTH_TOKEN`.

Here is a bash script which sets default env vars

> Note that in the toml file the `canvas_indexes` are all strings. In the env var this different and it is a json array
> of numbers and null.

```bash
export PLACENL_REDDIT_USERNAME="ADD USERNAME HERE" 
export PLACENL_REDDIT_PASSWORD="ADD PASSWORD HERE" 
export PLACENL_CHIEF_HOST="chief.placenl.nl"
export PLACENL_REDDIT_URI_HTTPS="https://gql-realtime-2.reddit.com/query"
export PLACENL_REDDIT_URI_WSS="wss://gql-realtime-2.reddit.com/query"
export PLACENL_CANVAS_INDEXES="[0, 1, 2, 3, 4, 5]"
export PLACENL_SUBSCRIBE_STATS="false"
export PLACENL_PINGPONG="false"
export PLACENL_SAVE_IMAGES="false"
```

If an `accounts.toml` file is present the contents of `PLACENL_REDDIT_PASSWORD`,  `PLACENL_REDDIT_USERNAME` and `PLACENL_REDDIT_AUTH_TOKEN` env vars are ignored.

# How to get reddit jwt?

You don't need a reddit jwt because you can just log in using an account and password. If you want to use multiple
accounts create an `account.toml` and run Henk.

If you do want to run with a token then The easiest way is to just run `login.py` to get a token. This will also
automatically add the token to
the `config.toml`. You can also run `login.py` by doing `poetry run login`. Both running `login.py`
and  `poetry run login` support the --config flag.

If the login does it work

## You can also go to the website:

1. Go to r/place
2. Open dev tools by pressing `ctrl+shift+i`
3. Click on the network tab
4. Locate the pause button but do not press it, it looks like a stop button on chrome.
5. Place a pixel
6. Wait until you hear the success noice
7. Press the pause button to stop new request from coming in
8. Now in the list of request find a `post` request to `https://gql-realtime-2.reddit.com/query`
9. Click on the post request in the list
10. Click on `headers`
11. Find the Authorization header
12. Copy the value of the authorization header. It should start with `Bearer ` and then a bunch of letters seperated.
13. Make sure you copy the entire token, you can probably right-click

> Realize that these tokens are valid for about 1440 minutes. There is no auto token refresh functionality yet. This is
> also because I don't know how reddit refreshes their tokens. Let me know if you konw.

**Be sure to not share this jwt with others! It is basically the same as sharing your password!**

# Downloading the Canvas

As a bonus feature you can run

```bash
poetry run downloadcanvas
``` 

to download the canvas. You don't have to put your auth token in `config.toml` or create an `acounts.toml` for this to
work.

<br>
<br>
<br>

[Disclaimer](./disclaimer.md)