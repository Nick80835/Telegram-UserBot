# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#
# You can find misc modules, which dont fit in anything xD
""" Userbot module for other small commands. """

from random import randint, choice
from time import sleep
from os import execl
import sys
from userbot import BOTLOG, BOTLOG_CHATID, CMD_HELP, CMDPREFIX
from userbot.events import register, errors_handler


@register(outgoing=True, pattern=f"^{CMDPREFIX}random(.*)")
@errors_handler
async def randomise(items):
    # For .random command, get a random item from the list of items.
    if len(items.pattern_match.group().split()) > 1:
        itemlist = items.pattern_match.group().split()[1:]
        chosenitem = choice(itemlist)
        await items.edit("**Query: **\n`" + ' '.join(itemlist) +
                            "`\n**Output: **\n`" + chosenitem + "`")
    else:
        await items.edit('`Give me a list of stuff to pick from!`')


@register(outgoing=True, pattern=f"^{CMDPREFIX}sleep(.*)")
@errors_handler
async def sleepybot(time):
    # For .sleep command, let the userbot snooze for a few second.
    if len(time.pattern_match.group().split()) > 1:
        counter = int(time.pattern_match.group().split()[1])
        await time.edit("`I'm sulking and snoozing...`")
        if BOTLOG:
            await time.client.send_message(
                BOTLOG_CHATID,
                f"You put the bot to sleep for {str(counter)} seconds",
            )
        sleep(counter)
        await time.edit("`Okay, I'm done sleeping!`")
    else:
        await time.edit("**Syntax:** `.sleep [seconds]`")


@register(outgoing=True, pattern=f"^{CMDPREFIX}shutdown$")
@errors_handler
async def killdabot(event):
    """ For .shutdown command, shut the bot down."""
    await event.edit("`Goodbye *Windows XP shutdown sound*....`")
    if BOTLOG:
        await event.client.send_message(BOTLOG_CHATID, "#SHUTDOWN \n"
                                        "Bot shut down")
    await event.client.disconnect()


@register(outgoing=True, pattern=f"^{CMDPREFIX}restart$")
@errors_handler
async def restartdabot(event):
    await event.edit("`Hold tight! I just need a second to be back up....`"
                        )
    if BOTLOG:
        await event.client.send_message(BOTLOG_CHATID, "#RESTART \n"
                                        "Bot Restarted")
    await event.client.disconnect()
    # Spin a new instance of bot
    execl(sys.executable, sys.executable, *sys.argv)
    # Shut the existing one down
    exit()


@register(outgoing=True, pattern=f"^{CMDPREFIX}support$")
@errors_handler
async def bot_support(wannahelp):
    """ For .support command, just returns the group link. """
    await wannahelp.edit("Link Portal: @userbot_support")


@register(outgoing=True, pattern=f"^{CMDPREFIX}repo$")
@errors_handler
async def repo_is_here(wannasee):
    """ For .repo command, just returns the repo URL. """
    await wannasee.edit("https://github.com/RaphielGang/Telegram-UserBot/")


CMD_HELP.update({
    'random':
    ".random <item1> <item2> ... <itemN>"
    "\nUsage: Get a random item from the list of items."
})

CMD_HELP.update({
    'sleep':
    '.sleep 10'
    '\nUsage: Userbots get tired too. Let yours snooze for a few seconds.'
})

CMD_HELP.update({
    "shutdown":
    ".shutdown"
    '\nUsage: Sometimes you need to restart your bot. Sometimes you just hope to'
    "hear Windows XP shutdown sound... but you don't."
})

CMD_HELP.update(
    {'support': ".support"
     "\nUsage: If you need help, use this command."})

CMD_HELP.update({
    'repo':
    '.repo'
    '\nUsage: If you are curious what makes Paperplane work, this is what you need.'
})
