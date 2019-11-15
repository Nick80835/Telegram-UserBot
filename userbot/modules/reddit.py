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
import mimetypes
from random import choice

import praw
from aiohttp import ClientSession
from prawcore.exceptions import NotFound

from userbot import CMD_HELP
from userbot.events import errors_handler, register

REDDIT = praw.Reddit(client_id='-fmzwojFG6JkGg',
                     client_secret=None,
                     user_agent='TG_Userbot')

VALID_ENDS = (".mp4", ".jpg", ".jpeg", ".png", ".gif")


async def imagefetcherfallback(sub):
    hot = REDDIT.subreddit(sub).hot()
    hot_list = list(hot.__iter__())

    for _ in range(10):
        post = choice(hot_list)

        try:
            if post.url:
                if post.url.endswith(VALID_ENDS):
                    return post.url, post.title, None
        except NotFound:
            return None, None, True

    return None, None, None


async def titlefetcherfallback(sub):
    hot = REDDIT.subreddit(sub).hot()
    hot_list = list(hot.__iter__())

    try:
        post_title = choice(hot_list).title
    except NotFound:
        return None, True

    return post_title, None


async def imagefetcher(event, sub):
    await event.edit(f"`Fetching from `**r/{sub}**`…`")
    image_url = False

    for _ in range(10):
        try:
            post = REDDIT.subreddit(sub).random()
        except NotFound:
            await event.edit(f"**r/{sub}**` doesn't seem to exist!`")
            return

        if not post:
            image_url, title, error = await imagefetcherfallback(sub)
            if error:
                await event.edit(f"**r/{sub}**` doesn't seem to exist!`")
                return
            break

        try:
            if post.url:
                if post.url.endswith(VALID_ENDS):
                    image_url = post.url
                    title = post.title
                    break
        except NotFound:
            await event.edit(f"**r/{sub}**` doesn't seem to exist!`")
            return

    if not image_url:
        await event.edit(f"`Failed to find any valid content on `**r/{sub}**`!`")
        return

    try:
        image_io = io.BytesIO()
        session = ClientSession()

        async with session.get(image_url) as response:
            if response.status == 200:
                image_io.write(await response.read())
                image_io.name = f"reddit_content{mimetypes.guess_extension(response.headers['content-type'])}"
                image_io.seek(0)
            else:
                raise Exception

        await session.close()
        await event.reply(title, file=image_io)
    except:
        await session.close()
        await event.edit(f"`Failed to download content from `**r/{sub}**`!`")


async def titlefetcher(event, sub):
    await event.edit(f"`Fetching from `**r/{sub}**`…`")

    post = REDDIT.subreddit(sub).random()

    if not post:
        title, error = await titlefetcherfallback(sub)
        if error:
            await event.edit(f"**r/{sub}**` doesn't seem to exist!`")
            return
    else:
        try:
            title = post.title
        except NotFound:
            await event.edit(f"**r/{sub}**` doesn't seem to exist!`")
            return

    await event.reply(title)


@register(outgoing=True, pattern="redi")
@errors_handler
async def redimg(event):
    sub = event.pattern_match.group(1)

    if sub:
        await imagefetcher(event, sub)
    else:
        event.edit("Syntax: .redi <subreddit name>")


@register(outgoing=True, pattern="redt")
@errors_handler
async def redtit(event):
    sub = event.pattern_match.group(1)

    if sub:
        await titlefetcher(event, sub)
    else:
        event.edit("Syntax: .redt <subreddit name>")


@register(outgoing=True, pattern="suffer")
@errors_handler
async def makemesuffer(event):
    await imagefetcher(event, "MakeMeSuffer")


@register(outgoing=True, pattern="snafu")
@errors_handler
async def coaxedintoasnafu(event):
    await imagefetcher(event, "CoaxedIntoASnafu")


@register(outgoing=True, pattern="aita")
@errors_handler
async def amitheasshole(event):
    await titlefetcher(event, "AmITheAsshole")


@register(outgoing=True, pattern="jon(x|)")
@errors_handler
async def imsorryjon(event):
    if "x" in event.pattern_match.group(0):
        sub = "ImReallySorryJon"
    else:
        sub = "ImSorryJon"

    await imagefetcher(event, sub)


@register(outgoing=True, pattern="tihi")
@errors_handler
async def thanksihateit(event):
    await imagefetcher(event, "TIHI")


CMD_HELP.update({
    'suffer':
    ".suffer"
    "\nUsage: Suffer."
})
CMD_HELP.update({
    'snafu':
    ".snafu"
    "\nUsage: Coaxed into a snafu."
})
CMD_HELP.update({
    'aita':
    ".aita"
    "\nUsage: Am I the asshole?"
})
CMD_HELP.update({
    'jon':
    ".jon(x)"
    "\nUsage: I'm (really) sorry Jon."
})
CMD_HELP.update({
    'redi':
    ".redi <subreddit name>"
    "\nUsage: Get random image content from any subreddit."
})
CMD_HELP.update({
    'redt':
    ".redt <subreddit name>"
    "\nUsage: Get random title content from any subreddit."
})
CMD_HELP.update({
    'tihi':
    ".tihi"
    "\nUsage: Thanks, I hate it."
})
