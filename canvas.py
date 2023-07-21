import asyncio
from typing import List, Literal

import httpx
from io import BytesIO

import requests
from PIL import Image

import reddit
from colors import GREEN, AQUA, RESET, printc, BLUE
from now import now


async def get_canvas_part(canvas_id: Literal[0, 1, 2, 3, 4, 5]):
    canvas_url = await reddit.get_canvas_url(canvas_id)
    # async with httpx.AsyncClient() as client:
    #     response = await client.get(canvas_url)
    printc(f'{now()} {GREEN}Downloading canvas from {BLUE}{canvas_url}')
    response = requests.get(canvas_url)
    # response.raise_for_status()
    return Image.open(BytesIO(response.content))


async def build_canvas_image(image_ids: List[Literal[0, 1, 2, 3, 4, 5, None]]) -> Image.Image:
    """
    Builds the complete canvas image by stacking the available parts.

    Parameters:
        image_ids (list): A list of canvas IDs representing the available parts.
                          Use None for missing parts.

    Returns:
        Image.Image: A PIL Image object representing the complete canvas image.
    """
    if not image_ids:
        raise ValueError("The image_ids list should not be empty.")

    canvas_parts = {}

    for i, image_id in enumerate(image_ids):
        if image_id is not None:
            canvas_part = await get_canvas_part(image_id)
            canvas_parts[i] = canvas_part

    # Calculate the size of the final canvas image.
    final_canvas_width = 3000
    final_canvas_height = 2000

    # Create the final canvas image.
    full_canvas = Image.new('RGBA', (final_canvas_width, final_canvas_height))

    for i in range(6): # There are 6 canvases
        if i in canvas_parts:
            canvas_part = canvas_parts[i]
            x = 1000 * i % 3000
            y = 1000 if i > 2 else 0
            print(i, x,y)
            full_canvas.paste(canvas_part, (x, y))

    return full_canvas


def download_and_save_canvas():
    # Replace the image_ids list with the actual IDs of the available parts.
    image_ids: List[Literal[0, 1, 2, 3, 4, 5, None]] = [
        None, 1, None, None, 4, None
    ]

    async def go():
        try:
            canvas_image = await build_canvas_image(image_ids)
            canvas_image.save("canvas.png")  # You can use .save("output.png") instead of .show() to save the image.
            print(f"{GREEN}Downloaded canvas {AQUA}to canvas.png{RESET}")
        except ValueError as e:
            print(f"Error building canvas image: {e}")

    asyncio.get_event_loop().run_until_complete(go())


if __name__ == "__main__":
    download_and_save_canvas()
