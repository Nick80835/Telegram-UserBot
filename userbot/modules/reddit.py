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

import praw

from userbot import CMD_HELP
from userbot.events import errors_handler, register

REDDIT = praw.Reddit(client_id='-fmzwojFG6JkGg',
                     client_secret=None,
                     user_agent='TG_Userbot')


@register(outgoing=True, pattern="suffer")
@errors_handler
async def makemesuffer(event):
    for _ in range(10):
        post = REDDIT.subreddit('makemesuffer').random()

        if post.url:
            image_url = post.url
            break

    if not image_url:
        await event.edit("`Failed to find any valid content!`")
        return

    try:
        await event.client.send_file(event.chat_id, image_url)
        await event.delete()
    except:
        await event.edit("`Failed to download content!`")


@register(outgoing=True, pattern="snafu")
@errors_handler
async def coaxedintoasnafu(event):
    for _ in range(10):
        post = REDDIT.subreddit('coaxedintoasnafu').random()

        if post.url:
            image_url = post.url
            break

    if not image_url:
        await event.edit("`Failed to find any valid content!`")
        return

    try:
        await event.client.send_file(event.chat_id, image_url)
        await event.delete()
    except:
        await event.edit("`Failed to download content!`")


@register(outgoing=True, pattern="aita")
@errors_handler
async def amitheasshole(event):
    for _ in range(10):
        post = REDDIT.subreddit('amitheasshole').random()

        if post.title:
            title_text = post.title
            break

    if not title_text:
        await event.edit("`Failed to find any valid content!`")
        return

    await event.reply(title_text)
    await event.delete()


@register(outgoing=True, pattern="jon(x|)")
@errors_handler
async def imsorryjon(event):
    if "x" in event.pattern_match.group(0):
        sub = "imreallysorryjon"
    else:
        sub = "imsorryjon"

    for _ in range(10):
        post = REDDIT.subreddit(sub).random()

        if post.url:
            image_url = post.url
            break

    if not image_url:
        await event.edit("`Failed to find any valid content!`")
        return

    try:
        await event.client.send_file(event.chat_id, image_url)
        await event.delete()
    except:
        await event.edit("`Failed to download content!`")


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
