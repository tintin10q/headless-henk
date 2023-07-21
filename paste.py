# file to play with the images
#
# import images
# import asyncio
#
# from PIL import Image
#
# canvas = Image.open("canvas.png")
# chief_template = Image.open("chieftemplate.png")
#
# canvas.paste(chief_template, (1000, 500))
#
# print("differences:", len(images.get_pixel_differences(canvas, chief_template)))
# canvas.save("AAcanvas.png")
#

from config import load_config

config = load_config()

import reddit


# test een random pixel place
reddit.place_pixel(config, reddit.Coordinates(50,505, 1))

print(reddit.get_place_cooldown(config.auth_token))


#
# print(len(asyncio.get_event_loop().run_until_complete(images.get_pixel_differences(canvas, chief_template))))
