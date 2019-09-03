# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#
""" Userbot module for changing your Telegram profile details. """

import os
from telethon.errors import ImageProcessFailedError, PhotoCropSizeSmallError
from telethon.errors.rpcerrorlist import (PhotoExtInvalidError,
                                          UsernameOccupiedError)
from telethon.tl.functions.account import (UpdateProfileRequest,
                                           UpdateUsernameRequest)
from telethon.tl.functions.photos import (DeletePhotosRequest,
                                          GetUserPhotosRequest,
                                          UploadProfilePhotoRequest)
from telethon.tl.types import InputPhoto, MessageMediaPhoto
from userbot import CMD_HELP, bot, CMDPREFIX
from userbot.events import register, errors_handler

# ====================== CONSTANT ===============================
INVALID_MEDIA = "```The extension of the media entity is invalid.```"
PP_CHANGED = "```Profile picture changed successfully.```"
PP_TOO_SMOL = "```This image is too small, use a bigger image.```"
PP_ERROR = "```Failure occured while processing image.```"

BIO_SUCCESS = "```Successfully edited Bio.```"

NAME_OK = "```Your name was successfully changed.```"
USERNAME_SUCCESS = "```Your username was successfully changed.```"
USERNAME_TAKEN = "```This username is already taken.```"

# ===============================================================


@register(outgoing=True, pattern=f"^{CMDPREFIX}name")
@errors_handler
async def update_name(event):
    # For .name command, change your name in Telegram
    newname = event.text[6:]
    if " " not in newname:
        firstname = newname
        lastname = ""
    else:
        namesplit = newname.split(" ", 1)
        firstname = namesplit[0]
        lastname = namesplit[1]

    await bot(
        UpdateProfileRequest(first_name=firstname, last_name=lastname))
    await event.edit(NAME_OK)


@register(outgoing=True, pattern=f"^{CMDPREFIX}profilepic$")
@errors_handler
async def set_profilepic(event):
    # For .profilepic command, change your profile picture in Telegram
    replymsg = await event.get_reply_message()
    photo = None
    if replymsg.media:
        if isinstance(replymsg.media, MessageMediaPhoto):
            photo = await bot.download_media(message=replymsg.photo)
        elif "image" in replymsg.media.document.mime_type.split('/'):
            photo = await bot.download_file(replymsg.media.document)
        else:
            await event.edit(INVALID_MEDIA)

    if photo:
        try:
            await bot(
                UploadProfilePhotoRequest(await bot.upload_file(photo)))
            os.remove(photo)
            await event.edit(PP_CHANGED)
        except PhotoCropSizeSmallError:
            await event.edit(PP_TOO_SMOL)
        except ImageProcessFailedError:
            await event.edit(PP_ERROR)
        except PhotoExtInvalidError:
            await event.edit(INVALID_MEDIA)


@register(outgoing=True, pattern=f"^{CMDPREFIX}setbio (.*)")
@errors_handler
async def set_biograph(event):
    # For .setbio command, set a new bio for your profile in Telegram
    newbio = event.pattern_match.group(1)
    await bot(UpdateProfileRequest(about=newbio))
    await event.edit(BIO_SUCCESS)


@register(outgoing=True, pattern=f"^{CMDPREFIX}username (.*)")
@errors_handler
async def update_username(event):
    # For .username command, set a new username in Telegram
    newusername = event.pattern_match.group(1)
    try:
        await bot(UpdateUsernameRequest(newusername))
        await event.edit(USERNAME_SUCCESS)
    except UsernameOccupiedError:
        await event.edit(USERNAME_TAKEN)


@register(outgoing=True, pattern=f"^{CMDPREFIX}delpfp")
@errors_handler
async def remove_profilepic(event):
    # For .delpfp command, delete your current
    # profile picture in Telegram
    group = event.text[8:]
    if group == 'all':
        lim = 0
    elif group.isdigit():
        lim = int(group)
    else:
        lim = 1

    pfplist = await bot(
        GetUserPhotosRequest(user_id=event.from_id,
                                offset=0,
                                max_id=0,
                                limit=lim))
    input_photos = []
    for sep in pfplist.photos:
        input_photos.append(
            InputPhoto(id=sep.id,
                        access_hash=sep.access_hash,
                        file_reference=sep.file_reference))
    await bot(DeletePhotosRequest(id=input_photos))
    await event.edit(
        f"`Successfully deleted {len(input_photos)} profile picture(s).`")


CMD_HELP.update({
    "username":
    ".username <new_username>"
    "\nUsage: Change your Telegram username."
})
CMD_HELP.update({
    "name":
    ".name <firstname> or .name <firstname> <lastname>"
    "\nUsage: Chane your Telegram name."
    "\n(First and last name will get split by the first space)"
})
CMD_HELP.update({
    "profilepic":
    ".profilepic"
    "\nUsage: Change your Telegram avatar with the replied photo."
})
CMD_HELP.update(
    {"setbio": ".setbio <new_bio>"
    "\nUsage: Change your Telegram bio."
})
CMD_HELP.update({
    "delpfp":
    ".delpfp or .delpfp <number>/<all>"
    "\nUsage: Delete your Telegram profile avatar(s)."
})
