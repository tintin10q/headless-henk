import asyncio
from typing import List, Literal

import requests
from io import BytesIO
from PIL import Image

import reddit
from colors import GREEN, AQUA, RESET
from config import load_config


async def get_canvas_part(canvas_id: Literal[0, 1, 2, 3, 4, 5]):
    canvas_url = await reddit.get_canvas_url(canvas_id)
    response = requests.get(canvas_url)
    response.raise_for_status()
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
    num_rows = (len(image_ids) + 2) // 3  # Calculate the number of rows based on the number of parts.

    canvas_width, canvas_height = None, None
    canvas_cols = 3  # Default number of columns.

    for i, image_id in enumerate(image_ids):
        if image_id is not None:
            canvas_part = await get_canvas_part(image_id)
            if canvas_width is None or canvas_height is None:
                canvas_width, canvas_height = canvas_part.size
            canvas_parts[i] = canvas_part

    if canvas_width is None or canvas_height is None:
        raise ValueError("No valid image IDs provided.")

    # Calculate the size of the final canvas image.
    final_canvas_width = canvas_width * min(canvas_cols, len(canvas_parts))
    final_canvas_height = canvas_height * num_rows

    # Create the final canvas image.
    full_canvas = Image.new('RGBA', (final_canvas_width, final_canvas_height))

    for i, canvas_part in canvas_parts.items():
        row, col = divmod(i, canvas_cols)
        x = col * canvas_width
        y = row * canvas_height
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
