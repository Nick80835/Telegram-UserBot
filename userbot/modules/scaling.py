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
from numba import jit, njit
from numba.types import Array, List, Tuple, int64, uint8
from PIL import Image
from telethon.errors.rpcerrorlist import PhotoInvalidDimensionsError
from telethon.tl.types import DocumentAttributeFilename

from userbot import CMD_HELP
from userbot.events import errors_handler, register


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
    img = img.convert("RGB")

    new_image = np.array(img)
    new_image = resize_image(new_image, width_scale)
    new_image = np.transpose(new_image, axes=(1, 0, 2))
    new_image = resize_image(new_image, height_scale)
    new_image = np.transpose(new_image, axes=(1, 0, 2))

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


### Scale utils ###

# The MIT License (MIT)
#
# Copyright (c) 2016 Margaret Sy margaretsy1016@gmail.com
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


@jit(Array(int64, 2, 'A')(Array(uint8, 3, 'A')))
def energy_map(img):
    """
    Parameters
    ==========

    img: numpy.array with shape (height, width, 3)
    func: function
        The energy function to use. Should take in 4 pixels and return a float.

    :returns 2-D numpy array with the same height and width as img
        Each energy[x][y] is an int specifying the energy of that pixel
    """

    x_0 = np.roll(img, -1, axis=1).T
    x_1 = np.roll(img, 1, axis=1).T
    y_0 = np.roll(img, -1, axis=0).T
    y_1 = np.roll(img, 1, axis=0).T

    # we do a lot of transposing before and after here because sums in the
    # energy function happen along the first dimension by default when we
    # want them to be happening along the last (summing the colors)
    en_map = sum(pow((x_0-x_1), 2) + pow((y_0-y_1), 2)).T

    return en_map


@njit(Tuple((Array(int64, 2, 'A'), int64))(Array(uint8, 2, 'A')))
def cumulative_energy(energy):
    """
    https://en.wikipedia.org/wiki/Seam_carving#Dynamic_programming

    Parameters
    ==========
    energy: 2-D numpy.array(uint8)
        Produced by energy_map

    Returns
    =======
        tuple of 2 2-D numpy.array(int64) with shape (height, width).
        paths has the x-offset of the previous seam element for each pixel.
        path_energies has the cumulative energy at each pixel.
    """

    height, width = energy.shape
    paths = np.zeros((height, width), dtype=int64)
    path_energies = np.zeros((height, width), dtype=int64)
    path_energies[0] = energy[0]
    paths[0] = np.arange(width) * np.nan

    for i in range(1, height):
        for j in range(width):
            # Note that indexing past the right edge of a row, as will happen if j == width-1, will
            # simply return the part of the slice that exists
            prev_energies = path_energies[i-1, max(j-1, 0):j+2]
            least_energy = prev_energies.min()
            path_energies[i][j] = energy[i][j] + least_energy
            paths[i][j] = np.where(prev_energies == least_energy)[0][0] - (1*(j != 0))

    path_energies = list(path_energies[-1]).index(min(path_energies[-1]))

    return paths, path_energies


@jit(List(int64)(Array(int64, 2, 'A'), int64))
def find_seam(paths, end_x):
    """
    Parameters
    ==========
    paths: 2-D numpy.array(int64)
        Output of cumulative_energy_map. Each element of the matrix is the offset of the index to
        the previous pixel in the seam
    end_x: int
        The x-coordinate of the end of the seam

    Returns
    =======
        1-D numpy.array(int64) with length == height of the image
        Each element is the x-coordinate of the pixel to be removed at that y-coordinate. e.g.
        [4,4,3,2] means "remove pixels (0,4), (1,4), (2,3), and (3,2)"
    """

    height, _ = paths.shape[:2]
    seam = [end_x]

    for i in range(height-1, 0, -1):
        cur_x = seam[-1]
        offset_of_prev_x = paths[i][cur_x]
        seam.append(cur_x + offset_of_prev_x)

    seam.reverse()
    return seam


@jit(Array(int64, 3, 'A')(Array(int64, 2, 'A'), Array(int64, 1, 'A')))
def remove_seam(img, seam):
    """
    Parameters
    ==========
    img: 3-D numpy.array
        RGB image you want to resize
    seam: 1-D numpy.array
        seam to remove. Output of seam function

    Returns
    =======
        3-D numpy array of the image that is 1 pixel shorter in width than the input img
    """

    height, _ = img.shape[:2]
    remove_array = np.array([np.delete(img[row], seam[row], axis=0) for row in range(height)])
    return remove_array


@jit(Array(uint8, 3, 'A')(Array(uint8, 3, 'A'), int64))
def resize_image(img, cropped_pixels):
    """
    Parameters
    ==========
    img: 3-D numpy.array
        Image you want to crop.
    cropped_pixels: int
        Number of pixels you want to shave off the width. Aka how many vertical seams to remove.

    Returns
    =======
        3-D numpy array of your now cropped_pixels-slimmer image.
    """

    for _ in range(cropped_pixels):
        e_map = energy_map(img)
        e_paths, e_totals = cumulative_energy(e_map)
        seam = find_seam(e_paths, e_totals)
        img = remove_seam(img, seam)

    return img
