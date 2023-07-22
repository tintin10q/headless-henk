# file to play with the images
#
import websockets

print(websockets.WebSocketException)

import images
import asyncio
#
from PIL import Image

#
canvas = Image.open("canvas.png")
chief_template = Image.open("chieftemplate.png")
#
#
print("differences:", len(images.get_pixel_differences(canvas, chief_template)))

width, height = 2000, 1000
offsetX, offsetY = -1000, -500

"""
canvas.paste(chief_template, (1500 + offsetX, 1000 + offsetY))

for i in range(width):
    x = i
    y = i
    canvas.putpixel((1500 + offsetX + i, 1000 + offsetY), (255, 0, 0, 255))
    canvas.putpixel((1500 + offsetX + i, 1000 + offsetY + 1), (255, 255, 255, 255))
    canvas.putpixel((1500 + offsetX + i, 1000 + offsetY + 2), (0, 0, 255, 255))

canvas.putpixel((500, 500), (255, 0, 255, 255))
"""
canvas.save("AAcanvas.png")

#

# from config import load_config

# config = load_config()

# import reddit


# test een random pixel place
# reddit.place_pixel(config, reddit.Coordinates(50,505, 1))
#
# print(reddit.get_place_cooldown(config.auth_token))


#
# print(len(asyncio.get_event_loop().run_until_complete(images.get_pixel_differences(canvas, chief_template))))
