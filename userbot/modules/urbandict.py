# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#
""" Userbot module for scraping Urban Dictionary. """

import io

import requests

from userbot import CMD_HELP
from userbot.events import errors_handler, register

UD_QUERY_URL = 'http://api.urbandictionary.com/v0/define'
UD_RANDOM_URL = 'http://api.urbandictionary.com/v0/random'


@register(outgoing=True, pattern="ud")
@errors_handler
async def urban_dict(event):
    udquery = event.pattern_match.group(1)

    if udquery:
        params = {'term': udquery}
        url = UD_QUERY_URL
    else:
        params = None
        url = UD_RANDOM_URL

    with requests.get(url, params=params) as response:
        if response.status_code == 200:
            response = response.json()
        else:
            await event.edit(f"`An error occurred, response code:` **{response.status_code}**")
            return

    if response['list']:
        response_word = response['list'][0]
    else:
        await event.edit(f"`No results for query:` **{udquery}**")
        return

    definition = f"**{response_word['word']}**: `{response_word['definition']}`"

    if response_word['example']:
        definition += f"\n\n**Example**: `{response_word['example']}`"

    definition = definition.replace("[", "").replace("]", "")

    if len(definition) >= 4096:
        file_io = io.BytesIO()
        file_io.write(bytes(definition.encode('utf-8')))
        file_io.name = f"definition of {response_word['word']}.txt"
        await event.client.send_file(event.chat_id, file_io, caption="`Output was too large, sent it as a file.`")
        await event.delete()
        return

    await event.edit(definition)


CMD_HELP.update({
    'ud':
    ".ud <search_query>"
    "\nUsage: Does a search on Urban Dictionary."
})
