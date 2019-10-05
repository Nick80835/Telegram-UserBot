# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#
# You can find misc modules, which dont fit in anything xD
""" Userbot module for other small commands. """

import sys
from os import execl
from random import choice, randint
from time import sleep

from userbot import BOTLOG, BOTLOG_CHATID, CMD_HELP
from userbot.events import errors_handler, register


@register(outgoing=True, pattern="random")
@errors_handler
async def randomise(event):
    # For .random command, get a random item from the list of event.
    if len(event.pattern_match.group().split()) > 1:
        itemlist = event.pattern_match.group().split()[1:]
        chosenitem = choice(itemlist)
        await event.edit("**Query: **\n`" + ' '.join(itemlist) +
                            "`\n**Output: **\n`" + chosenitem + "`")
    else:
        await event.edit("`Give me a list of stuff to pick from!`")


@register(outgoing=True, pattern="sleep")
@errors_handler
async def sleepybot(event):
    # For .sleep command, let the userbot snooze for a few second.
    if len(event.pattern_match.group().split()) > 1:
        counter = int(event.pattern_match.group().split()[1])
        await event.edit("`I'm sulking and snoozing…`")
        if BOTLOG:
            await event.client.send_message(
                BOTLOG_CHATID,
                f"You put the bot to sleep for {str(counter)} seconds",
            )
        sleep(counter)
        await event.edit("`Okay, I'm done sleeping!`")
        if randint(0, 4) == 1 and not event.chat.default_banned_rights.send_media:
            try:
                await event.reply(file="userbot/files/xp_startup.mp3")
            except:
                pass # it be like that sometimes
    else:
        await event.edit("**Syntax:** `.sleep <number of seconds>`")


@register(outgoing=True, pattern="shutdown")
@errors_handler
async def killdabot(event):
    # For .shutdown command, shut the bot down
    await event.edit("`Goodbye…`")

    if randint(0, 4) == 1 and not event.chat.default_banned_rights.send_media:
        try:
            await event.reply(file="userbot/files/xp_shutdown.mp3")
        except:
            pass # it be like that sometimes

    if BOTLOG:
        await event.client.send_message(BOTLOG_CHATID, "#SHUTDOWN\nBot shut down")

    try:
        await event.client.disconnect()
    except:
        pass # just shut up
    exit(0)


@register(outgoing=True, pattern="restart")
@errors_handler
async def restartdabot(event):
    await event.edit("`Restarting bot…`")
    if BOTLOG:
        await event.client.send_message(BOTLOG_CHATID, "#RESTART\nBot restarted")
    await event.client.disconnect()
    # Spin a new instance of bot
    execl(sys.executable, sys.executable, *sys.argv)
    # Shut the existing one down
    exit()


@register(outgoing=True, pattern="support")
@errors_handler
async def bot_support(event):
    # For .support command, just returns the group link
    await event.edit("Link Portal: @userbot_support")


@register(outgoing=True, pattern="repo")
@errors_handler
async def repo_is_here(event):
    # For .repo command, just returns the repo URL
    await event.edit("https://github.com/RaphielGang/Telegram-UserBot/")


CMD_HELP.update({
    "random":
    ".random <item1> <item2> … <itemN>"
    "\nUsage: Get a random item from the list of items."
})
CMD_HELP.update({
    "sleep":
    ".sleep <number of seconds>"
    "\nUsage: Userbots get tired too. Let yours snooze for a few seconds."
})
CMD_HELP.update({
    "shutdown":
    ".shutdown"
    "\nUsage: Sometimes you need to restart your bot. Sometimes you just hope to"
    "hear Windows XP shutting down…"
})
CMD_HELP.update({
    "support":
    ".support"
    "\nUsage: If you need help, use this command."
})
CMD_HELP.update({
    "repo":
    ".repo"
    "\nUsage: If you are curious what makes Paperplane work, this is what you need."
})
