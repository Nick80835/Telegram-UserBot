# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#
""" Userbot module containing various scrapers. """

import io
import os
import re

from emoji import get_emoji_regexp
from googletrans import LANGUAGES, Translator
from gtts import gTTS
from wikipedia import summary
from wikipedia.exceptions import DisambiguationError, PageError

from userbot import BOTLOG, BOTLOG_CHATID, CMD_HELP
from userbot.events import errors_handler, register

LANG = "en"


@register(outgoing=True, pattern="google")
@errors_handler
async def gsearch(event):
    # For .google command, do a Google search
    from search_engine_parser import GoogleSearch

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
        await event.edit("`Give a text or reply to a message for Text-to-Speech!`")
        return

    tts_bytesio = io.BytesIO()
    tts_bytesio.name = "tts.mp3"

    try:
        tts = gTTS(message, lang=LANG)
        tts.write_to_fp(tts_bytesio)
        tts_bytesio.seek(0)
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

    await event.client.send_file(event.chat_id, tts_bytesio, voice_note=True)
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


def de_emojify(input_string):
    # Remove emojis and other non-safe characters from string
    return get_emoji_regexp().sub(u'', input_string)


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
