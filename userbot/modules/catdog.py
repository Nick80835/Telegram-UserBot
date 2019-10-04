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


class catapi():
    def __init__(self, type):
        headers = {"x-api-key": CAT_API_KEY}
        self.params = {"mime_types": type}
        self.session = aiohttp.ClientSession(headers=headers)

    async def _get(self):
        async with self.session.get(CAT_URL, params=self.params) as response:
            if response.status == 200:
                response = await response.json()
            else:
                raise Exception

        return response

    async def getcat(self):
        cat = await self._get()
        return cat

    async def close(self):
        await self.session.close()


class dogapi():
    def __init__(self, type):
        headers = {"x-api-key": DOG_API_KEY}
        self.params = {"mime_types": type}
        self.session = aiohttp.ClientSession(headers=headers)

    async def _get(self):
        async with self.session.get(DOG_URL, params=self.params) as response:
            if response.status == 200:
                response = await response.json()
            else:
                raise Exception

        return response

    async def getdog(self):
        dog = await self._get()
        return dog

    async def close(self):
        await self.session.close()


async def nekoatsume(type):
    cathouse = catapi(type)
    cat = await cathouse.getcat()
    await cathouse.close()
    return cat


async def inuatsume(type):
    doghouse = dogapi(type)
    dog = await doghouse.getdog()
    await doghouse.close()
    return dog


@register(outgoing=True, pattern="cat")
@errors_handler
async def cat(event):
    cat = await nekoatsume("jpg,png")
    await event.client.send_file(await event.client.get_input_entity(event.chat_id), cat[0]["url"])
    await event.delete()


@register(outgoing=True, pattern="cathd")
@errors_handler
async def cathd(event):
    cat = await nekoatsume("jpg,png")
    await event.client.send_file(await event.client.get_input_entity(event.chat_id), cat[0]["url"], force_document=True)
    await event.delete()


@register(outgoing=True, pattern="catgif")
@errors_handler
async def catgif(event):
    cat = await nekoatsume("gif")
    await event.client.send_file(await event.client.get_input_entity(event.chat_id), cat[0]["url"])
    await event.delete()


@register(outgoing=True, pattern="dog")
@errors_handler
async def dog(event):
    dog = await inuatsume("jpg,png")
    await event.client.send_file(await event.client.get_input_entity(event.chat_id), dog[0]["url"])
    await event.delete()


@register(outgoing=True, pattern="doghd")
@errors_handler
async def doghd(event):
    dog = await inuatsume("jpg,png")
    await event.client.send_file(await event.client.get_input_entity(event.chat_id), dog[0]["url"], force_document=True)
    await event.delete()


@register(outgoing=True, pattern="doggif")
@errors_handler
async def doggif(event):
    dog = await inuatsume("gif")
    await event.client.send_file(await event.client.get_input_entity(event.chat_id), dog[0]["url"])
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