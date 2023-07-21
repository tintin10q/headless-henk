import asyncio
from typing import List, Literal

import httpx
from io import BytesIO
from PIL import Image

from colors import printc, GREEN, RESET, BLUE
from now import now
from parse_order import Order
from canvas import build_canvas_image


async def download_image(url):
    printc(f"{now()} {GREEN} downloading image from {BLUE}{url}{RESET}")
    async with httpx.AsyncClient() as client:
        response = await client.get(url, timeout=2 * 60)
    response.raise_for_status()
    return Image.open(BytesIO(response.content))


async def get_pixel_differences_with_download(order: Order, canvas_indexes: List[Literal[0, 1, 2, 3, 4, 5, None]]):
    """
    :param order:
    :param canvas_indexes: Put None on the missing indexes, so to fetch 1 and 4 you do [None, 1, None, None, 4, None]
    :return:
    """
    canvas, chief_template = await asyncio.gather(build_canvas_image(canvas_indexes), download_image(order.images.order))

    chief_template.save("chieftemplate.png")

    width, height = order.size.width, order.size.height

    offset_x = 1000
    offset_y = 500

    diff_pixels = []

    for x in range(width):
        for y in range(height):
            canvas_pixel = canvas.getpixel((x + offset_x, y + offset_y * -1))
            template_pixel = chief_template.getpixel((x, y))
            print(canvas_pixel, template_pixel)

            if canvas_pixel != template_pixel:
                diff_pixels.append((x + offset_x, y + offset_y, canvas_pixel, template_pixel))

    return diff_pixels


def get_pixel_differences(canvas: Image, chief_template: Image) -> List[(int, int, (int, int, int, int), (int, int, int, int))]:
    width, height = 1000, 1000
    offsetX, offsetY = 1000, 500

    diff_pixels = []

    for x in range(width):
        for y in range(height):
            template_pixel = chief_template.getpixel((x, y))
            match template_pixel:
                case (0, 0, 0, 0):
                    continue
            canvas_pixel = canvas.getpixel((x + offsetX, y + offsetY))
            print(canvas_pixel, template_pixel)

            if canvas_pixel != template_pixel:
                diff_pixels.append((x + offsetX, y + offsetY, canvas_pixel, template_pixel))

    return diff_pixels
