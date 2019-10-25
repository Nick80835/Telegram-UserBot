# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#
""" Userbot module for scraping anime stuff. """

import requests

from userbot import CMD_HELP
from userbot.events import errors_handler, register

DAN_URL = "http://danbooru.donmai.us/posts.json"


@register(outgoing=True, pattern="dan(x|)")
@errors_handler
async def danbooru(event):
    await event.edit(f"`Processing…`")

    if "x" in event.pattern_match.group(0):
        rating = "Explicit"
    else:
        rating = "Safe"

    search_query = event.pattern_match.group(2)

    params = {"limit": 1,
              "random": "true",
              "tags": f"Rating:{rating} {search_query}".strip()}

    with requests.get(DAN_URL, params=params) as response:
        if response.status_code == 200:
            response = response.json()
        else:
            await event.edit(f"`An error occurred, response code:` **{response.status_code}**")
            return

    if not response:
        await event.edit(f"`No results for query:` **{search_query}**")
        return

    valid_urls = []

    for url in ['file_url', 'large_file_url', 'source']:
        if url in response[0].keys():
            valid_urls.append(response[0][url])

    if not valid_urls:
        await event.edit(f"`Failed to find URLs for query:` **{search_query}**")
        return

    for image_url in valid_urls:
        try:
            await event.client.send_file(event.chat_id, file=image_url)
            await event.delete()
            return
        except:
            pass

    await event.edit(f"``Failed to fetch media for query:` **{search_query}**")


CMD_HELP.update({
    'dan':
    ".dan(x)"
    "\nUsage: Random anime images from Danbooru with optional searching, optionally explicit."
})
