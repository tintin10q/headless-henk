# Headless Henk
A headless [placeNL](https://github.com/PlaceNL/Chief) client written in [python](https://www.python.org/).

To install the dependencies run `poetry install` 

> If you don't have [poetry](https://python-poetry.org/docs/) then install it with:
>
> **Linux**: `curl -sSL https://install.python-poetry.org | python3 -`
> 
> **Windows**: `(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -` 

If you have problems with poetry just delete `poetry.lock` and try again.

**Start the client with `poetry run gaanmetdiebanaan`**

This will start the client. It will probably stop the client right away and create a [config.toml](config.toml) file. You have to insert your reddit jwt into this config file under `auth_token` field. 


## How to get reddit jwt?

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

**Be sure to not share this jwt with others!**

There is also a docker available at: 

<h2 style="color: red; font-size:15pt"> Werkt nog niet. Maar kan wel de brand updaten :)</h2>
