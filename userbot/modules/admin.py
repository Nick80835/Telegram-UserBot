# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
"""
Userbot module to help you manage a group
"""

from asyncio import sleep
from telethon.errors import (BadRequestError, ChatAdminRequiredError,
                             ImageProcessFailedError, PhotoCropSizeSmallError,
                             UserAdminInvalidError)
from telethon.errors.rpcerrorlist import UserIdInvalidError
from telethon.tl.functions.channels import (EditAdminRequest,
                                            EditBannedRequest,
                                            EditPhotoRequest)
from telethon.tl.functions.messages import UpdatePinnedMessageRequest
from telethon.tl.types import (ChannelParticipantsAdmins, ChatAdminRights,
                               ChatBannedRights, MessageEntityMentionName,
                               MessageMediaPhoto)
from userbot import CMD_HELP, BOTLOG, BOTLOG_CHATID, bot, CMDPREFIX
from userbot.events import register, errors_handler

# =================== CONSTANT ===================
NO_ADMIN = "`You aren't an admin!`"
NO_PERM = "`You don't have sufficient permissions!`"

CHAT_PP_CHANGED = "`Chat Picture Changed`"
CHAT_PP_ERROR = "`Some issue with updating the pic,`" \
                "`maybe you aren't an admin,`" \
                "`or don't have the desired rights.`"
INVALID_MEDIA = "`Invalid Extension`"

banRights = ChatBannedRights(
    until_date=None,
    view_messages=True,
    send_messages=True,
    send_media=True,
    send_stickers=True,
    send_gifs=True,
    send_games=True,
    send_inline=True,
    embed_links=True,
)

unBanRights = ChatBannedRights(
    until_date=None,
    view_messages=None,
    send_messages=None,
    send_media=None,
    send_stickers=None,
    send_gifs=None,
    send_games=None,
    send_inline=None,
    embed_links=None,
)

adminRights = ChatAdminRights(
    add_admins=True,
    invite_users=True,
    change_info=True,
    ban_users=True,
    delete_messages=True,
    pin_messages=True
)

unAdminRights = ChatAdminRights(
    add_admins=None,
    invite_users=None,
    change_info=None,
    ban_users=None,
    delete_messages=None,
    pin_messages=None
)

kickRights = ChatBannedRights(until_date=None, view_messages=True)
muteRights = ChatBannedRights(until_date=None, send_messages=True)
unMuteRights = ChatBannedRights(until_date=None, send_messages=False)

# ================================================


@register(outgoing=True, pattern="promote")
@errors_handler
async def promote(event):
    # For .promote command, promote targeted person
    # Get targeted chat
    chat = await event.get_chat()
    # Grab admin status or creator in a chat
    admin = chat.admin_rights
    creator = chat.creator

    # If not admin and not creator, also return
    if not admin and not creator:
        await event.edit(NO_ADMIN)
        return

    await event.edit("`Promoting…`")

    user = await get_user_from_event(event)
    if user:
        pass
    else:
        return

    # Try to promote if current user is admin or creator
    try:
        await event.client(EditAdminRequest(event.chat_id, user.id, adminRights, None))
        await event.edit("`Promoted Successfully!`")

    # If Telethon spit BadRequestError, assume
    # we don't have Promote permission
    except BadRequestError:
        await event.edit(NO_PERM)
        return

    # Announce to the logging group if we have promoted successfully
    if BOTLOG:
        await event.client.send_message(
            BOTLOG_CHATID, "#PROMOTE\n"
            f"USER: [{user.first_name}](tg://user?id={user.id})\n"
            f"CHAT: {event.chat.title}(`{event.chat_id}`)")


@register(outgoing=True, pattern="demote")
@errors_handler
async def demote(event):
    # For .demote command, demote targeted person
    # Admin right check
    chat = await event.get_chat()
    admin = chat.admin_rights
    creator = chat.creator

    if not admin and not creator:
        await event.edit(NO_ADMIN)
        return

    # If passing, declare that we're going to demote
    await event.edit("`Demoting…`")

    user = await get_user_from_event(event)
    if user:
        pass
    else:
        return

    # Edit Admin Permission
    try:
        await event.client(EditAdminRequest(event.chat_id, user.id, unAdminRights, None))
        await event.edit("`Demoted Successfully!`")

    # If we catch BadRequestError from Telethon
    # Assume we don't have permission to demote
    except BadRequestError:
        await event.edit(NO_PERM)
        return

    # Announce to the logging group if we have demoted successfully
    if BOTLOG:
        await event.client.send_message(
            BOTLOG_CHATID, "#DEMOTE\n"
            f"USER: [{user.first_name}](tg://user?id={user.id})\n"
            f"CHAT: {event.chat.title}(`{event.chat_id}`)")


