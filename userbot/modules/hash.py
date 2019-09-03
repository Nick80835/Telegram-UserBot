# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#
""" Userbot module containing hash and encode/decode commands. """

import pybase64
from subprocess import PIPE, run as runapp
from userbot import CMD_HELP, CMDPREFIX
from userbot.events import register, errors_handler


@register(outgoing=True, pattern=f"^{CMDPREFIX}hash (.*)")
@errors_handler
async def gethash(event):
    # For .hash command, find the md5,
    # sha1, sha256 and sha512 of the string.
    hashtxt_ = event.pattern_match.group(1)
    hashtxt = open("hashdis.txt", "w+")
    hashtxt.write(hashtxt_)
    hashtxt.close()
    md5 = runapp(["md5sum", "hashdis.txt"], stdout=PIPE)
    md5 = md5.stdout.decode()
    sha1 = runapp(["sha1sum", "hashdis.txt"], stdout=PIPE)
    sha1 = sha1.stdout.decode()
    sha256 = runapp(["sha256sum", "hashdis.txt"], stdout=PIPE)
    sha256 = sha256.stdout.decode()
    sha512 = runapp(["sha512sum", "hashdis.txt"], stdout=PIPE)
    runapp(["rm", "hashdis.txt"], stdout=PIPE)
    sha512 = sha512.stdout.decode()
    ans = ("Text: `" + hashtxt_ + "`\nMD5: `" + md5 + "`SHA1: `" + sha1 +
            "`SHA256: `" + sha256 + "`SHA512: `" + sha512[:-1] + "`")
    if len(ans) > 4096:
        hashfile = open("hashes.txt", "w+")
        hashfile.write(ans)
        hashfile.close()
        await event.client.send_file(
            event.chat_id,
            "hashes.txt",
            reply_to=event.id,
            caption="`It's too big, sending a text file instead. `")
        runapp(["rm", "hashes.txt"], stdout=PIPE)
    else:
        await event.reply(ans)


@register(outgoing=True, pattern=f"^{CMDPREFIX}base64 (en|de) (.*)")
@errors_handler
async def endecrypt(event):
    # For .base64 command, find the base64 encoding of the given string.
    if event.pattern_match.group(1) == "en":
        lething = str(
            pybase64.b64encode(bytes(event.pattern_match.group(2),
                                        "utf-8")))[2:]
        await event.reply("Encoded: `" + lething[:-1] + "`")
    else:
        lething = str(
            pybase64.b64decode(bytes(event.pattern_match.group(2),
                                        "utf-8"),
                                validate=True))[2:]
        await event.reply("Decoded: `" + lething[:-1] + "`")


CMD_HELP.update({
    "base64":
    "Find the base64 encoding of the given string"
})
CMD_HELP.update({
    "hash":
    "Find the md5, sha1, sha256 and sha512 of the string when written into a txt file."
})
