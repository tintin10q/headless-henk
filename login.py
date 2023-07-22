import requests
import time
import json
from bs4 import BeautifulSoup

REDDIT_URL = "https://www.reddit.com"
LOGIN_URL = REDDIT_URL + "/login"
INITIAL_HEADERS = {
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en",
    "content-type": "application/x-www-form-urlencoded",
    "origin": REDDIT_URL,
    "sec-ch-ua": '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}

def get_token(username: str, password: str) -> str:
    s = requests.session()
    s.headers.update(INITIAL_HEADERS)

    s.get(REDDIT_URL)
    time.sleep(0.5)

    # Get csrf token from login page
    print("Getting CSRF token...")
    r = s.get(LOGIN_URL)
    soup = BeautifulSoup(r.content, "html.parser")
    csrf_token = soup.find("input", {"name": "csrf_token"})["value"]
    time.sleep(0.5)

    # Login
    print("Logging in...")
    r = s.post(LOGIN_URL, data={
                "username": username,
                "password": password,
                "dest": REDDIT_URL,
                "csrf_token": csrf_token
            })
    time.sleep(0.5)
    if r.status_code != 200:
        print("Login failed! Most likely you've entered an invalid password.")
        return
    else:
        print("Login successful!")

    # Get new access token
    print("Getting access token...")
    r = s.get(REDDIT_URL)
    soup = BeautifulSoup(r.content, features="html.parser")
    data_str = soup.find("script", {"id": "data"}).contents[0][len("window.__r = "):-1]
    data = json.loads(data_str)
    token = 'Bearer ' + data["user"]["session"]["accessToken"]

    return token
