# Copyright (C) 2019 Nick Filmer (nick80835@gmail.com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import io
from time import time_ns

import numpy as np
from cv2 import COLOR_BGR2RGB, COLOR_RGB2BGR, cvtColor
from numba import jit
from PIL import Image
from scipy import ndimage as ndi
from telethon.errors.rpcerrorlist import PhotoInvalidDimensionsError
from telethon.tl.types import DocumentAttributeFilename

from userbot import CMD_HELP
from userbot.events import errors_handler, register


@register(outgoing=True, pattern="scale2")
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
    await event.edit("`Downloading media…`")
    image = io.BytesIO()
    await event.client.download_media(data, image)
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
    await event.edit(f"`Scaling media by {width_scale}/{height_scale} pixels…`")
    time_before = time_ns()
    image = await stillscale(image, width_scale, height_scale, image.size)
    time_after = time_ns()
    time_taken = (time_after - time_before) / 1000000
    await event.edit(f"`Scaling complete, {width_scale}/{height_scale} pixels in {int(time_taken)} milliseconds.`")

    scaled_io = io.BytesIO()
    scaled_io.name = "image.jpeg"
    image.save(scaled_io, "JPEG")
    scaled_io.seek(0)

    try:
        await event.reply(file=scaled_io)
    except PhotoInvalidDimensionsError:
        await event.reply("`Sorry, you scaled it too much!`")


async def stillscale(img, width_scale, height_scale, original_size):
    # insert documentaton here
    pil_img = img.convert("RGB")
    np_array_img = np.array(pil_img)
    bgr_array_img = cvtColor(np_array_img, COLOR_RGB2BGR)
    raw_scaled_img = seam_carve(bgr_array_img, height_scale, width_scale)
    rgb_scaled_img = cvtColor(raw_scaled_img.astype(np.uint8), COLOR_BGR2RGB)
    scaled_img = Image.fromarray(rgb_scaled_img)
    finished_image = scaled_img.resize(original_size, resample=Image.BICUBIC)
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


### Scale utils ###


@jit
def rotate_image(image, clockwise):
    k = 1 if clockwise else 3
    return np.rot90(image, k)


@jit
def backward_energy(img):
    """
    Simple gradient magnitude energy map.
    """
    xgrad = ndi.convolve1d(img, np.array([1, 0, -1]), axis=1, mode='wrap')
    ygrad = ndi.convolve1d(img, np.array([1, 0, -1]), axis=0, mode='wrap')

    grad_mag = np.sqrt(np.sum(xgrad**2, axis=2) + np.sum(ygrad**2, axis=2))

    return grad_mag


@jit
def remove_seam(img, boolmask):
    img_h, img_w = img.shape[:2]
    boolmask3c = np.stack([boolmask] * 3, axis=2)
    return img[boolmask3c].reshape((img_h, img_w - 1, 3))


@jit
def get_minimum_seam(img):
    """
    DP algorithm for finding the seam of minimum energy. Code adapted from
    https://karthikkaranth.me/blog/implementing-seam-carving-with-python/
    """
    img_h, img_w = img.shape[:2]
    mag = backward_energy(img)

    backtrack = np.zeros_like(mag, dtype=np.int)

    # populate DP matrix
    for i in range(1, img_h):
        for j in range(0, img_w):
            if j == 0:
                idx = np.argmin(mag[i - 1, j:j + 2])
                backtrack[i, j] = idx + j
                min_energy = mag[i-1, idx + j]
            else:
                idx = np.argmin(mag[i - 1, j - 1:j + 2])
                backtrack[i, j] = idx + j - 1
                min_energy = mag[i - 1, idx + j - 1]

            mag[i, j] += min_energy

    # backtrack to find path
    boolmask = np.ones((img_h, img_w), dtype=np.bool)
    j = np.argmin(mag[-1])
    for i in range(img_h-1, -1, -1):
        boolmask[i, j] = False
        j = backtrack[i, j]

    return boolmask


@jit
def seams_removal(img, num_remove):
    for _ in range(num_remove):
        boolmask = get_minimum_seam(img)
        img = remove_seam(img, boolmask)

    return img


def seam_carve(img, d_y, d_x):
    img = seams_removal(img, d_x)
    img = rotate_image(img, True)
    img = seams_removal(img, d_y)
    img = rotate_image(img, False)

    return img
