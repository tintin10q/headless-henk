import asyncio
from typing import List, Literal, Tuple

from io import BytesIO

import httpx
import requests
from PIL import Image

import reddit
from colors import GREEN, AQUA, RESET, printc, BLUE, RED
from now import now_usr


async def get_canvas_part(canvas_id: Literal[0, 1, 2, 3, 4, 5], username: str = None):
    canvas_url = await reddit.get_canvas_url(canvas_id, username=username)
    # async with httpx.AsyncClient() as client:
    #     response = await client.get(canvas_url)
    response = requests.get(canvas_url)
    printc(f'{now_usr(username=username)} {GREEN}Downloading canvas from {BLUE}{canvas_url}')
    # response = requests.get(canvas_url)
    # response.raise_for_status()
    return Image.open(BytesIO(response.content))


async def build_canvas_image(image_ids: List[Literal[0, 1, 2, 3, 4, 5, None]], username: str = None) -> Image.Image:
    """
    Builds the complete canvas image by stacking the available parts.

    Parameters:
        image_ids (list): A list of canvas IDs representing the available parts.
                          Use None for missing parts.

    Returns:
        Image.Image: A PIL Image object representing the complete canvas image.
        :param username: username of user building the canvas
    """
    if not image_ids:
        raise ValueError("The image_ids list should not be empty.")

    canvas_parts = {}

    get_canvas_coroutines = []
    for i, image_id in enumerate(image_ids):
        if image_id is not None:
            async def get_canvaspart(*, _index, _image_id):
                canvas_part = await get_canvas_part(_image_id, username=username)
                canvas_parts[_index] = canvas_part
                # apparently this is good for memory
                await asyncio.sleep(0)

            get_canvas_coroutines.append(get_canvaspart(_index=i, _image_id=image_id))


    try:
        await asyncio.gather(*get_canvas_coroutines)
    except RuntimeError as e:
        print(f'{now_usr(username=username)}{RED}Something went wrong downloading the canvas trying again, the error was:{RESET}', e)
        canvas_parts = {}

        get_canvas_coroutines = []
        for i, image_id in enumerate(image_ids):
            if image_id is not None:
                async def get_canvaspart(*, _index, _image_id):
                    canvas_part = await get_canvas_part(_image_id, username=username)
                    canvas_parts[_index] = canvas_part
                    # apparently this is good for memory
                    await asyncio.sleep(0)

                get_canvas_coroutines.append(get_canvaspart(_index=i, _image_id=image_id))
        await asyncio.gather(*get_canvas_coroutines)

    # Calculate the size of the final canvas image.
    final_canvas_width = 3000
    final_canvas_height = 2000

    # Create the final canvas image.
    full_canvas = Image.new('RGBA', (final_canvas_width, final_canvas_height))

    for i in range(6):  # There are 6 canvases
        if i in canvas_parts:
            canvas_part = canvas_parts[i]
            x = 1000 * i % 3000
            y = 1000 if i > 2 else 0
            # print(i, x,y)
            full_canvas.paste(canvas_part, (x, y))

    return full_canvas


def download_and_save_canvas():
    # Replace the image_ids list with the actual IDs of the available parts.
    image_ids: List[Literal[0, 1, 2, 3, 4, 5, None]] = [
        0, 1, 2, 3, 4, 5
    ]

    async def go():
        try:
            canvas_image = await build_canvas_image(image_ids)
            canvas_image.save("canvas.png")  # You can use .save("output.png") instead of .show() to save the image.
            print(f"{GREEN}Downloaded canvas {AQUA}to canvas.png{RESET}")
        except ValueError as e:
            print(f"Error building canvas image: {e}")

    asyncio.get_event_loop().run_until_complete(go())


def xy_to_canvas_index(x: int, y: int) -> Literal[0, 1, 2, 3, 4, 5]:
    if x < 1000 and y < 1000:
        return 0
    elif 1000 <= x < 2000 and y < 1000:
        return 1
    elif x >= 2000 and y < 1000:
        return 2
    if x < 1000 and y >= 1000:
        return 3
    elif 1000 <= x < 2000 and y >= 1000:
        return 4
    elif x >= 2000 and y >= 1000:
        return 5


def rgba_to_hex(rgba_tuple):
    # Check if the input tuple has exactly 4 elements
    if len(rgba_tuple) != 4:
        raise ValueError("Input tuple must contain exactly 4 elements (RGBA).")

    # Convert each component to a 2-digit hexadecimal representation
    hex_components = [format(component, '02x') for component in rgba_tuple]

    hex_code = f"#{hex_components[0]}{hex_components[1]}{hex_components[2]}"

    return hex_code.upper()


valid_color_codes = ['#6D001A', '#BE0039', '#FF4500', '#FFA800', '#FFD635', '#FFF8B8', '#00A368', '#00CC78', '#7EED56', '#00756F', '#009EAA', '#00CCC0', '#2450A4', '#3690EA', '#51E9F4', '#493AC1', '#6A5CFF', '#94B3FF', '#811E9F', '#B44AC0',
                     '#E4ABFF', '#DE107F', '#FF3881', '#FF99AA', '#6D482F', '#9C6926', '#FFB470', '#000000', '#515252', '#898D90', '#D4D7D9', '#FFFFFF']

color_names = ['N/A - #6D001A', 'Dark red', 'Red', 'Orange', 'Yellow', 'N/A - #FFF8B8', 'Dark green', 'Green', 'Light green', 'Dark teal', 'Teal', 'N/A - #00CCC0', 'Dark blue', 'Blue', 'Light blue',
               'Indigo', 'Periwinkle', 'N/A - #94B3FF', 'Dark purple', 'Purple',
               'N/A - #E4ABFF', 'N/A - #DE107F', 'Pink', 'Light pink', 'Dark brown', 'Brown', 'N/A - #FFB470', 'Black', 'N/A - #515252', 'Gray', 'Light gray', 'White']


def color_index_to_name(color_index: int) -> str:
    return color_names[color_index]


def color_tuple_to_color_index(color_tuple: Tuple[int, int, int, int]) -> int:
    hexcode = rgba_to_hex(color_tuple)
    return valid_color_codes.index(hexcode)


if __name__ == "__main__":
    download_and_save_canvas()
