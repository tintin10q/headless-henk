import requests

from config import load_config

from dataclasses import dataclass


@dataclass
class Coordinates:
    x: int
    y: int
    canvasIndex: int


def ui_to_req_coords(displayX, displayY) -> Coordinates:
    canvasX = (displayX + 500) % 1000
    canvasY = (displayY + 1000) % 1000
    if displayY < 0:
        if displayX < -500:
            canvas = 0
        elif displayX > 499:
            canvas = 2
        else:
            canvas = 1
    else:
        if displayX < -500:
            canvas = 3
        elif displayX > 499:
            canvas = 5
        else:
            canvas = 4
    return Coordinates(canvasX, canvasY, canvas)


config = load_config()

colorIndex = 3


VALID_COLORS = ['#6D001A', '#BE0039', '#FF4500', '#FFA800', '#FFD635', '#FFF8B8', '#00A368', '#00CC78', '#7EED56', '#00756F', '#009EAA', '#00CCC0', '#2450A4', '#3690EA', '#51E9F4', '#493AC1', '#6A5CFF', '#94B3FF', '#811E9F', '#B44AC0', '#E4ABFF', '#DE107F', '#FF3881', '#FF99AA', '#6D482F', '#9C6926', '#FFB470', '#000000', '#515252', '#898D90', '#D4D7D9', '#FFFFFF'];

def send_request(authorization: str, coords: Coordinates, color = 3):
    print("got to the reqeust")
    set_pixel = requests.post(config.reddit_uri,
                                  data=f"""{{\"operationName\":\"setPixel\",\"variables\":{{\"input\":{{\"actionName\":\"r/replace:set_pixel\",\"PixelMessageData\":{{\"coordinate\":{{\"x\":{coords.x},\"y\":{coords.y}}},\"colorIndex\":{colorIndex},\"canvasIndex\":{coords.canvasIndex}}}}}}},\"query\":\"mutation setPixel($input: ActInput!) {{\\n  act(input: $input) {{\\n    data {{\\n      ... on BasicMessage {{\\n        id\\n        data {{\\n          ... on GetUserCooldownResponseMessageData {{\\n            nextAvailablePixelTimestamp\\n            __typename\\n          }}\\n          ... on SetPixelResponseMessageData {{\\n            timestamp\\n            __typename\\n          }}\\n          __typename\\n        }}\\n        __typename\\n      }}\\n      __typename\\n    }}\\n    __typename\\n  }}\\n}}\\n\"}}""",
                                  headers={
                                      "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/114.0",
                                      "Accept": "*/*",
                                      "Accept-Language": "en-US,en;q=0.5",
                                      "content-type": "application/json",
                                      "authorization": authorization,
                                      "apollographql-client-name": "garlic-bread",
                                      "apollographql-client-version": "0.0.1",
                                      "Sec-Fetch-Dest": "empty",
                                      "Sec-Fetch-Mode": "cors",
                                      "Sec-Fetch-Site": "same-site"
                                  })
    print("set pixel", set_pixel.status_code)
    print("set pixel response", set_pixel.text)

def test_authorization(authorization: str):
    return requests.post(config.reddit_uri,
                                  data=f"""{{\"operationName\":\"setPixel\",\"variables\":{{\"input\":{{\"actionName\":\"r/replace:set_pixel\",\"PixelMessageData\":{{\"coordinate\":{{\"x\":{coords.x},\"y\":{coords.y}}},\"colorIndex\":{colorIndex},\"canvasIndex\":{coords.canvasIndex}}}}}}},\"query\":\"mutation setPixel($input: ActInput!) {{\\n  act(input: $input) {{\\n    data {{\\n      ... on BasicMessage {{\\n        id\\n        data {{\\n          ... on GetUserCooldownResponseMessageData {{\\n            nextAvailablePixelTimestamp\\n            __typename\\n          }}\\n          ... on SetPixelResponseMessageData {{\\n            timestamp\\n            __typename\\n          }}\\n          __typename\\n        }}\\n        __typename\\n      }}\\n      __typename\\n    }}\\n    __typename\\n  }}\\n}}\\n\"}}""",
                                  headers={
                                      "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/114.0",
                                      "Accept": "*/*",
                                      "Accept-Language": "en-US,en;q=0.5",
                                      "content-type": "application/json",
                                      "authorization": authorization,
                                      "apollographql-client-name": "garlic-bread",
                                      "apollographql-client-version": "0.0.1",
                                      "Sec-Fetch-Dest": "empty",
                                      "Sec-Fetch-Mode": "cors",
                                      "Sec-Fetch-Site": "same-site"
                                  }).status_code == 200
