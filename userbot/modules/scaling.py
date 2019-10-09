# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#
""" Userbot module for content-aware scaling. """

import io

import numpy
from PIL import Image
from telethon.errors.rpcerrorlist import PhotoInvalidDimensionsError
from telethon.tl.types import DocumentAttributeFilename

from userbot import CMD_HELP, bot
from userbot.events import errors_handler, register
from userbot.scaleutils.seam_carver import resize_image


@register(outgoing=True, pattern="scale")
@errors_handler
async def stillscaler(event):
    try:
        scale_pixels = int(event.pattern_match.group(1))
        if scale_pixels < 1:
            raise ValueError
    except ValueError:
        scale_pixels = 64

    if event.is_reply:
        reply_message = await event.get_reply_message()
        data = await check_media(reply_message)

        if isinstance(data, bool):
            await event.edit("`I can't scale that!`")
            return
    else:
        await event.edit("`Reply to an image or sticker to scale it!`")
        return

    # download last photo (highres) as byte array
    image = io.BytesIO()
    image = await bot.download_media(data, image)
    image = Image.open(image)

    width, height = image.size

    if height > width:
        while scale_pixels > height:
            scale_pixels -= 32

        height_scale = scale_pixels

        width_scale = int(height_scale * (width / height))
    elif width > height:
        while scale_pixels > width:
            scale_pixels -= 32

        width_scale = scale_pixels

        height_scale = int(width_scale * (height / width))
    else:
        while scale_pixels > height:
            scale_pixels -= 32

        width_scale = scale_pixels
        height_scale = scale_pixels

    # scale the image
    image = await stillscale(image, width_scale, height_scale, image.size)

    scaled_io = io.BytesIO()
    scaled_io.name = "image.jpeg"
    image.save(scaled_io, "JPEG")
    scaled_io.seek(0)

    try:
        await event.reply(file=scaled_io)
    except PhotoInvalidDimensionsError:
        await event.reply("`Sorry, you scaled it too much!`")


async def stillscale(img, width_scale, height_scale, original_size):
    img = img.convert("RGB")

    new_image = resize_image(numpy.array(img), width_scale)
    new_image = numpy.transpose(new_image, axes=(1, 0, 2))
    new_image = resize_image(new_image, height_scale)
    new_image = numpy.transpose(new_image, axes=(1, 0, 2))

    finished_image = Image.fromarray(new_image).resize(original_size, resample=Image.BICUBIC)

    return finished_image


async def check_media(reply_message):
    if reply_message and reply_message.media:
        if reply_message.photo:
            data = reply_message.photo
        elif reply_message.document:
            if DocumentAttributeFilename(file_name='AnimatedSticker.tgs') in reply_message.media.document.attributes:
                return False
            if reply_message.gif or reply_message.video or reply_message.audio or reply_message.voice:
                return False
            data = reply_message.media.document
        else:
            return False
    else:
        return False

    if not data or data is None:
        return False
    else:
        return data


CMD_HELP.update({
    'scale':
    ".scale <number>"
    "\nContent-aware scales an image or sticker, optional scale pass count."
})
