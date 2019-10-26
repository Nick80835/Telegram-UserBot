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

import praw
import requests

from userbot import CMD_HELP
from userbot.events import errors_handler, register

TOKEN_URL = "https://www.reddit.com/api/v1/access_token"

REDDIT_URL = "https://reddit.com/r/{}/hot"
HOT_PARAMS = {"g": "GLOBAL"}


async def get_reddit():
    reddit = praw.Reddit(client_id='-fmzwojFG6JkGg',
                         client_secret=None,
                         user_agent='TG_Userbot')

    return reddit


@register(outgoing=True, pattern="suffer")
@errors_handler
async def makemesuffer(event):
    reddit = await get_reddit()

    for _ in range(10):
        post = reddit.subreddit('makemesuffer').random()

        if post.url:
            image_url = post.url
            break

    if not image_url:
        await event.edit("`Failed to find any valid content!`")
        return

    try:
        await event.client.send_file(event.chat_id, image_url)
    except:
        await event.edit("`Failed to download content!`")


CMD_HELP.update({
    'suffer':
    ".suffer"
    "\nUsage: Suffer."
})
