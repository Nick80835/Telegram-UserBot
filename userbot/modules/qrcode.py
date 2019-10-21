# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#
# The entire source code is OSSRPL except 'makeqr and getqr' which is MPL
# License: MPL and OSSRPL
""" Userbot module containing commands related to QR Codes. """

import os

from requests import get, post

from userbot import CMD_HELP
from userbot.events import errors_handler, register

ENC_URL = "https://api.qrserver.com/v1/create-qr-code/?data={}&size=200x200&charset-source=UTF-8&charset-target=UTF-8&ecc=L&color=0-0-0&bgcolor=255-255-255&margin=1&qzone=0&format=jpg"
DEC_URL = "https://api.qrserver.com/v1/read-qr-code/?outputformat=json"


@register(outgoing=True, pattern="getqr")
@errors_handler
async def getqr(event):
    # For .getqr command, get QR Code content from the replied photo
    downloaded_file_name = await event.client.download_media(
        await event.get_reply_message())
    file = open(downloaded_file_name, "rb")
    files = {"file": file}
    resp = post(DEC_URL, files=files).json()
    qr_contents = resp[0]["symbol"][0]["data"]
    file.close()
    os.remove(downloaded_file_name)
    await event.edit(f"`QR code contents:`\n{qr_contents}")


@register(outgoing=True, pattern="makeqr")
@errors_handler
async def makeqr(event):
    # For .makeqr command, make a QR Code containing the given content
    input_str = event.pattern_match.group(1)
    message = "SYNTAX: `.makeqr <long text to include>`"

    if input_str:
        message = input_str
    elif event.reply_to_msg_id:
        previous_message = await event.get_reply_message()
        if previous_message.media:
            downloaded_file_name = await event.client.download_media(previous_message)
            m_list = None
            with open(downloaded_file_name, "rb") as file:
                m_list = file.readlines()
            message = ""
            for media in m_list:
                message += media.decode("UTF-8") + "\r\n"
            os.remove(downloaded_file_name)
        else:
            message = previous_message.message

    resp = get(ENC_URL.format(message), stream=True)
    required_file_name = "temp_qr.webp"
    with open(required_file_name, "w+b") as file:
        for chunk in resp.iter_content(chunk_size=128):
            file.write(chunk)

    await event.reply(file=required_file_name)
    os.remove(required_file_name)


CMD_HELP.update({
    'getqr':
    ".getqr"
    "\nUsage: Get the QR Code content from the replied QR Code."
})
CMD_HELP.update({
    'makeqr':
    ".makeqr <content>)"
    "\nUsage: Make a QR Code from the given content."
    "\nExample: .makeqr www.google.com"
})
