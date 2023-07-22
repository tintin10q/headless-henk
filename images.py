import asyncio
from typing import List, Literal, Tuple

import httpx
from io import BytesIO
from PIL import Image

from colors import printc, GREEN, RESET, BLUE, RED
from now import now
from parse_order import Order
from canvas import build_canvas_image, colorTuple_to_colorIndex
import random
import math
from typing import Tuple


async def download_order_image(url):
    printc(f"{now()} {GREEN}Downloading order image from {BLUE}{url}{RESET}")
    async with httpx.AsyncClient() as client:
        response = await client.get(url, timeout=2 * 60)
    response.raise_for_status()

    order_img = Image.open(BytesIO(response.content))
    order_img.save("chieftemplate.png")
    return order_img

async def download_priority_image(url):
    printc(f"{now()} {GREEN}Downloading priority image from {BLUE}{url}{RESET}")
    async with httpx.AsyncClient() as client:
        response = await client.get(url, timeout=2 * 60)
    response.raise_for_status()

    priority_img = Image.open(BytesIO(response.content))
    priority_img.save("prioritymap.png")
    return priority_img


async def get_pixel_differences_with_download(order: Order, canvas_indexes: List[Literal[0, 1, 2, 3, 4, 5, None]]):
    """
    :param order:
    :param canvas_indexes: Put None on the missing indexes, so to fetch 1 and 4 you do [None, 1, None, None, 4, None]
    :return:
    """
    canvas, chief_template = await asyncio.gather(build_canvas_image(canvas_indexes), download_order_image(order.images.order))

    # we don't need to save this, but it's nice
    chief_template.save("chieftemplate.png")

    width, height = order.size.width, order.size.height

    offsetX = order.offset.x
    offsetY = order.offset.y

    diff_pixels = []

    for x in range(width):
        for y in range(height):
            template_pixel = chief_template.getpixel((x, y))

            if isinstance(template_pixel, int):
                print(f"{now()}{RED} THE TEMPLATE IS USING A 4 BIT PNG AND NOT 32 BIT PNG!{RESET}")
                return []

            if template_pixel[-1] == 0:
                continue

            canvas_pixel = canvas.getpixel((x + 1500 + offsetX, y + 1000 + offsetY))

            if canvas_pixel != template_pixel:
                diff_pixels.append((x + 1500 + offsetX, y + 1000 + offsetY, canvas_pixel, template_pixel, 0)) # add priority = 0, because we don't know the priority here

    del canvas, chief_template
    return diff_pixels


async def get_pixel_differences_with_canvas_download(order: Order, canvas_indexes: List[Literal[0, 1, 2, 3, 4, 5, None]], order_image: Image, priority_image: Image=None):
    """
    Only download the canvas and supply the order as an input
    :param order_image:
    :param order:
    :param canvas_indexes: Put None on the missing indexes, so to fetch 1 and 4 you do [None, 1, None, None, 4, None]
    :return:
    """
    canvas = await build_canvas_image(canvas_indexes)

    template_width, template_height = order.size.width, order.size.height

    offsetX = order.offset.x
    offsetY = order.offset.y

    # print(f"{template_width=}, {template_height=}, {offsetX=}, {offsetY=}, {canvas_indexes=}")

    diff_pixels = []

    for x in range(template_width):
        for y in range(template_height):
            template_pixel = order_image.getpixel((x, y))

            if isinstance(template_pixel, int):
                print(f"{now()}{RED} THE TEMPLATE IS USING A 4 BIT PNG AND NOT 32 BIT PNG!{RESET}")
                return []

            if template_pixel[-1] == 0:
                continue

            canvas_pixel = canvas.getpixel((x + 1500 + offsetX, y + 1000 + offsetY))

            if canvas_pixel != template_pixel:
                priority = 0
                if priority_image:
                    priority_pixel = priority_image.getpixel((x, y))
                    priority = calculate_priority(priority_pixel)
                    priority += math.floor(random.random() * 10000) # Increase randomness

                diff_pixels.append((x + 1500 + offsetX, y + 1000 + offsetY, canvas_pixel, template_pixel, priority))

    del canvas

    return diff_pixels

def calculate_priority(pixel: Tuple[int, int, int, int]) -> int:
    r, g, b, a = pixel
    if a == 0: return 0
    return (r << 16) + (g << 8) + b

def get_pixel_differences(canvas: Image, chief_template: Image) -> List[Tuple[int, int, Tuple[int, int, int, int], Tuple[int, int, int, int]]]:
    template_width, template_height = 2000, 1000
    offsetX, offsetY = -1000, -500

    diff_pixels = []

    for x in range(template_width):
        for y in range(template_height):
            template_pixel = chief_template.getpixel((x, y))

            if isinstance(template_pixel, int):
                print(f"{now()} {RED}THE TEMPLATE IS USING A 4 BIT PNG AND NOT 32 BIT PNG! {RESET}")
                return []
                # return find_pixel_differences_4bitcanvas(canvas, chief_template, template_width=template_width, template_height=template_height, offset_x=offsetX, offset_y=offsetY)

            if template_pixel[-1] == 0:
                continue

            canvas_pixel = canvas.getpixel((x + 1500 + offsetX, y + 1000 + offsetY))
            if canvas_pixel != template_pixel:
                print("not equal", canvas_pixel, template_pixel)
                diff_pixels.append((x + 1500 + offsetX, y + 1000 + offsetY, canvas_pixel, template_pixel))

    del canvas, chief_template

    return diff_pixels

def find_pixel_differences_4bitcanvas(canvas: Image, chief_template: Image, *, template_width, template_height, offset_x, offset_y) -> List[Tuple[int, int, Tuple[int, int, int, int], Tuple[int, int, int, int]]]:
    """ This does not work yet"""
    differences = []
    last = -1
    for x in range(template_width):
        for y in range(template_height):

            template_pixel = chief_template.getpixel((x, y))

            canvas_pixel = canvas.getpixel((x + 1500 + offset_x, y + 1000 + offset_y))

            if template_pixel not in (12,):
                print((canvas_pixel, template_pixel))
            if template_pixel != last:
                print(template_pixel)
                last = template_pixel

            canvas_pixel = 3
            match (canvas_pixel, template_pixel):
                case ( (0, 0, 0, 255), 1 ) | ( (255, 168, 0, 255), 4 ) | ((255, 214, 53, 255), 5) | ( (54, 144, 234, 255), 6 ) | ((36, 80, 164, 255), 7) | ((255, 153, 170, 255), 12):
                    continue
    return differences
