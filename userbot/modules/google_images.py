# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#

# Original source for the scraping code (used under the following license): https://github.com/hardikvasa/google-images-download

# The MIT License (MIT)
#
# Copyright (c) 2015-2019 Hardik Vasa
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
""" Userbot module containing a proper google images scraper. """

import io
import json
import re

import requests

from userbot import CMD_HELP
from userbot.events import errors_handler, register

HEADERS = {'User-Agent': "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36"}


@register(outgoing=True, pattern="img")
@errors_handler
async def img_sampler(event):
    # For .img command, search and return images matching the query
    await event.edit("`Processing…`")
    query = event.pattern_match.group(1)
    lim = re.findall(r"lim=\d+", query)

    try:
        lim = lim[0]
        lim = int(lim.replace("lim=", ""))
        query = query.replace(f"lim={lim}", "")
    except IndexError:
        lim = 2

    if lim > 10:
        lim = 10
    elif lim < 1:
        lim = 1

    if not query or query is None:
        await event.edit("`You need to add search terms to find images!`")
        return

    # creating list of arguments
    arguments = {
        "keywords": query,
        "limit": lim,
        "format": "jpg"
    }

    # passing the arguments to the function
    image_urls = download_executor(arguments)
    image_streams = []

    for i in image_urls:
        image_io = io.BytesIO(requests.get(i, stream=True).content)
        image_io.name = "image.jpg"
        image_streams.append(image_io)

    try:
        await event.client.send_file(event.chat_id, image_streams)
    except TypeError:
        await event.edit("`The images failed to download! Oopsie!`")
        return

    await event.delete()


#
# Scraping code
#


def format_object(page_object):
    formatted_object = {}
    formatted_object['image_format'] = page_object['ity']
    formatted_object['image_height'] = page_object['oh']
    formatted_object['image_width'] = page_object['ow']
    formatted_object['image_link'] = page_object['ou']
    formatted_object['image_description'] = page_object['pt']
    formatted_object['image_host'] = page_object['rh']
    formatted_object['image_source'] = page_object['ru']
    formatted_object['image_thumbnail_url'] = page_object['tu']
    return formatted_object


def build_url_parameters(arguments):
    built_url = "&tbs="
    counter = 0
    params = {'format':[arguments['format'],{'jpg':'ift:jpg','gif':'ift:gif','png':'ift:png','bmp':'ift:bmp','svg':'ift:svg','webp':'webp','ico':'ift:ico','raw':'ift:craw'}]}

    for _, value in params.items():
        if value[0] is not None:
            ext_param = value[1][value[0]]
            # counter will tell if it is first param added or not
            if counter == 0:
                # add it to the built url
                built_url = built_url + ext_param
                counter += 1
            else:
                built_url = built_url + ',' + ext_param
                counter += 1

    return built_url


def build_search_url(search_term, params):
    return 'https://www.google.com/search?q=' + requests.utils.quote(
        search_term.encode('utf-8')) + '&espv=2&biw=1366&bih=667&site=webhp&source=lnms&tbm=isch' + params + '&sa=X&ei=XosDVaCXD8TasATItgE&ved=0CAcQ_AUoAg'


def get_next_item(page):
    start_line = page.find('rg_meta notranslate')
    if start_line == -1:  # If no links are found then give an error!
        end_quote = 0
        link = "no_links"
        return link, end_quote
    else:
        start_line = page.find('class="rg_meta notranslate">')
        start_object = page.find('{', start_line + 1)
        end_object = page.find('</div>', start_object + 1)
        object_raw = str(page[start_object:end_object])

        try:
            object_decode = bytes(object_raw, "utf-8").decode("unicode_escape")
            final_object = json.loads(object_decode)
        except Exception:
            final_object = ""

        return final_object, end_object


def get_all_items(page, limit):
    count = 0
    image_urls = []

    while count < limit:
        page_object, end_content = get_next_item(page)
        if page_object == "no_links":
            break
        elif page_object == "":
            page = page[end_content:]
        else:
            page_object = format_object(page_object)
            image_urls.append(page_object['image_link'])
            page = page[end_content:]

        count += 1

    return image_urls


def download_executor(arguments):
    search_keyword = [str(item) for item in arguments['keywords'].split(',')]
    limit = int(arguments['limit'])

    count = 0
    image_urls = []

    while count < len(search_keyword): # perform a search for every keyword
        search_term = search_keyword[count]
        params = build_url_parameters(arguments) # build URL with params
        url = build_search_url(search_term, params) # build full search url
        raw_html = requests.get(url, headers=HEADERS).text # download page
        image_url_list = get_all_items(raw_html, limit) # get all desired image urls

        for img_url in image_url_list:
            image_urls.append(img_url)

        count += 1

    return image_urls


CMD_HELP.update({
    'img':
    ".img <search query>,<search query 2> <lim=#>"
    "\nUsage: Does an image search on Google and shows two or lim images for each query."
})
