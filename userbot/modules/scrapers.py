# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#
""" Userbot module containing various scrapers. """

import os
import re

import aiohttp
from emoji import get_emoji_regexp
from google_images_download import google_images_download
from googletrans import LANGUAGES, Translator
from gtts import gTTS
from pytube import YouTube
from pytube.helpers import safe_filename
from requests import get
from search_engine_parser import GoogleSearch
from wikipedia import summary
from wikipedia.exceptions import DisambiguationError, PageError

from userbot import BOTLOG, BOTLOG_CHATID, CMD_HELP, bot
from userbot.events import errors_handler, register

LANG = "en"
UD_QUERY_URL = 'http://api.urbandictionary.com/v0/define'
UD_RANDOM_URL = 'http://api.urbandictionary.com/v0/random'


@register(outgoing=True, pattern="img")
@errors_handler
async def img_sampler(event):
    # For .img command, search and return images matching the query
    await event.edit("Processing…")
    query = event.pattern_match.group(1)
    lim = re.findall(r"lim=\d+", query)
    try:
        lim = lim[0]
        lim = lim.replace("lim=", "")
        query = query.replace("lim=" + lim[0], "")
    except IndexError:
        lim = 2
    response = google_images_download.googleimagesdownload()

    # creating list of arguments
    arguments = {
        "keywords": query,
        "limit": lim,
        "format": "jpg",
        "no_directory": "no_directory"
    }

    # passing the arguments to the function
    paths = response.download(arguments)
    lst = paths[0][query]

    try:
        await event.client.send_file(await event.client.get_input_entity(event.chat_id), lst)
    except TypeError:
        await event.edit(f"`The images failed to download! Oopsie!`")
        return

    os.remove(lst[0])
    os.remove(lst[1])
    os.rmdir(os.path.dirname(os.path.abspath(lst[0])))
    await event.delete()


@register(outgoing=True, pattern="google")
@errors_handler
async def gsearch(event):
    # For .google command, do a Google search
    match = event.pattern_match.group(1)
    page = re.findall(r"page=\d+", match)
    try:
        page = page[0]
        page = page.replace("page=", "")
        match = match.replace("page=" + page[0], "")
    except IndexError:
        page = 1
    search_args = (str(match), int(page))
    google_search = GoogleSearch()
    gresults = google_search.search(*search_args)
    msg = ""
    for i in range(10):
        try:
            title = gresults["titles"][i]
            link = gresults["links"][i]
            desc = gresults["descriptions"][i]
            msg += f"{i}. [{title}]({link})\n`{desc}`\n\n"
        except IndexError:
            break
    await event.edit("**Search Query:**\n`" + match +
                     "`\n\n**Results:**\n" + msg,
                     link_preview=False)
    if BOTLOG:
        await event.client.send_message(
            BOTLOG_CHATID,
            "Google Search query `" + match +
            "` was executed successfully",
        )


@register(outgoing=True, pattern="wiki")
@errors_handler
async def wiki(event):
    # For .google command, fetch content from Wikipedia
    match = event.pattern_match.group(1)
    try:
        summary(match)
    except DisambiguationError as error:
        await event.edit(f"Disambiguated page found.\n\n{error}")
        return
    except PageError as pageerror:
        await event.edit(f"Page not found.\n\n{pageerror}")
        return
    result = summary(match)
    if len(result) >= 4096:
        file = open("output.txt", "w+")
        file.write(result)
        file.close()
        await event.client.send_file(
            event.chat_id,
            "output.txt",
            reply_to=event.id,
            caption="`Output too large, sending as file`",
        )
        if os.path.exists("output.txt"):
            os.remove("output.txt")
        return
    await event.edit("**Search:**\n`" + match + "`\n\n**Result:**\n" +
                     result)
    if BOTLOG:
        await event.client.send_message(
            BOTLOG_CHATID, f"Wiki query {match} was executed successfully")


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


@register(outgoing=True, pattern="tts")
@errors_handler
async def text_to_speech(event):
    # For .tts command, a wrapper for Google Text-to-Speech
    textx = await event.get_reply_message()
    message = event.pattern_match.group(1)
    if message:
        pass
    elif textx:
        message = textx.text
    else:
        await event.edit("`Give a text or reply to a "
                         "message for Text-to-Speech!`")
        return

    try:
        gTTS(message, LANG)
    except AssertionError:
        await event.edit('The text is empty.\n'
                         'Nothing left to speak after pre-precessing, '
                         'tokenizing and cleaning.')
        return
    except ValueError:
        await event.edit('Language is not supported.')
        return
    except RuntimeError:
        await event.edit('Error loading the languages dictionary.')
        return
    tts = gTTS(message, LANG)
    tts.save("k.mp3")
    with open("k.mp3", "rb") as audio:
        linelist = list(audio)
        linecount = len(linelist)
    if linecount == 1:
        tts = gTTS(message, LANG)
        tts.save("k.mp3")
    with open("k.mp3", "r"):
        await event.client.send_file(event.chat_id, "k.mp3", voice_note=True)
        os.remove("k.mp3")
        if BOTLOG:
            await event.client.send_message(
                BOTLOG_CHATID,
                "tts of " + message + " executed successfully!")
        await event.delete()