@register(outgoing=True, pattern="ban")
@errors_handler
async def ban(event):
    # For .ban command, ban targeted person
    # Here laying the sanity check
    chat = await event.get_chat()
    admin = chat.admin_rights
    creator = chat.creator

    # Well
    if not admin and not creator:
        await event.edit(NO_ADMIN)
        return

    user = await get_user_from_event(event)
    if user:
        pass
    else:
        return

    # Announce that we're going to whack the pest
    await event.edit("`Whacking the pest!`")

    try:
        await event.client(
            EditBannedRequest(event.chat_id, user.id, banRights))
    except BadRequestError:
        await event.edit(NO_PERM)
        return
    # Helps ban group join spammers more easily
    try:
        reply = await event.get_reply_message()
        if reply:
            await reply.delete()
    except BadRequestError:
        bmsg = "`I dont have enough rights! But still he was banned!`"
        await event.edit(bmsg)
        return
    # Delete message and then tell that the command
    # is done gracefully
    # Shout out the ID, so that fedadmins can fban later

    await event.edit("`{}` was banned!".format(str(user.id)))

    # Announce to the logging group if we have demoted successfully
    if BOTLOG:
        await event.client.send_message(
            BOTLOG_CHATID, "#BAN\n"
            f"USER: [{user.first_name}](tg://user?id={user.id})\n"
            f"CHAT: {event.chat.title}(`{event.chat_id}`)")


@register(outgoing=True, pattern="unban")
@errors_handler
async def unban(event):
    # For .unban command, unban targeted person
    # Here laying the sanity check
    chat = await event.get_chat()
    admin = chat.admin_rights
    creator = chat.creator

    # Well
    if not admin and not creator:
        await event.edit(NO_ADMIN)
        return

    # If everything goes well...
    await event.edit("`Unbanning…`")

    user = await get_user_from_event(event)
    if user:
        pass
    else:
        return

    try:
        await event.client(
            EditBannedRequest(event.chat_id, user.id, unBanRights))
        await event.edit("`Unbanned Successfully!`")

        if BOTLOG:
            await event.client.send_message(
                BOTLOG_CHATID, "#UNBAN\n"
                f"USER: [{user.first_name}](tg://user?id={user.id})\n"
                f"CHAT: {event.chat.title}(`{event.chat_id}`)")
    except UserIdInvalidError:
        await event.edit("`Uh oh my unban logic broke!`")


@register(outgoing=True, pattern="delusers")
@errors_handler
async def remove_deleted_accounts(event):
    # For .delusers command, remove deleted accounts from chat
    con = event.pattern_match.group(1)
    del_u = 0
    del_status = "`No deleted accounts found, Group is cleaned as Hell`"

    if not event.is_group:
        await event.edit("`This command is only for groups!`")
        return

    if con != "clean":
        await event.edit("`Searching for zombie accounts…`")
        async for user in event.client.iter_participants(event.chat_id):
            if user.deleted:
                del_u += 1

        if del_u > 0:
            del_status = f"found **{del_u}** \
                deleted account(s) in this group \
            \nclean them by using .delusers clean"

        await event.edit(del_status)
        return

    # Here laying the sanity check
    chat = await event.get_chat()
    admin = chat.admin_rights
    creator = chat.creator

    # Well
    if not admin and not creator:
        await event.edit("`You aren't an admin here!`")
        return

    await event.edit("`Cleaning deleted accounts…`")
    del_u = 0
    del_a = 0

    async for user in event.client.iter_participants(event.chat_id):
        if user.deleted:
            try:
                await event.client(EditBannedRequest(event.chat_id, user.id, banRights))
            except ChatAdminRequiredError:
                await event.edit("`You don't have enough rights.`")
                return
            except UserAdminInvalidError:
                del_u -= 1
                del_a += 1
            await event.client(
                EditBannedRequest(event.chat_id, user.id, unBanRights))
            del_u += 1

    if del_u > 0:
        del_status = f"cleaned **{del_u}** deleted account(s)"

    if del_a > 0:
        del_status = f"cleaned **{del_u}** deleted account(s) \
\n**{del_a}** deleted admin accounts are not removed"

    await event.edit(del_status)


@register(outgoing=True, pattern="adminlist")
@errors_handler
async def list_admins(event):
    # For .adminlist command, list all of the admins of the chat
    if not event.is_group:
        await event.edit("Are you sure this is a group?")
        return
    info = await event.client.get_entity(event.chat_id)
    title = info.title if info.title else "this chat"
    mentions = f'<b>Admins in {title}:</b> \n'
    try:
        async for user in event.client.iter_participants(
                event.chat_id, filter=ChannelParticipantsAdmins):
            if not user.deleted:
                link_unf = "<a href=\"tg://user?id={}\">{}</a>"
                link = link_unf.format(user.id, user.first_name)
                userid = f"<code>{user.id}</code>"
                mentions += f"\n{link} {userid}"
            else:
                mentions += f"\nDeleted Account <code>{user.id}</code>"
    except ChatAdminRequiredError as err:
        mentions += " " + str(err) + "\n"
    await event.edit(mentions, parse_mode="html")


