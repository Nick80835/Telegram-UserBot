# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#
""" Userbot module for getting information about the server. """

from asyncio import create_subprocess_shell as asyncrunapp
from asyncio.subprocess import PIPE as asyncPIPE
from os import remove
from platform import python_version, uname
from shutil import which
from telethon import version
from userbot import CMD_HELP, CMDPREFIX
from userbot.events import register, errors_handler

# ================= CONSTANT =================
DEFAULTUSER = uname().node
# ============================================


@register(outgoing=True, pattern="sysd")
@errors_handler
async def sysdetails(event):
    # For .sysd command, get system info using neofetch
    try:
        neo = "neofetch --stdout"
        fetch = await asyncrunapp(
            neo,
            stdout=asyncPIPE,
            stderr=asyncPIPE,
        )

        stdout, stderr = await fetch.communicate()
        result = str(stdout.decode().strip()) \
            + str(stderr.decode().strip())

        await event.edit("`" + result + "`")
    except FileNotFoundError:
        await event.edit("`Hella install neofetch first kthx`")


@register(outgoing=True, pattern="botver")
@errors_handler
async def bot_ver(event):
    # For .botver command, get the bot version
    if which("git") is not None:
        invokever = "git describe --all --long"
        ver = await asyncrunapp(
            invokever,
            stdout=asyncPIPE,
            stderr=asyncPIPE,
        )
        stdout, stderr = await ver.communicate()
        verout = str(stdout.decode().strip()) \
            + str(stderr.decode().strip())

        invokerev = "git rev-list --all --count"
        rev = await asyncrunapp(
            invokerev,
            stdout=asyncPIPE,
            stderr=asyncPIPE,
        )
        stdout, stderr = await rev.communicate()
        revout = str(stdout.decode().strip()) \
            + str(stderr.decode().strip())

        await event.edit("`Userbot Version: "
                            f"{verout}"
                            "` \n"
                            "`Revision: "
                            f"{revout}"
                            "` \n"
                            "`Tagged Version: r4.0`")
    else:
        await event.edit(
            "Shame that you don't have git, You're running r4.0 anyway")


@register(outgoing=True, pattern="pip")
@errors_handler
async def pipcheck(event):
    # For .pip command, do a pip search
    pipmodule = event.pattern_match.group(1)
    if pipmodule:
        await event.edit("`Searching…`")
        invokepip = f"pip3 search {pipmodule}"
        pipc = await asyncrunapp(
            invokepip,
            stdout=asyncPIPE,
            stderr=asyncPIPE,
        )

        stdout, stderr = await pipc.communicate()
        pipout = str(stdout.decode().strip()) \
            + str(stderr.decode().strip())

        if pipout:
            if len(pipout) > 4096:
                await event.edit("`Output too large, sending as file`")
                file = open("output.txt", "w+")
                file.write(pipout)
                file.close()
                await event.client.send_file(
                    event.chat_id,
                    "output.txt",
                    reply_to=event.id,
                )
                remove("output.txt")
                return
            await event.edit("**Query: **\n`"
                            f"{invokepip}"
                            "`\n**Result: **\n`"
                            f"{pipout}"
                            "`")
        else:
            await event.edit("**Query: **\n`"
                            f"{invokepip}"
                            "`\n**Result: **\n`No Result Returned/False`")
    else:
        await event.edit("`Use .help pip to see an example`")


@register(outgoing=True, pattern="alive")
@errors_handler
async def amireallyalive(event):
    await event.edit("`"
        "Your bot is running \n\n"
        f"Telethon version: {version.__version__} \n"
        f"Python: {python_version()} \n"
        f"User: {DEFAULTUSER}"
        "`")


@register(outgoing=True, pattern="aliveu")
@errors_handler
async def amireallyaliveuser(event):
    # For .aliveu command, change the username in the .alive command
    message = event.text
    output = '.aliveu [new user without brackets] nor can it be empty'
    if not (message == '.aliveu' or message[7:8] != ' '):
        newuser = message[8:]
        global DEFAULTUSER
        DEFAULTUSER = newuser
        output = 'Successfully changed user to ' + newuser + '!'
    await event.edit("`" f"{output}" "`")


@register(outgoing=True, pattern="resetalive")
@errors_handler
async def amireallyalivereset(event):
    # For .resetalive command, reset the username in the .alive command
    global DEFAULTUSER
    DEFAULTUSER = uname().node
    await event.edit("`" "Successfully reset user for alive!" "`")


CMD_HELP.update({
    "sysd":
    ".sysd"
    "\nUsage: Show system information using neofetch."
})
CMD_HELP.update({
    "botver":
    ".botver" "\nUsage: Show the userbot version."
})
CMD_HELP.update({
    "pip":
    ".pip <module(s)>"
    "\nUsage: Search module(s) in PyPi."
})
CMD_HELP.update({
    "alive":
    ".alive"
    "\nUsage: Check if your bot is working or not. "
    "Use .aliveu <new_user> to change user name, or .resetalive "
    "to reset it to default."
})
