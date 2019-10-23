# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#
""" Userbot module for scraping Urban Dictionary. """

import os
import re

import aiohttp

from userbot import CMD_HELP
from userbot.events import errors_handler, register

UD_QUERY_URL = 'http://api.urbandictionary.com/v0/define'
UD_RANDOM_URL = 'http://api.urbandictionary.com/v0/random'


@register(outgoing=True, pattern="ud")
@errors_handler
async def urban_dict(event):
    udquery = event.pattern_match.group(1)

    try:
        udquery
    except:
        udquery = None

    if udquery:
        params = {'term': udquery}
        url = UD_QUERY_URL
    else:
        params = None
        url = UD_RANDOM_URL

    session = aiohttp.ClientSession()

    async with session.get(url, params=params) as response:
        if response.status == 200:
            response = await response.json()
        else:
            response = response.status

    await session.close()

    try:
        response = response['list'][0]
        wordinfo = [response['word'], response['definition']]
        if response['example'] != '':
            wordinfo.append(response['example'])
    except NameError:
        wordinfo = ["An error occurred, response code:", str(response)]
    except IndexError:
        wordinfo = ['No results for query', udquery]

    definition = '**{0[0]}**: {0[1]}'.format(wordinfo)

    try:
        definition += '\n\n**Example**: {0[2]}'.format(wordinfo)
    except IndexError:
        pass

    definition = re.sub(r'[[]', '', definition)
    definition = re.sub(r'[]]', '', definition)

    if len(definition) >= 4096:
        await event.edit("`Output too large, sending as file.`")
        file = open("output.txt", "w+")
        file.write(definition)
        file.close()
        await event.client.send_file(event.chat_id, "output.txt", caption="`Output was too large, sent it as a file.`")
        if os.path.exists("output.txt"):
            os.remove("output.txt")
        await event.delete()
        return

    await event.edit(definition)


CMD_HELP.update({
    'ud':
    ".ud <search_query>"
    "\nUsage: Does a search on Urban Dictionary."
})
