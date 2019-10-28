# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#
""" Userbot initialization. """

import os
import re
from distutils.util import strtobool as sb
from logging import DEBUG, INFO, basicConfig, getLogger
from sys import executable, version_info

import pylast
from dotenv import load_dotenv
from requests import get
from telethon import TelegramClient
from telethon.network.connection.tcpabridged import ConnectionTcpAbridged

getstr = lambda varname, default: os.environ.get(varname, default)
getbool = lambda varname, default: sb(os.environ.get(varname, default))
getint = lambda varname, default: int(os.environ.get(varname, default))

load_dotenv("config.env")

# Telegram client key/hash
API_KEY = getstr("API_KEY", None)
API_HASH = getstr("API_HASH", None)

# Modules to not load upon startup
DONT_LOAD = getstr("DONT_LOAD", "").split(sep=" ")

# Name of the session file to use
SESSION_NAME = getstr("SESSION_NAME", "userbot")

# Command prefix
CMDPREFIX = re.escape(getstr("CMDPREFIX", "."))

# Bot logging setup
CONSOLE_LOGGER_VERBOSE = getbool("CONSOLE_LOGGER_VERBOSE", "False")
BOTLOG_CHATID = getstr("BOTLOG_CHATID", None)
BOTLOG = getbool("BOTLOG", "False")

basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=DEBUG if CONSOLE_LOGGER_VERBOSE else INFO
)

LOGS = getLogger(__name__)

if version_info[0] < 3 or version_info[1] < 6:
    LOGS.error(
        "You MUST have a python version of at least 3.6.0"
        "Multiple features depend on this. Bot quitting.")
    quit(1)

# Autoban PMs, mute on welcome
PM_AUTO_BAN = getbool("PM_AUTO_BAN", "False")
WELCOME_MUTE = getbool("WELCOME_MUTE", "False")

# pylint: disable=invalid-name
bot = TelegramClient(SESSION_NAME, API_KEY, API_HASH, connection=ConnectionTcpAbridged)

# Global Variables
COUNT_MSG = 0
USERS = {}
COUNT_PM = {}
LASTMSG = {}
ENABLE_KILLME = True
CMD_HELP = {}
