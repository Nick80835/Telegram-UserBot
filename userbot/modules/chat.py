# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
""" Userbot module containing userid, chatid and log commands"""

from time import sleep

from telethon.tl.functions.channels import LeaveChannelRequest

from userbot import BOTLOG, BOTLOG_CHATID, CMD_HELP
from userbot.events import errors_handler, register


@register(outgoing=True, pattern="userid")
@errors_handler
async def useridgetter(event):
    # For .userid command, returns the ID of the target user
    message = await event.get_reply_message()
    if message:
        if not message.forward:
            user_id = message.sender.id
            if message.sender.username:
                name = f"@{message.sender.username}"
            else:
                name = f"**{message.sender.first_name}**"
        else:
            user_id = message.forward.sender.id
            if message.forward.sender.username:
                name = f"@{message.forward.sender.username}"
            else:
                name = f"**{message.forward.sender.first_name}**"
        await event.edit(f"**Name:** {name}\n**User ID:** `{user_id}`")
    else:
        await event.edit(f"`Reply to someone to get their user ID!`")


@register(outgoing=True, pattern="chatid")
@errors_handler
async def chatidgetter(event):
    # For .chatid, returns the ID of the chat you are in at that moment.
    await event.edit(f"**Chat ID:** `{event.chat_id}`")


@register(outgoing=True, pattern="log")
@errors_handler
async def log(event):
    # For .log command, forwards a message
    # or the command argument to the bot logs group
    if BOTLOG:
        if event.reply_to_msg_id:
            reply_msg = await event.get_reply_message()
            await reply_msg.forward_to(BOTLOG_CHATID)
        elif event.pattern_match.group(1):
            user = f"#LOG / Chat ID: {event.chat_id}\n\n"
            textx = user + event.pattern_match.group(1)
            await event.client.send_message(BOTLOG_CHATID, textx)
        else:
            await event.edit("`What am I supposed to log?`")
            return
        await event.edit("`Logged Successfully`")
    else:
        await event.edit("`This feature requires Logging to be enabled!`")
        return

    sleep(2)
    await event.delete()


@register(outgoing=True, pattern="kickme")
@errors_handler
async def kickme(event):
    # Basically it's .kickme command
    await event.edit("`Nope, no, no, I go away!`")
    await event.client(LeaveChannelRequest(event.chat_id))


CMD_HELP.update({
    "chatid":
    "Fetch the current chat's ID"
})
CMD_HELP.update({
    "userid":
    "Fetch the ID of the user in reply or the "
    "original author of a forwarded message."
})
CMD_HELP.update({
    "log":
    "Forward the message you've replied to to your "
    "botlog group."
})
CMD_HELP.update({
    "kickme":
    "Leave from a targeted group."
})
