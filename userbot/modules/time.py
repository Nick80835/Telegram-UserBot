# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#
""" Userbot module for getting the date
    and time of any country or the userbot server.  """

from datetime import datetime as dt
from pytz import country_names as c_n
from pytz import country_timezones as c_tz
from pytz import timezone as tz
from userbot import CMD_HELP, CMDPREFIX
from userbot.events import register, errors_handler

# ===== CONSTANT =====
INV_CON = "`Invalid country.`"
TZ_NOT_FOUND = "`The selected timezone is not found! Try again!`"
DB_FAILED = "`Database connections failed!`"


# ===== CONSTANT =====
async def get_tz(con):
    # Get time zone of the given country
    if "(Uk)" in con:
        con = con.replace("Uk", "UK")
    if "(Us)" in con:
        con = con.replace("Us", "US")
    if " Of " in con:
        con = con.replace(" Of ", " of ")
    if "(Western)" in con:
        con = con.replace("(Western)", "(western)")
    if "Minor Outlying Islands" in con:
        con = con.replace("Minor Outlying Islands", "minor outlying islands")
    if "Nl" in con:
        con = con.replace("Nl", "NL")

    for c_code in c_n:
        if con == c_n[c_code]:
            return c_tz[c_code]
    try:
        if c_n[con]:
            return c_tz[con]
    except KeyError:
        return


@register(outgoing=True, pattern="time")
@errors_handler
async def time_func(event):
    # For .time command, return the time of
    # 1. The country passed as an argument,
    # 2. The default userbot country(set it by using .settime),
    # 3. The server where the userbot runs.
    con = event.pattern_match.group(1).title()
    tz_num = event.pattern_match.group(2)

    t_form = "%H:%M"

    if con:
        try:
            c_name = c_n[con]
        except KeyError:
            c_name = con

        timezones = await get_tz(con)
    else:
        await event.edit(
            f"`It's`  **{dt.now().strftime(t_form)}**  `here.`")
        return

    if not timezones:
        await event.edit(INV_CON)
        return

    if len(timezones) == 1:
        time_zone = timezones[0]
    elif len(timezones) > 1:
        if tz_num:
            tz_num = int(tz_num)
            if len(timezones) >= tz_num:
                time_zone = timezones[tz_num - 1]
            else:
                await event.edit(TZ_NOT_FOUND)
                return
        else:
            return_str = f"{c_name} has multiple timezones:\n"

            for i, item in enumerate(timezones):
                return_str += f"{i+1}. {item}\n"

            return_str += "Choose one by typing the number "
            return_str += "in the command. Example:\n"
            return_str += f".time {c_name} 2"

            await event.edit(return_str)
            return

    dtnow = dt.now(tz(time_zone)).strftime(t_form)

    await event.edit(
        f"`It's`  **{dtnow}**  `in {c_name}({time_zone} timezone).`")


@register(outgoing=True, pattern="date")
@errors_handler
async def date_func(event):
    # For .date command, return the date of
    # 1. The country passed as an argument,
    # 2. The default userbot country(set it by using .settime),
    # 3. The server where the userbot runs.
    con = event.pattern_match.group(1).title()
    tz_num = event.pattern_match.group(2)

    d_form = "%d/%m/%y - %A"

    if con:
        try:
            c_name = c_n[con]
        except KeyError:
            c_name = con

        timezones = await get_tz(con)
    else:
        await event.edit(f"`It's`  **{dt.now().strftime(d_form)}**  `here.`")
        return

    if not timezones:
        await event.edit(INV_CON)
        return

    if len(timezones) == 1:
        time_zone = timezones[0]
    elif len(timezones) > 1:
        if tz_num:
            tz_num = int(tz_num)
            if len(timezones) >= tz_num:
                time_zone = timezones[tz_num - 1]
            else:
                await event.edit(TZ_NOT_FOUND)
                return
        else:
            return_str = f"{c_name} has multiple timezones:\n"

            for i, item in enumerate(timezones):
                return_str += f"{i+1}. {item}\n"

            return_str += "Choose one by typing the number "
            return_str += "in the command. Example:\n"
            return_str += f".date {c_name} 2"

            await event.edit(return_str)
            return

    dtnow = dt.now(tz(time_zone)).strftime(d_form)

    await event.edit(
        f"`It's`  **{dtnow}**  `in {c_name}({time_zone} timezone).`")


CMD_HELP.update({
    "time":
    ".time <country name/code> <timezone number>"
    "\nUsage: Get the time of a country. If a country has "
    "multiple timezones, Paperplane will list all of them "
    "and let you select one."
})
CMD_HELP.update({
    "date":
    ".date <country name/code> <timezone number>"
    "\nUsage: Get the date of a country. If a country has "
    "multiple timezones, Paperplane will list all of them "
    "and let you select one."
})
