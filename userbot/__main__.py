# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#
""" Userbot start point """

from importlib import import_module, reload
from sys import argv

from telethon.errors.rpcerrorlist import PhoneNumberInvalidError

from userbot import LOGS, bot
from userbot.events import errors_handler, register
from userbot.modules import ALL_MODULES

INVALID_PH = '\nERROR: The Phone No. entered is INVALID' \
             '\n  Tip: Use Country Code along with No.' \
             '\n       Recheck your Phone Number'

LOADED_MODULES = []

try:
    bot.start()
except PhoneNumberInvalidError:
    print(INVALID_PH)
    exit(1)

for module_name in ALL_MODULES:
    LOADED_MODULES.append(import_module("userbot.modules." + module_name))


@register(outgoing=True, pattern="reload")
@errors_handler
async def reloadmodules(event):
    for callback, _ in event.client.list_event_handlers():
        if id(callback) != id(reloadmodules):
            event.client.remove_event_handler(callback)

    errors = ""

    for module in LOADED_MODULES:
        try:
            reload(module)
        except Exception as exception:
            errors += f"`Error while reloading {module.__name__} -> {exception}\n\n`"

    if errors:
        await event.edit(errors)
    else:
        await event.delete()


LOGS.info("Your Bot is alive! Test it by typing .alive on any chat."
          " Should you need assistance, head to https://t.me/userbot_support")
LOGS.info("Your Bot Version is 4.0")

if len(argv) not in (1, 3, 4):
    bot.disconnect()
else:
    bot.run_until_disconnected()
