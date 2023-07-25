import asyncio
from typing import List, Literal

import PIL.Image
import httpx
from io import BytesIO

import requests
from PIL import Image

from colors import printc, GREEN, RESET, BLUE, RED
from now import now_usr
from parse_order import Order
from canvas import build_canvas_image
import random
import math
from typing import Tuple
from dataclasses import dataclass

from config import default_save_images


@dataclass
class ImageDiff:
    x: int
    y: int
    canvas_pixel: Tuple[int, int, int, int]
    template_pixel: Tuple[int, int, int, int]
    priority: int


async def download_order_image(url: str, save_images: bool = default_save_images, *, username: str = None):
    printc(f"{now_usr(username=username)} {GREEN}Downloading chief image from {BLUE}{url}{RESET}")
    # async with httpx.AsyncClient() as client:
    #     response = await client.get(url, timeout=2 * 60)
    # response.raise_for_status()
    response = requests.get(url)

    order_img = Image.open(BytesIO(response.content)).convert("RGBA")
    if save_images:
        order_img.save("chieftemplate.png")
    # apparently this is good for memory
    await asyncio.sleep(0)
    return order_img


async def download_priority_image(url: str, save_images: bool = default_save_images, *, username: str = None):
    printc(f"{now_usr(username=username)} {GREEN}Downloading priority image from {BLUE}{url}{RESET}")
    async with httpx.AsyncClient() as client:
        response = await client.get(url, timeout=2 * 60)
    response.raise_for_status()

    priority_img = Image.open(BytesIO(response.content)).convert("RGBA")
    if save_images:
        priority_img.save("prioritymap.png")
    # apparently this is good for memory
    await asyncio.sleep(0)
    return priority_img


async def get_pixel_differences_with_download(order: Order, canvas_indexes: List[Literal[0, 1, 2, 3, 4, 5, None]], *,
                                              save_images: bool = default_save_images, username: str = None):
    """
    :param save_images:  True to save as png
    :param order: Order dataclass with information about template image
    :param canvas_indexes: Put None on the missing indexes, so to fetch 1 and 4 you do [None, 1, None, None, 4, None]
    :return:
    """
    canvas, chief_template = await asyncio.gather(build_canvas_image(canvas_indexes, username=username),
                                                  download_order_image(order.images.order, username=username))

    if save_images:
        chief_template.save("chieftemplate.png")
        canvas.save("canvas.png")

    width, height = order.size.width, order.size.height

    offset_x = order.offset.x
    offset_y = order.offset.y

    diff_pixels = []

    for x in range(width):
        for y in range(height):
            template_pixel = chief_template.getpixel((x, y))

            if isinstance(template_pixel, int):
                print(f"{now_usr(username=username)}{RED} THE TEMPLATE IS USING A 4 BIT PNG AND NOT 32 BIT PNG!{RESET}")
                return []

            if template_pixel[-1] == 0:
                continue

            canvas_pixel = canvas.getpixel((x + 1500 + offset_x, y + 1000 + offset_y))

            if canvas_pixel != template_pixel:
                diff_pixels.append(ImageDiff(x + 1500 + offset_x, y + 1000 + offset_y, canvas_pixel, template_pixel,
                                             0))  # add priority = 0, because we don't know the priority here

    del canvas, chief_template
    return diff_pixels


def calculate_priority(pixel: Tuple[int, int, int, int]) -> int:
    r, g, b, a = pixel
    if a == 0:
        return 0
    return (r << 16) + (g << 8) + b


async def get_pixel_differences_with_canvas_download(order: Order,
                                                     canvas_indexes: List[Literal[0, 1, 2, 3, 4, 5, None]],
                                                     order_image: Image, priority_image: Image = None, *,
                                                     save_images: bool = default_save_images, username: str = None) -> List[ImageDiff]:
    """
    Only download the canvas and supply the chief as an input
    :param save_images: True to template and canvas as png
    :param priority_image: The priority image
    :param order_image: Template with the correct pixels
    :param order: Order object with information about chief image
    :param canvas_indexes: Put None on the missing indexes, so to fetch 1 and 4 you do [None, 1, None, None, 4, None]
    :return:
    """
    canvas = await build_canvas_image(canvas_indexes, username=username)

    if save_images:
        canvas.save("canvas.png")

    template_width, template_height = order.size.width, order.size.height

    offset_x = order.offset.x
    offset_y = order.offset.y

    # print(f"{template_width=}, {template_height=}, {offsetX=}, {offsetY=}, {canvas_indexes=}")

    diff_pixels = []

    for x in range(template_width):
        for y in range(template_height):
            template_pixel = order_image.getpixel((x, y))

            if isinstance(template_pixel, int):
                print(f"{now_usr(username=username)}{RED} THE TEMPLATE IS USING A 4 BIT PNG AND NOT 32 BIT PNG!{RESET}")
                return []

            if template_pixel[-1] == 0:
                continue

            canvas_pixel = canvas.getpixel((x + 1500 + offset_x, y + 1000 + offset_y))

            if canvas_pixel != template_pixel:
                priority = 0
                if priority_image:
                    priority_pixel = priority_image.getpixel((x, y))
                    priority = calculate_priority(priority_pixel)
                    priority += math.floor(random.random() * 10000)  # Increase randomness

                diff_pixels.append(
                    ImageDiff(x + 1500 + offset_x, y + 1000 + offset_y, canvas_pixel, template_pixel, priority))

    del canvas

    return diff_pixels


def get_pixel_differences(order: Order, canvas: Image, chief_template: Image, priority_image: Image = None, *, username: str = None) -> List[ImageDiff]:
    """ This one is just for testing, use save_images config to save the images, and then you can load them into this """

    diff_pixels = []
    # Todo maybe use https://stackoverflow.com/questions/35176639/compare-images-python-pil

    for x in range(order.size.width):
        for y in range(order.size.height):
            template_pixel = chief_template.getpixel((x, y))

            if isinstance(template_pixel, int):
                print(
                    f"{now_usr(username=username)} {RED}THE TEMPLATE IS USING A 4 BIT PNG AND NOT 32 BIT PNG! {RESET}")
                return []

            if template_pixel[-1] == 0:
                continue

            canvas_pixel = canvas.getpixel((x + 1500 + order.offset.x, order.offset.y + 1000 + order.offset.y))
            if canvas_pixel != template_pixel:
                priority = 0
                if priority_image:
                    priority_pixel = priority_image.getpixel((x, y))
                    priority = calculate_priority(priority_pixel)
                    priority += math.floor(random.random() * 10000)  # Increase randomness

                diff_pixels.append(
                    ImageDiff(x + 1500 + order.offset.x, y + 1000 + order.offset.y, canvas_pixel, template_pixel, priority))

    return diff_pixels


if __name__ == '__main__':
    downloaded_canvas = PIL.Image.open("canvas.png")
    downloaded_template = PIL.Image.open('chieftemplate.png').convert("RGBA")
    print(len(get_pixel_differences(downloaded_canvas, downloaded_template)))
