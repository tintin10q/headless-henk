import asyncio
from typing import List, Literal

import httpx
from io import BytesIO
from PIL import Image
from parse_order import Order
from canvas import build_canvas_image


async def download_image(url):
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
    response.raise_for_status()
    return Image.open(BytesIO(response.content))


async def get_pixel_differences(order: Order, canvas_indexes: List[Literal[0, 1, 2, 3, 4, 5, None]]):
    """
    :param order:
    :param canvas_indexes: Put None on the missing indexes, so to fetch 1 and 4 you do [None, 1, None, None, 4, None]
    :return:
    """
    canvas, chief_template = await asyncio.gather(build_canvas_image(canvas_indexes), download_image(order.images.order))

    width, height = order.size.width, order.size.height

    diff_pixels = []

    for x in range(width):
        for y in range(height):
            pixel1 = canvas.getpixel((x + order.offset.x, y + order.offset.y))
            pixel2 = chief_template.getpixel((x, y))

            if pixel1 != pixel2:
                diff_pixels.append((x + order.offset.x, y + order.offset.y, pixel1, pixel2))

    return diff_pixels

# if __name__ == "__main__":
#     url1 = "URL_TO_BIGGER_IMAGE"
#     url2 = "URL_TO_SMALLER_IMAGE"
#
#     # offset_x = 100  # Replace with the actual x-coordinate offset
#     # offset_y = 50   # Replace with the actual y-coordinate offset
#
#     image1 = download_image(url1)
#     image2 = download_image(url2)
#
#     differences = get_pixel_differences(image1, image2, , offset_y)
#
#     print("Pixel differences:")
#     for diff in differences:
#         x, y, pixel1, pixel2 = diff
#         print(f"At ({x}, {y}): Image1 - {pixel1}, Image2 - {pixel2}")
