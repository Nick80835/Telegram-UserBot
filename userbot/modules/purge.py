# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#
""" Userbot module for purging unneeded messages(usually spam or ot). """

from asyncio import sleep

from telethon.errors import rpcbaseerrors

from userbot import BOTLOG, BOTLOG_CHATID, CMD_HELP, CMDPREFIX
from userbot.events import register, errors_handler


@register(outgoing=True, pattern=f"^{CMDPREFIX}purge$")
@errors_handler
async def fastpurger(event):
    # For .purge command, purge all messages starting from the reply
    chat = await event.get_input_chat()
    msgs = []
    count = 0

    async for msg in event.client.iter_messages(
            chat, min_id=event.reply_to_msg_id):
        msgs.append(msg)
        count = count + 1
        msgs.append(event.reply_to_msg_id)
        if len(msgs) == 100:
            await event.client.delete_messages(chat, msgs)
            msgs = []

    if msgs:
        await event.client.delete_messages(chat, msgs)
    done = await event.client.send_message(
        event.chat_id,
        "`Fast purge complete!\n`Purged " + str(count) +
        " messages. **This auto-generated message " +
        "  shall be self destructed in 2 seconds.**",
    )

    if BOTLOG:
        await event.client.send_message(
            BOTLOG_CHATID,
            "Purge of " + str(count) + " messages done successfully.")
    await sleep(2)
    await done.delete()


@register(outgoing=True, pattern=f"^{CMDPREFIX}purgeme")
@errors_handler
async def purgeme(event):
    # For .purgeme, delete x count of your latest message
    message = event.text
    count = int(message[9:])
    i = 1

    async for message in event.client.iter_messages(event.chat_id,
                                                    from_user='me'):
        if i > count + 1:
            break
        i = i + 1
        await message.delete()

    smsg = await event.client.send_message(
        event.chat_id,
        "`Purge complete!` Purged " + str(count) +
        " messages. **This auto-generated message " +
        " shall be self destructed in 2 seconds.**",
    )
    if BOTLOG:
        await event.client.send_message(
            BOTLOG_CHATID,
            "Purge of " + str(count) + " messages done successfully.")
    await sleep(2)
    i = 1
    await smsg.delete()


@register(outgoing=True, pattern=f"^{CMDPREFIX}del$")
@errors_handler
async def delete_it(event):
    # For .del command, delete the replied message
    msg_src = await event.get_reply_message()
    if event.reply_to_msg_id:
        try:
            await msg_src.delete()
            await event.delete()
            if BOTLOG:
                await event.client.send_message(
                    BOTLOG_CHATID, "Deletion of message was successful")
        except rpcbaseerrors.BadRequestError:
            if BOTLOG:
                await event.client.send_message(
                    BOTLOG_CHATID, "Well, I can't delete a message")


@register(outgoing=True, pattern=f"^{CMDPREFIX}editme")
@errors_handler
async def editer(event):
    # For .editme command, edit your last message
    message = event.text
    chat = await event.get_input_chat()
    self_id = await event.client.get_peer_id('me')
    string = str(message[8:])
    i = 1
    async for message in event.client.iter_messages(chat, self_id):
        if i == 2:
            await message.edit(string)
            await event.delete()
            break
        i = i + 1
    if BOTLOG:
        await event.client.send_message(
            BOTLOG_CHATID, "Edit query was executed successfully")


@register(outgoing=True, pattern=f"^{CMDPREFIX}sd")
@errors_handler
async def selfdestruct(event):
    # For .sd command, make seflf-destructable messages
    message = event.text
    counter = int(message[4:6])
    text = str(event.text[6:])
    await event.delete()
    smsg = await event.client.send_message(event.chat_id, text)
    await sleep(counter)
    await smsg.delete()
    if BOTLOG:
        await event.client.send_message(BOTLOG_CHATID,
                                            "sd query done successfully")


CMD_HELP.update({
    'purge':
    '.purge'
    '\nUsage: Purge all messages starting from the reply.'
})
CMD_HELP.update({
    'purgeme':
    '.purgeme <x>'
    '\nUsage: Delete x amount of your latest messages.'
})
CMD_HELP.update({
    "del":
    ".del" "\nUsage: Delete the message you replied to."
})
CMD_HELP.update({
    'editme':
    ".editme <newmessage>"
    "\nUsage: Edit the text you replied to with newtext."
})
CMD_HELP.update({
    'sd':
    '.sd <x> <message>'
    "\nUsage: Create a message that self-destructs in x seconds."
    '\nKeep the seconds under 100 since it puts your bot to sleep.'
})
