# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#

# This module updates the userbot based on Upstream revision

from git import Repo
from git.exc import (
    NoSuchPathError,
    GitCommandError,
    InvalidGitRepositoryError,
    CheckoutError
)

import sys, os, gc
from os import remove, execl, path
from userbot import CMD_HELP, CMDPREFIX, LOGS, BASEDIR
from userbot.events import register, errors_handler

upstream_repo = 'https://github.com/Nick80835/Telegram-UserBot.git'
valid_branch = 'staging-nodb'


@register(outgoing=True, pattern=f"^{CMDPREFIX}update(?: |$)(.*)")
@errors_handler
async def upstream(ups):
    # For the update command, checkout the latest revision on the remote
    await ups.edit("`Checking for updates, please wait...`")

    try:
        txt = "`Oops.. Updater cannot continue due to "
        txt += "some problems occured`\n\n**LOGTRACE:**\n"
        repo = Repo()
    except NoSuchPathError as error:
        await ups.edit(f'{txt}\n`directory {error} is not found`')
        return
    except InvalidGitRepositoryError as error:
        await ups.edit(f'{txt}\n`directory {error} does \
                        not seems to be a git repository`')
        return
    except GitCommandError as error:
        await ups.edit(f'{txt}\n`Early failure! {error}`')
        return

    try: # Ensure the upstream remote exists
        repo.create_remote('upstream', upstream_repo)
    except: # Don't cause an uproar if it already exists
        pass

    upstream_remote = repo.remote('upstream')

    try: # Fetch the remote repository for updates
        upstream_remote.fetch()
    except: # Notify the user of a fetching error and bail
        await ups.edit('`Failed to check for updates. :(`')
        return
    
    try: # Checkout the remote branch locally
        upstream_remote.refs['staging-nodb'].checkout()
    except CheckoutError: # Notify the user of a checkout error and bail
        await ups.edit('`Failed to checkout the updated branch due to local changes. :(`')
        return
    except: # In the case of any other random error, notify the user and bail
        await ups.edit('`Failed to update due to an unknown error. :(`')
        return

    await ups.edit('`Successfully checked out latest bot revision!\n'
                    'The bot will not pass go, will not collect $200, and will not automatically restart...`')

    try:
        await ups.client.disconnect()
    except:
        pass # we dont care
    
    gc.collect()


CMD_HELP.update({
    'update':
    '.update'
    '\nUsage: Check if the main userbot repository has any'
    'updates and checkout the latest revision.'
})
