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
