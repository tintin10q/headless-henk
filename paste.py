# file to play with the images

import images
import asyncio

from PIL import Image

canvas = Image.open("canvas.png")
chief_template = Image.open("chieftemplate.png")

canvas.paste(chief_template, (1000, 500))

print(len(images.get_pixel_differences(canvas, chief_template)))
canvas.save("AAcanvas.png")
#
# print(len(asyncio.get_event_loop().run_until_complete(images.get_pixel_differences(canvas, chief_template))))
