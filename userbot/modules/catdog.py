# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#
""" Userbot module containing dogs and cats. """

import asyncio, re, aiohttp
from userbot import CMD_HELP, bot
from userbot.events import register, errors_handler

CAT_URL = 'http://api.thecatapi.com/v1/images/search'
DOG_URL = 'http://api.thedogapi.com/v1/images/search'
CAT_API_KEY = 'e5a56813-be40-481c-9c8a-a6585c37c1fe'
DOG_API_KEY = '105555df-5c50-40fe-bd59-d15a17ce1c2e'
CAT_HEADERS = {"x-api-key": CAT_API_KEY}
DOG_HEADERS = {"x-api-key": DOG_API_KEY}
IMGPARAM = {"mime_types": "jpg,png"}
GIFPARAM = {"mime_types": "gif"}


async def nekoAtsume(params):
    session = aiohttp.ClientSession(headers=CAT_HEADERS)

    async with session.get(CAT_URL, params=params) as response:
        if response.status == 200:
            neko = await response.json()
        else:
            neko = response.status

    await session.close()
    return neko

async def inuAtsume(params):
    session = aiohttp.ClientSession(headers=DOG_HEADERS)

    async with session.get(DOG_URL, params=params) as response:
        if response.status == 200:
            inu = await response.json()
        else:
            inu = response.status

    await session.close()
    return inu


@register(outgoing=True, pattern="cat")
@errors_handler
async def cat(event):
    neko = await nekoAtsume(IMGPARAM)

    if type(neko) == int:
        await event.edit(f"`There was an error finding the cats! :( -> {neko}`")
        return

    await event.client.send_file(await event.client.get_input_entity(event.chat_id), neko[0]["url"])
    await event.delete()


@register(outgoing=True, pattern="cathd")
@errors_handler
async def cathd(event):
    neko = await nekoAtsume(IMGPARAM)

    if type(neko) == int:
        await event.edit(f"`There was an error finding the cats! :( -> {neko}`")
        return

    await event.client.send_file(await event.client.get_input_entity(event.chat_id), neko[0]["url"], force_document=True)
    await event.delete()


@register(outgoing=True, pattern="catgif")
@errors_handler
async def catgif(event):
    neko = await nekoAtsume(GIFPARAM)

    if type(neko) == int:
        await event.edit(f"`There was an error finding the cats! :( -> {neko}`")
        return

    await event.client.send_file(await event.client.get_input_entity(event.chat_id), neko[0]["url"])
    await event.delete()


@register(outgoing=True, pattern="dog")
@errors_handler
async def dog(event):
    inu = await inuAtsume(IMGPARAM)

    if type(inu) == int:
        await event.edit(f"`There was an error finding the dogs! :( -> {inu}`")
        return

    await event.client.send_file(await event.client.get_input_entity(event.chat_id), inu[0]["url"])
    await event.delete()


@register(outgoing=True, pattern="doghd")
@errors_handler
async def doghd(event):
    inu = await inuAtsume(IMGPARAM)

    if type(inu) == int:
        await event.edit(f"`There was an error finding the dogs! :( -> {inu}`")
        return

    await event.client.send_file(await event.client.get_input_entity(event.chat_id), inu[0]["url"], force_document=True)
    await event.delete()


@register(outgoing=True, pattern="doggif")
@errors_handler
async def doggif(event):
    inu = await inuAtsume(GIFPARAM)

    if type(inu) == int:
        await event.edit(f"`There was an error finding the dogs! :( -> {inu}`")
        return

    await event.client.send_file(await event.client.get_input_entity(event.chat_id), inu[0]["url"])
    await event.delete()


CMD_HELP.update({
    'cat':
    ".cat(hd|gif)"
    "\nSends an image of a cat, optionally as a file or a GIF."
})
CMD_HELP.update({
    'dog':
    ".dog(hd|gif)"
    "\nSends an image of a dog, optionally as a file or a GIF."
})