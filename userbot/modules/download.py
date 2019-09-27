# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#
# The entire source code is OSSRPL except
# 'download, uploadir, uploadas, upload' which is MPL
# License: MPL and OSSRPL
""" Userbot module which contains everything related to
    downloading/uploading from/to the server. """

import json, os, logging, mimetypes, re, subprocess, psutil
from datetime import datetime
from io import BytesIO
from time import sleep
from telethon.tl.types import DocumentAttributeVideo, MessageMediaPhoto
from pyDownload import Downloader
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from userbot import LOGS, CMD_HELP, CMDPREFIX
from userbot.events import register, errors_handler

TEMP_DOWNLOAD_DIRECTORY = os.environ.get("TMP_DOWNLOAD_DIRECTORY", "./")


def progress(current, total):
    # Logs the download progress
    LOGS.info("Downloaded %s of %s\nCompleted %s", current, total,
              (current / total) * 100)


async def download_from_url(url: str, file_name: str) -> str:
    # Download files from URL
    start = datetime.now()
    downloader = Downloader(url=url)
    if downloader.is_running:
        sleep(1)
    end = datetime.now()
    duration = (end - start).seconds
    os.rename(downloader.file_name, file_name)
    status = f"Downloaded `{file_name}` in {duration} seconds."
    return status


async def download_from_tg(event) -> (str, BytesIO):
    # Download files from Telegram
    async def dl_file(buffer: BytesIO) -> BytesIO:
        buffer = await event.client.download_media(
            reply_msg,
            buffer,
            progress_callback=progress,
        )
        return buffer

    start = datetime.now()
    buf = BytesIO()
    reply_msg = await event.get_reply_message()
    avail_mem = psutil.virtual_memory().available + psutil.swap_memory().free
    try:
        if reply_msg.media.document.size >= avail_mem:  # unlikely to happen but baalaji crai
            filen = await event.client.download_media(
                reply_msg,
                progress_callback=progress,
            )
        else:
            buf = await dl_file(buf)
            filen = reply_msg.media.document.attributes[0].file_name
    except AttributeError:
        buf = await dl_file(buf)
        try:
            filen = reply_msg.media.document.attributes[0].file_name
        except AttributeError:
            if isinstance(reply_msg.media, MessageMediaPhoto):
                filen = 'photo-' + str(datetime.today())\
                    .split('.')[0].replace(' ', '-') + '.jpg'
            else:
                filen = reply_msg.media.document.mime_type\
                    .replace('/', '-' + str(datetime.today())
                             .split('.')[0].replace(' ', '-') + '.')
    end = datetime.now()
    duration = (end - start).seconds
    await event.edit(f"`Downloaded {filen} in {duration} seconds.`")
    return filen, buf


@register(outgoing=True, pattern=f"^{CMDPREFIX}download(?: |$)(.*)")
@errors_handler
async def download(event):
    # For .download command, download files to the userbot's server
    if event.fwd_from:
        return
    await event.edit("Processing ...")
    input_str = event.pattern_match.group(1)
    reply_msg = await event.get_reply_message()
    if not os.path.isdir(TEMP_DOWNLOAD_DIRECTORY):
        os.makedirs(TEMP_DOWNLOAD_DIRECTORY)
    if reply_msg and reply_msg.media:
        await event.edit('`Downloading file from Telegram....`')
        filen, buf = await download_from_tg(event)
        if buf:
            with open(filen, 'wb') as to_save:
                to_save.write(buf.read())
    elif "|" in input_str:
        url, file_name = input_str.split("|")
        url = url.strip()
        file_name = file_name.strip()
        await event.edit(f'`Downloading {file_name}`')
        status = await download_from_url(url, file_name)
        await event.edit(status)
    else:
        await event.edit("`Reply to a message to \
            download to my local server.`\n")


@register(outgoing=True, pattern=f"^{CMDPREFIX}uploadir (.*)")
@errors_handler
async def uploadir(event):
    # For .uploadir command, allows you to upload
    # everything from a folder in the server
    if event.fwd_from:
        return
    input_str = event.pattern_match.group(1)
    if os.path.exists(input_str):
        start = datetime.now()
        await event.edit("Processing ...")
        lst_of_files = []
        for r, d, f in os.walk(input_str):
            for file in f:
                lst_of_files.append(os.path.join(r, file))
            for file in d:
                lst_of_files.append(os.path.join(r, file))
        LOGS.info(lst_of_files)
        uploaded = 0
        await event.edit("Found {} files. Uploading will \
                start soon. Please wait!".format(len(lst_of_files)))
        for single_file in lst_of_files:
            if os.path.exists(single_file):
                # https://stackoverflow.com/a/678242/4723940
                caption_rts = os.path.basename(single_file)
                if not caption_rts.lower().endswith(".mp4"):
                    await event.client.send_file(
                        event.chat_id,
                        single_file,
                        caption=caption_rts,
                        force_document=False,
                        allow_cache=False,
                        reply_to=event.message.id,
                        progress_callback=progress,
                    )
                else:
                    thumb_image = os.path.join(input_str, "thumb.jpg")
                    metadata = extractMetadata(createParser(single_file))
                    duration = 0
                    width = 0
                    height = 0
                    if metadata.has("duration"):
                        duration = metadata.get("duration").seconds
                    if metadata.has("width"):
                        width = metadata.get("width")
                    if metadata.has("height"):
                        height = metadata.get("height")
                    await event.client.send_file(
                        event.chat_id,
                        single_file,
                        caption=caption_rts,
                        thumb=thumb_image,
                        force_document=False,
                        allow_cache=False,
                        reply_to=event.message.id,
                        attributes=[
                            DocumentAttributeVideo(
                                duration=duration,
                                w=width,
                                h=height,
                                round_message=False,
                                supports_streaming=True,
                            )
                        ],
                        progress_callback=progress,
                    )
                os.remove(single_file)
                uploaded = uploaded + 1
        end = datetime.now()
        duration = (end - start).seconds
        await event.edit("Uploaded {} files in {} seconds.".format(
            uploaded, duration))
    else:
        await event.edit("404: Directory Not Found")


