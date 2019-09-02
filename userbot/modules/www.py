# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#
""" Userbot module containing commands related to the \
    Information Superhighway(yes, Internet). """

from speedtest import Speedtest
from datetime import datetime
from telethon import functions
from userbot import CMD_HELP, CMDPREFIX
from userbot.events import register, errors_handler


@register(outgoing=True, pattern=f"^{CMDPREFIX}speed$")
@errors_handler
async def speedtst(event):
    # For the speed command, use SpeedTest to check server speeds.
    await event.edit("`Running speed test...`")
    test = Speedtest()

    test.get_best_server()
    test.download()
    test.upload()
    test.results.share()
    result = test.results.dict()

    await event.edit(
        f"`Started at: {result['timestamp']}\n\n"
        f"Download: {speed_convert(result['download'])}\n"
        f"Upload: {speed_convert(result['upload'])}\n"
        f"Ping: {result['ping']}ms\n"
        f"ISP: {result['client']['isp']}`"
    )


def speed_convert(size):
    # Hi human, you can't read bytes?
    power = 2**10
    zero = 0
    units = {0: '', 1: 'Kb/s', 2: 'Mb/s', 3: 'Gb/s', 4: 'Tb/s'}
    while size > power:
        size /= power
        zero += 1
    return f"{round(size, 2)} {units[zero]}"


@register(outgoing=True, pattern=f"^{CMDPREFIX}nearestdc$")
@errors_handler
async def neardc(event):
    # For the nearestdc command, get the nearest datacenter information.
    result = await event.client(functions.help.GetNearestDcRequest())

    await event.edit(
        f"`Country: {result.country}\n"
        f"Nearest Datacenter: {result.nearest_dc}\n"
        f"This Datacenter: {result.this_dc}`"
    )


@register(outgoing=True, pattern=f"^{CMDPREFIX}ping$")
@errors_handler
async def pingme(event):
    # For the pingme command, ping the userbot from any chat.
    start = datetime.now()
    await event.edit("`Pong!`")
    end = datetime.now()
    duration = (end - start).microseconds / 1000
    await event.edit(f"`Pong! {duration}ms`")


CMD_HELP.update(
    {"speed":
    ".speed\n"
    "Usage: Conduct a speedtest and show the results."
})

CMD_HELP.update({
    "nearestdc":
    ".nearestdc\n"
    "Usage: Find the nearest datacenter from your server."
})

CMD_HELP.update(
    {"ping":
    ".ping\n"
    "Usage: Show how long it takes to ping your bot."})
