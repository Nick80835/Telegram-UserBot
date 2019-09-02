# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#
""" Userbot initialization. """

import os, pylast, re
from distutils.util import strtobool as sb
from dotenv import load_dotenv
from logging import basicConfig, getLogger, INFO, DEBUG
from requests import get
from sys import version_info, executable
from telethon import TelegramClient

getstr = lambda varname, default: os.environ.get(varname, default)
getbool = lambda varname, default: sb(os.environ.get(varname, default))
getint = lambda varname, default: int(os.environ.get(varname, default))

try: BASEDIR
except: BASEDIR = os.getcwd()

load_dotenv("config.env")

# Telegram client key/hash
API_KEY = getstr("API_KEY", None)
API_HASH = getstr("API_HASH", None)

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

# Misc fancy integrations
SCREENSHOT_LAYER_ACCESS_KEY = getstr("SCREENSHOT_LAYER_ACCESS_KEY", None)
OPEN_WEATHER_MAP_APPID = getstr("OPEN_WEATHER_MAP_APPID", None)
YOUTUBE_API_KEY = getstr("YOUTUBE_API_KEY", None)
SPOTIFY_USERNAME = getstr("SPOTIFY_USERNAME", None)
SPOTIFY_PASS = getstr("SPOTIFY_PASS", None)
BIO_PREFIX = getstr("BIO_PREFIX", None)
DEFAULT_BIO = getstr("DEFAULT_BIO", None)
CURRENCY_API = getstr("CURRENCY_API", None)
GDRIVE_FOLDER = getstr("GDRIVE_FOLDER", None)

# LastFM integration variables
LASTFM_API = getstr("LASTFM_API", None)
LASTFM_SECRET = getstr("LASTFM_SECRET", None)
LASTFM_USERNAME = getstr("LASTFM_USERNAME", None)
LASTFM_PASSWORD_PLAIN = getstr("LASTFM_PASSWORD", None)
LASTFM_PASS = pylast.md5(LASTFM_PASSWORD_PLAIN)

if LASTFM_USERNAME != 'None':
    lastfm = pylast.LastFMNetwork(
        api_key=LASTFM_API,
        api_secret=LASTFM_SECRET,
        username=LASTFM_USERNAME,
        password_hash=LASTFM_PASS
    )
else:
    lastfm = None

if os.path.exists("learning-data-root.check"):
    os.remove("learning-data-root.check")
else:
    LOGS.info("Braincheck file does not exist, fetching...")

URL = 'https://raw.githubusercontent.com/RaphielGang/'
URL += 'databasescape/master/learning-data-root.check'

with open('learning-data-root.check', 'wb') as load:
    load.write(get(URL).content)

# pylint: disable=invalid-name
bot = TelegramClient("userbot", API_KEY, API_HASH)

# Global Variables
COUNT_MSG = 0
BRAIN_CHECKER = []
USERS = {}
COUNT_PM = {}
LASTMSG = {}
ENABLE_KILLME = True
CMD_HELP = {}
AFKREASON = "no reason"

# Zalgo characters
ZALG_LIST = [
    [
        "̖"," ̗"," ̘"," ̙"," ̜"," ̝"," ̞"," ̟"," ̠"," ̤"," ̥"," ̦",
        " ̩"," ̪"," ̫"," ̬"," ̭"," ̮"," ̯"," ̰"," ̱"," ̲"," ̳"," ̹",
        " ̺"," ̻"," ̼"," ͅ"," ͇"," ͈"," ͉"," ͍"," ͎"," ͓"," ͔"," ͕",
        " ͖"," ͙"," ͚"," ",
    ],
    [
        " ̍"," ̎"," ̄"," ̅"," ̿"," ̑"," ̆"," ̐"," ͒"," ͗"," ͑"," ̇",
        " ̈"," ̊"," ͂"," ̓"," ̈́"," ͊"," ͋"," ͌"," ̃"," ̂"," ̌"," ͐",
        " ́"," ̋"," ̏"," ̽"," ̉"," ͣ"," ͤ"," ͥ"," ͦ"," ͧ"," ͨ"," ͩ",
        " ͪ"," ͫ"," ͬ"," ͭ"," ͮ"," ͯ"," ̾"," ͛"," ͆"," ̚",
    ],
    [
        " ̕"," ̛"," ̀"," ́"," ͘"," ̡"," ̢"," ̧"," ̨"," ̴"," ̵"," ̶",
        " ͜"," ͝"," ͞"," ͟"," ͠"," ͢"," ̸"," ̷"," ͡",
    ]
]
