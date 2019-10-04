# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#

# This module updates the userbot based on Upstream revision

import sys, os, gc
from git import Repo
from git.exc import (
    NoSuchPathError,
    GitCommandError,
    InvalidGitRepositoryError,
    CheckoutError
)
from os import remove, execl, path
from userbot import CMD_HELP, CMDPREFIX, LOGS
from userbot.events import register, errors_handler

upstream_repo = 'https://github.com/Nick80835/Telegram-UserBot.git'
valid_branches = ['staging-nodb']
commit_date_format = "%d/%m/%y"


async def generate_changelog(local_head, local_remote_diff):
    changelog = ''

    for commit in local_head.iter_commits(local_remote_diff):
        changelog += f'•[{commit.committed_datetime.strftime(commit_date_format)}]:'
        changelog += f' {commit.summary} <{commit.author}>\n'

    return changelog


@register(outgoing=True, pattern="update")
@errors_handler
async def upstream(event):
    # For the update command, checkout the latest revision on the remote
    await event.edit("`Checking for updates, please wait…`")
    flag = event.pattern_match.group(1)

    update_error_template = "`The updater cannot continue due to an "
    update_error_template += "unexpected error! :(`\n\n**LOGTRACE:**\n"

    try:
        repo = Repo()
    except NoSuchPathError as error:
        await event.edit(f'{update_error_template}\n`Directory {error} does not exist.`')
        return
    except InvalidGitRepositoryError as error:
        await event.edit(f'{update_error_template}\n`Directory {error} is not a git repository`')
        return
    except GitCommandError as error:
        await event.edit(f'{update_error_template}\n`Git error: {error}`')
        return

    try: # Ensure the upstream remote exists
        repo.create_remote('upstream', upstream_repo)
    except: # Don't cause an uproar if it already exists
        pass

    upstream_remote = repo.remote('upstream')

    try: # Fetch the remote repository for updates
        upstream_remote.fetch()
    except: # Notify the user of a fetching error and bail
        await event.edit('`Failed to check for updates. :(`')
        return

    try:
        changelog = await generate_changelog(repo, f'HEAD..upstream/{valid_branches[0]}')
    except TypeError:
        repo.git.reset('--hard', 'FETCH_HEAD')
        await event.edit("`The local branch wasn't properly set up so it was reset to FETCH_HEAD.`")
        return
    except:
        await event.edit('`There was an error when checking for changes. :(`')
        return

    if not changelog: # No changes, say so and bail
        await event.edit('`Your bot is already the latest revision. :)`')
        return
    elif flag != 'now': # Changes found but the user didn't say update now, list changes and bail
        await event.edit('`An update is available, run` **.update now** `to update.`')
        if len(changelog) < 2048:
            await event.reply(f'**Changelog:**\n`{changelog}`')
        else:
            file = open("changelog.txt", "w+")
            file.write(changelog)
            file.close()
            await event.reply(file="changelog.txt")
            remove("changelog.txt")
        return
    else: # Changes found and the user said update now, continue
        await event.edit('`Updating to the latest revision…`')

    try: # Reset to the latest remote branch locally
        repo.git.reset('--hard', 'FETCH_HEAD')
    except CheckoutError: # Notify the user in the case of a checkout error and bail
        await event.edit('`Failed to update to the latest revision due to local changes. :(`')
        return
    except: # In the case of any other random error, notify the user and bail
        await event.edit('`Failed to update due to an unknown error. :(`')
        return

    await event.edit('`Successfully updated to latest bot revision!\n'
                    'The bot will pass go, will collect $200, and will automagically restart…`')

    try: await event.client.disconnect()
    except: pass # we dont care
    # Spin a new instance of bot
    execl(sys.executable, sys.executable, *sys.argv)
    # Shut the existing one down
    exit()


CMD_HELP.update({
    'update':
    '.update'
    '\nUsage: Check if the main userbot repository has any'
    'updates and checkout the latest revision.'
})