@register(outgoing=True, pattern="trt")
@errors_handler
async def translateme(event):
    # For .trt command, translate the given text using Google Translate
    translator = Translator()
    textx = await event.get_reply_message()
    message = event.pattern_match.group(1)
    if message:
        pass
    elif textx:
        message = textx.text
    else:
        await event.edit("`Give a text or reply to a message to translate!`")
        return

    try:
        reply_text = translator.translate(de_emojify(message), dest=LANG)
    except ValueError:
        await event.edit("`Invalid destination language.`")
        return

    source_lan = LANGUAGES[f'{reply_text.src.lower()}']
    transl_lan = LANGUAGES[f'{reply_text.dest.lower()}']
    reply_text = f"**Source ({source_lan.title()}):**`\n{message}`**\n\
\nTranslation ({transl_lan.title()}):**`\n{reply_text.text}`"

    await event.edit(reply_text)

    if BOTLOG:
        await event.client.send_message(
            BOTLOG_CHATID,
            f"Translate query {message} was executed successfully",
        )


@register(outgoing=True, pattern="lang")
@errors_handler
async def lang(event):
    # For .lang command, change the default langauge of userbot scrapers
    global LANG
    LANG = event.pattern_match.group(1)
    await event.edit(f"`Default language changed to` **{LANG}**")
    if BOTLOG:
        await event.client.send_message(
            BOTLOG_CHATID, f"`Default language changed to` **{LANG}**")


@register(outgoing=True, pattern="yt_dl")
@errors_handler
async def download_video(event):
    # For .yt_dl command, download videos from YouTube
    url = event.pattern_match.group(1)
    quality = event.pattern_match.group(2)

    await event.edit("`Fetching…`")

    video = YouTube(url)

    if quality:
        video_stream = video.streams.filter(progressive=True,
                                            subtype="mp4",
                                            res=quality).first()
    else:
        video_stream = video.streams.filter(progressive=True,
                                            subtype="mp4").first()

    if video_stream is None:
        all_streams = video.streams.filter(progressive=True, subtype="mp4").all()
        available_qualities = ""

        for item in all_streams[:-1]:
            available_qualities += f"{item.resolution}, "
        available_qualities += all_streams[-1].resolution

        await event.edit("**A stream matching your query wasn't found. "
                         "Try again with different options.\n**"
                         "**Available Qualities:**\n"
                         f"{available_qualities}")
        return

    video_size = video_stream.filesize / 1000000

    if video_size >= 50:
        await event.edit(
            ("**File larger than 50MB. Sending the link instead.\n**"
             f"Get the video [here]({video_stream.url})\n\n"
             "**If the video plays instead of downloading, "
             "right click(or long press on touchscreen) and "
             "press 'Save Video As…'(may depend on the browser) "
             "to download the video.**"))
        return

    await event.edit("**Downloading...**")

    video_stream.download(filename=video.title)

    url = f"https://img.youtube.com/vi/{video.video_id}/maxresdefault.jpg"
    resp = get(url)
    with open('thumbnail.jpg', 'wb') as file:
        file.write(resp.content)

    await event.edit("**Uploading...**")
    await bot.send_file(event.chat_id,
                        f'{safe_filename(video.title)}.mp4',
                        caption=f"{video.title}",
                        thumb="thumbnail.jpg")

    os.remove(f"{safe_filename(video.title)}.mp4")
    os.remove('thumbnail.jpg')
    await event.delete()


def de_emojify(input_string):
    # Remove emojis and other non-safe characters from string
    return get_emoji_regexp().sub(u'', input_string)


CMD_HELP.update({
    'img':
    ".img <search_query>"
    "\nUsage: Does an image search on Google and shows two images."
})
CMD_HELP.update({
    'google':
    ".google <search_query>"
    "\nUsage: Does a search on Google."
})
CMD_HELP.update({
    'wiki':
    ".wiki <search_query>"
    "\nUsage: Does a Wikipedia search."
})
CMD_HELP.update({
    'ud':
    ".ud <search_query>"
    "\nUsage: Does a search on Urban Dictionary."
})
CMD_HELP.update({
    'tts':
    ".tts <text> or reply to someones text with .trt"
    "\nUsage: Translates text to speech for the default language which is set."
})
CMD_HELP.update({
    'trt':
    ".trt <text> or reply to someones text with .trt"
    "\nUsage: Translates text to the default language which is set."
})
CMD_HELP.update({
    'lang':
    ".lang <lang>"
    "\nUsage: Changes the default language of"
    "userbot scrapers used for Google TRT, "
    "TTS may not work."
})
CMD_HELP.update({
    'yt_dl':
    ".yt_dl <url> <quality>(optional)"
    "\nUsage: Download videos from YouTube. "
    "If no quality is specified, the highest downloadable quality is "
    "downloaded. Will send the link if the video is larger than 50 MB."
})