@register(outgoing=True, pattern=f"^{CMDPREFIX}upload (.*)")
@errors_handler
async def upload(event):
    # For .upload command, allows you to
    # upload a file from the userbot's server
    if event.fwd_from:
        return
    if event.is_channel and not event.is_group:
        await event.edit("`Uploading isn't permitted on channels`")
        return
    await event.edit("Processing ...")
    input_str = event.pattern_match.group(1)
    if input_str in ("userbot.session", "config.env"):
        await event.edit("`That's a dangerous operation! Not Permitted!`"
                            )
        return
    if os.path.exists(input_str):
        start = datetime.now()
        await event.client.send_file(
            event.chat_id,
            input_str,
            force_document=True,
            allow_cache=False,
            reply_to=event.message.id,
            progress_callback=progress,
        )
        end = datetime.now()
        duration = (end - start).seconds
        await event.edit("Uploaded in {} seconds.".format(duration))
    else:
        await event.edit("404: File Not Found")


def get_video_thumb(file, output=None, width=90):
    # Get video thhumbnail
    metadata = extractMetadata(createParser(file))
    popen = subprocess.Popen(
        [
            "ffmpeg",
            "-i",
            file,
            "-ss",
            str(
                int((0, metadata.get("duration").seconds
                     )[metadata.has("duration")] / 2)),
            "-filter:v",
            "scale={}:-1".format(width),
            "-vframes",
            "1",
            output,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    if not popen.returncode and os.path.lexists(file):
        return output
    return None


def extract_w_h(file):
    # Get width and height of media
    command_to_run = [
        "ffprobe",
        "-v",
        "quiet",
        "-print_format",
        "json",
        "-show_format",
        "-show_streams",
        file,
    ]
    # https://stackoverflow.com/a/11236144/4723940
    try:
        t_response = subprocess.check_output(command_to_run,
                                             stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as exc:
        LOGS.warning(exc)
    else:
        x_reponse = t_response.decode("UTF-8")
        response_json = json.loads(x_reponse)
        width = int(response_json["streams"][0]["width"])
        height = int(response_json["streams"][0]["height"])
        return width, height


@register(outgoing=True, pattern=f"^{CMDPREFIX}uploadas(stream|vn|all) (.*)")
@errors_handler
async def uploadas(event):
    # For .uploadas command, allows you
    # to specify some arguments for upload.
    if event.fwd_from:
        return
    await event.edit("Processing ...")
    type_of_upload = event.pattern_match.group(1)
    supports_streaming = False
    round_message = False
    spam_big_messages = False
    if type_of_upload == "stream":
        supports_streaming = True
    if type_of_upload == "vn":
        round_message = True
    if type_of_upload == "all":
        spam_big_messages = True
    input_str = event.pattern_match.group(2)
    thumb = None
    file_name = None
    if "|" in input_str:
        file_name, thumb = input_str.split("|")
        file_name = file_name.strip()
        thumb = thumb.strip()
    else:
        file_name = input_str
        thumb_path = "a_random_f_file_name" + ".jpg"
        thumb = get_video_thumb(file_name, output=thumb_path)
    if os.path.exists(file_name):
        start = datetime.now()
        metadata = extractMetadata(createParser(file_name))
        duration = 0
        width = 0
        height = 0
        if metadata.has("duration"):
            duration = metadata.get("duration").seconds
        if metadata.has("width"):
            width = metadata.get("width")
        if metadata.has("height"):
            height = metadata.get("height")
        try:
            if supports_streaming:
                await event.client.send_file(
                    event.chat_id,
                    file_name,
                    thumb=thumb,
                    caption=input_str,
                    force_document=False,
                    allow_cache=False,
                    reply_to=event.message.id,
                    attributes=[
                        DocumentAttributeVideo(
                            duration=duration,
                            w=width,
                            h=height,
                            round_message=False,
                            supports_streaming=True,
                        )
                    ],
                    progress_callback=progress,
                )
            elif round_message:
                await event.client.send_file(
                    event.chat_id,
                    file_name,
                    thumb=thumb,
                    allow_cache=False,
                    reply_to=event.message.id,
                    video_note=True,
                    attributes=[
                        DocumentAttributeVideo(
                            duration=0,
                            w=1,
                            h=1,
                            round_message=True,
                            supports_streaming=True,
                        )
                    ],
                    progress_callback=progress,
                )
            elif spam_big_messages:
                await event.edit("TBD: Not (yet) Implemented")
                return
            end = datetime.now()
            duration = (end - start).seconds
            os.remove(thumb)
            await event.edit("Uploaded in {} seconds.".format(duration)
                                    )
        except FileNotFoundError as err:
            await event.edit(str(err))
    else:
        await event.edit("404: File Not Found")


CMD_HELP.update({
    "download":
    ".download [in reply to TG file]\n"
    "or .download <link> | <filename>\n"
    "Usage: Download a file from telegram or link to the server."
})
CMD_HELP.update({
    "upload":
    ".upload <link>\nUsage: Upload a "
    "locally stored file to Telegram."
})
CMD_HELP.update({
    "drive":
    ".upload <file>\nUsage: Upload a locally stored file to GDrive."
})
CMD_HELP.update({
    "mirror":
    ".mirror [in reply to TG file]\n"
    "or .mirror <link> | <filename>\n"
    "Usage: Download a file from telegram "
    "or link to the server then upload to your GDrive."
})
