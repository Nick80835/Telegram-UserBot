# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#
""" Userbot module for executing code and eventinal commands from Telegram. """

import asyncio
from getpass import getuser
from os import remove
from sys import executable
from userbot import CMD_HELP, BOTLOG, BOTLOG_CHATID
from userbot.events import register, errors_handler


@register(outgoing=True, pattern="eval")
@errors_handler
async def evaluate(event):
    # For .eval command, evaluates the given Python expression.
    if event.is_channel and not event.is_group:
        await event.edit("`Eval isn't permitted on channels!`")
        return

    if event.pattern_match.group(1):
        expression = event.pattern_match.group(1)
    else:
        await event.edit("`Give an expression to evaluate!`")
        return

    if expression in ("userbot.session", "config.env"):
        await event.edit("`That's a dangerous operation! Not Permitted!`")
        return

    try:
        evaluation = str(eval(expression))
        if evaluation:
            if isinstance(evaluation, str):
                if len(evaluation) >= 4096:
                    file = open("output.txt", "w+")
                    file.write(evaluation)
                    file.close()
                    await event.client.send_file(
                        event.chat_id,
                        "output.txt",
                        reply_to=event.id,
                        caption="`Output too large, sending as file…`",
                    )
                    remove("output.txt")
                    return
                await event.edit("**Query: **\n`"
                                    f"{expression}"
                                    "`\n**Result: **\n`"
                                    f"{evaluation}"
                                    "`")
        else:
            await event.edit("**Query: **\n`"
                                f"{expression}"
                                "`\n**Result: **\n`No Result Returned/False`")
    except Exception as err:
        await event.edit("**Query: **\n`"
                            f"{expression}"
                            "`\n**Exception: **\n"
                            f"`{err}`")

    if BOTLOG:
        await event.client.send_message(
            BOTLOG_CHATID,
            f"Eval query {expression} was executed successfully")


@register(outgoing=True, pattern="exec")
@errors_handler
async def run(event):
    # For .exec command, which executes the dynamically created program
    code = event.pattern_match.group(1)

    if event.is_channel and not event.is_group:
        await event.edit("`Exec isn't permitted on channels!`")
        return

    if not code:
        await event.edit("`At least a variable is required to \
execute. Use .help exec for an example.`")
        return

    if code in ("userbot.session", "config.env"):
        await event.edit("`That's a dangerous operation! Not Permitted!`")
        return

    if len(code.splitlines()) <= 5:
        codepre = code
    else:
        clines = code.splitlines()
        codepre = clines[0] + "\n" + clines[1] + "\n" + clines[2] + \
            "\n" + clines[3] + "..."

    command = "".join(f"\n {l}" for l in code.split("\n.strip()"))
    process = await asyncio.create_subprocess_exec(
        executable,
        '-c',
        command.strip(),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await process.communicate()
    result = str(stdout.decode().strip()) \
        + str(stderr.decode().strip())

    if result:
        if len(result) > 4096:
            file = open("output.txt", "w+")
            file.write(result)
            file.close()
            await event.client.send_file(
                event.chat_id,
                "output.txt",
                reply_to=event.id,
                caption="`Output too large, sending as file`",
            )
            remove("output.txt")
            return
        await event.edit("**Query: **\n`"
                            f"{codepre}"
                            "`\n**Result: **\n`"
                            f"{result}"
                            "`")
    else:
        await event.edit("**Query: **\n`"
                            f"{codepre}"
                            "`\n**Result: **\n`No Result Returned/False`")

    if BOTLOG:
        await event.client.send_message(
            BOTLOG_CHATID,
            "Exec query " + codepre + " was executed successfully")


@register(outgoing=True, pattern="term")
@errors_handler
async def terminal_runner(event):
    # For .event command, runs bash commands and scripts on your server.
    curruser = getuser()
    command = event.pattern_match.group(1)
    try:
        from os import geteuid
        uid = geteuid()
    except ImportError:
        uid = "This ain't it chief!"

    if event.is_channel and not event.is_group:
        await event.edit("`Terminal commands aren't permitted on channels!`")
        return

    if not command:
        await event.edit("`Give a command or use .help term for \
            an example.`")
        return

    if command in ("userbot.session", "config.env"):
        await event.edit("`That's a dangerous operation! Not Permitted!`")
        return

    process = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await process.communicate()
    result = str(stdout.decode().strip()) \
        + str(stderr.decode().strip())

    if len(result) > 4096:
        output = open("output.txt", "w+")
        output.write(result)
        output.close()
        await event.client.send_file(
            event.chat_id,
            "output.txt",
            reply_to=event.id,
            caption="`Output too large, sending as file`",
        )
        remove("output.txt")
        return

    if uid == 0:
        await event.edit("`" f"{curruser}:~# {command}" f"\n{result}" "`")
    else:
        await event.edit("`" f"{curruser}:~$ {command}" f"\n{result}" "`")

    if BOTLOG:
        await event.client.send_message(
            BOTLOG_CHATID,
            "Terminal Command " + command + " was executed sucessfully",
        )


CMD_HELP.update({
    "eval":
    ".eval 2 + 3\nUsage: Evalute mini-expressions."
})
CMD_HELP.update({
    "exec":
    ".exec print('hello')\nUsage: Execute small Python scripts."
})
CMD_HELP.update({
    "term":
    ".term ls\nUsage: Run terminal commands and scripts on your server."
})