@register(outgoing=True, pattern="pin")
@errors_handler
async def pin(event):
    # for .pin command, pin a message in the chat
    # Admin or creator check
    chat = await event.get_chat()
    admin = chat.admin_rights
    creator = chat.creator

    # If not admin and not creator, return
    if not admin and not creator:
        await event.edit(NO_ADMIN)
        return

    to_pin = event.reply_to_msg_id

    if not to_pin:
        await event.edit("`Reply to a message which you want to pin.`")
        return

    options = event.pattern_match.group(1)

    is_silent = True

    if options.lower() == "loud":
        is_silent = False

    try:
        await event.client(UpdatePinnedMessageRequest(event.to_id, to_pin, is_silent))
    except BadRequestError:
        await event.edit(NO_PERM)
        return

    await event.edit("`Pinned Successfully!`")

    user = await get_user_from_id(event.from_id, event)

    if BOTLOG:
        await event.client.send_message(
            BOTLOG_CHATID, "#PIN\n"
            f"ADMIN: [{user.first_name}](tg://user?id={user.id})\n"
            f"CHAT: {event.chat.title}(`{event.chat_id}`)\n"
            f"LOUD: {not is_silent}")


@register(outgoing=True, pattern="kick")
@errors_handler
async def kick(event):
    # For .kick command, kick someone from the chat
    # Admin or creator check
    chat = await event.get_chat()
    admin = chat.admin_rights
    creator = chat.creator

    # If not admin and not creator, return
    if not admin and not creator:
        await event.edit(NO_ADMIN)
        return

    user = await get_user_from_event(event)
    if not user:
        await event.edit("`Couldn't fetch user.`")
        return

    await event.edit("`Kicking…`")

    try:
        await event.client(
            EditBannedRequest(event.chat_id, user.id, kickRights))
        await sleep(.5)
    except BadRequestError:
        await event.edit(NO_PERM)
        return
    await event.client(EditBannedRequest(event.chat_id, user.id, ChatBannedRights(until_date=None)))

    kmsg = "`Kicked` [{}](tg://user?id={})`!`"
    await event.edit(kmsg.format(user.first_name, user.id))

    if BOTLOG:
        await event.client.send_message(
            BOTLOG_CHATID, "#KICK\n"
            f"USER: [{user.first_name}](tg://user?id={user.id})\n"
            f"CHAT: {event.chat.title}(`{event.chat_id}`)\n")


async def get_user_from_event(event):
    # Get the user from argument or replied message
    if event.reply_to_msg_id:
        previous_message = await event.get_reply_message()
        user_obj = await event.client.get_entity(previous_message.from_id)
    else:
        user = event.pattern_match.group(1)

        if user.isnumeric():
            user = int(user)

        if not user:
            await event.edit("`Pass the user's username, id or reply!`")
            return

        if event.message.entities is not None:
            probable_user_mention_entity = event.message.entities[0]

            if isinstance(probable_user_mention_entity,
                          MessageEntityMentionName):
                user_id = probable_user_mention_entity.user_id
                user_obj = await event.client.get_entity(user_id)
                return user_obj
        try:
            user_obj = await event.client.get_entity(user)
        except (TypeError, ValueError) as err:
            await event.edit(str(err))
            return None

    return user_obj


async def get_user_from_id(user, event):
    if isinstance(user, str):
        user = int(user)

    try:
        user_obj = await event.client.get_entity(user)
    except (TypeError, ValueError) as err:
        await event.edit(str(err))
        return None

    return user_obj


CMD_HELP.update({
    "promote":
    "Usage: Reply to message with .promote to promote them."
})
CMD_HELP.update({
    "demote":
    "Usage: Reply to message with .demote to revoke their admin permissions."
})
CMD_HELP.update({
    "ban":
    "Usage: Reply to message with .ban to ban them."
})
CMD_HELP.update({
    "unban":
    "Usage: Reply to message with .unban to unban them in this chat."
})
CMD_HELP.update({
    "delusers":
    "Usage: Searches for deleted accounts in a group."
})
CMD_HELP.update({
    "delusers clean":
    "Usage: Searches for and removes deleted accounts from the group."
})
CMD_HELP.update({
    "adminlist":
    "Usage: Retrieves all admins in the chat."
})
