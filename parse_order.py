from dataclasses import dataclass
from types import NoneType
from typing import List

from colors import PURPLE, RESET, GREEN, AQUA


@dataclass
class Creator:
    name: str
    avatar: str


def creator_from_dict(payload: dict) -> Creator | None:
    match payload:
        case {"name": str(name), "avatar": str(avatar)}:
            return Creator(name, avatar)  # Todo parse avatar as url
        case _:
            return None


@dataclass
class Image:
    order: str  # The URL to the order image
    priority: str | None

    @staticmethod
    def from_dict(payload: dict) -> "Image":
        """ Create an image object from a dict"""
        match payload:
            case {"order": str(order), "priority": str(priority)}:
                return Image(order, priority)
            case {"order": str(order)}:
                return Image(order, priority=None)
            case _:
                raise ValueError("Could not parse image in order payload")


@dataclass
class Size:
    width: int
    height: int

    @staticmethod
    def from_dict(payload: dict) -> "Size":
        match payload:
            case {"width": int(width), "height": height}:
                return Size(width, height)
            case _:
                raise ValueError("Could not parse size object in order!")


@dataclass
class Offset:
    x: int
    y: int

    @staticmethod
    def from_dict(payload) -> "Offset":
        match payload:
            case {"x": int(x), "y": int(y)}:
                return Offset(x, y)
            case _:
                raise ValueError("Could not parse offset in order!")


@dataclass
class Order:
    id: str
    message: str | None
    createdAt: str
    # Can be None
    creator: Creator | None
    offset: Offset
    images: Image
    size: Size

    def __repr__(self) -> str:
        ln = '\n'
        result = f"{PURPLE}--== Order ==--{RESET}\n" \
                 f"{GREEN}Created at: {AQUA}{self.createdAt}{RESET}\n" \
                 f"{f'{GREEN}Created by: {AQUA}{self.creator.name}{RESET}{ln}' if self.creator else ''}" \
                 f"{f'{GREEN}Message: {AQUA}{self.message}{RESET}{ln}' if self.message else ''}" \
                 f"{GREEN}Offset: x={AQUA}{self.offset.x}{GREEN}, y={AQUA}{self.offset.y}{RESET}\n" \
                 f"{GREEN}Size: width={AQUA}{self.size.width}{GREEN}, height={AQUA}{self.size.height}{RESET}\n"
        return result


def parse_order(payload: dict) -> Order:
    """
    #### Payload

    | name      | type                | description                                                                                |
    |-----------|---------------------|--------------------------------------------------------------------------------------------|
    | id        | string (uuid)       |                                                                                            |
    | message   | string?             | The message describing the changes made in this order, or null if no message was provided. |
    | createdAt | string (datetime)   | The timestamp this order was created at                                                    |
    | creator   | object? (see below) | The user that created this order, or null if the user wishes to remain anonymous.          |
    | images    | object (see below)  | The images related to this order                                                           |
    | size      | object (see below)  | The size of the images related to the order                                                |
    | offset	| object (see below)  | The offset of the image on the canvas                                                      |

    ##### Creator Format

    | name   | type         | description                           |
    |--------|--------------|---------------------------------------|
    | name   | string       | The name of the creator               |
    | avatar | string (url) | The URL to the creator's avatar image |

    ##### Images Format

    | name     | type          | description                                                                                                    |
    |----------|---------------|----------------------------------------------------------------------------------------------------------------|
    | order    | string (url)  | The URL to the order image                                                                                     |
    | priority | string? (url) | The URL to the [priority mapping image](../client/PRIORITY-MAPPINGS.md), or null if the order doesn't have one |

    ##### Size Format

    | name   | type    | description                        |
    |--------|---------|------------------------------------|
    | width  | integer | The width of the images in pixels  |
    | height | integer | The height of the images in pixels |


    ##### Offset Format

    | name   | type    | description                              |
    |--------|---------|------------------------------------------|
    | x      | integer | The x offset of the image on the canvas  |
    | y      | integer | The y offset of the image on the canvas  |


    """
    match payload:
        case {"id": str(id), "message": message, "createdAt": str(createdAt), "creator": creator, "images": images, "size": size, "offset": offset}:

            if message is not None and not isinstance(message, str):
                raise ValueError("Invalid message in order! Neither a string or None!")

            creator = creator_from_dict(creator)  # can be null
            images = Image.from_dict(images)
            offset = Offset.from_dict(offset)
            size = Size.from_dict(size)

            order = Order(id=id, message=message, createdAt=createdAt, creator=creator, images=images, size=size, offset=offset)
            return order
        case _:
            raise ValueError("Could not parse order object!")


example_order = {'createdAt': '2023-07-20T22:56:11.310Z',
                 'creator': {'avatar': 'https://cdn.discordapp.com/avatars/320130072767889409/7b3140beca82327722fb9235b5af9b14.png',
                             'name': 'meinth'},
                 'id': '16f67468-0625-4c0c-82f6-805cb6021820',
                 'images': {'order': 'https://chief.placenl.nl/orders/16f67468-0625-4c0c-82f6-805cb6021820.png',
                            'priority': 'https://chief.placenl.nl/orders/16f67468-0625-4c0c-82f6-805cb6021820-priority.png'},
                 'message': 'Mark Rutte heeft weer prioriteit',
                 'offset': {'x': -500, 'y': -500},
                 'size': {'height': 1000, 'width': 1000}}
