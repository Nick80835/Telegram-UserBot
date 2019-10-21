# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#
#
# Userbot module for having some fun.

import asyncio
import re
import time
from random import choice, getrandbits, randint

from cowpy import cow

from userbot import CMD_HELP
from userbot.events import errors_handler, register

METOOSTR = [
    "Me too thanks","Haha yes, me too","Same lol","Me irl",
    "Haha same","Same here","Haha yes","Yeah, same bro","Me rn",
    "I, too, exhibit this","I share this experience",
    "Indeed my good chum","Same, haha","Me three",
    "The condition you're exclaiming is one that I, too, experience as a human.",
    "Dude, like, same","Same","I feel ya","O\nM\nG\n\nSame",
    """What the fuck did you just fucking say about me, you little bitch? I'll have you know I graduated top of my class in the Navy Seals, and I've been involved in numerous secret raids on Al-Quaeda, and I have over 300 confirmed kills. I am trained in gorilla warfare and I'm the top sniper in the entire US armed forces. You are nothing to me but just another target. I will wipe you the fuck out with precision the likes of which has never been seen before on this Earth, mark my fucking words. You think you can get away with saying that shit to me over the Internet? Think again, fucker. As we speak I am contacting my secret network of spies across the USA and your IP is being traced right now so you better prepare for the storm, maggot. The storm that wipes out the pathetic little thing you call your life. You're fucking dead, kid. I can be anywhere, anytime, and I can kill you in over seven hundred ways, and that's just with my bare hands. Not only am I extensively trained in unarmed combat, but I have access to the entire arsenal of the United States Marine Corps and I will use it to its full extent to wipe your miserable ass off the face of the continent, you little shit. If only you could have known what unholy retribution your little "clever" comment was about to bring down upon you, maybe you would have held your fucking tongue. But you couldn't, you didn't, and now you're paying the price, you goddamn idiot. I will shit fury all over you and you will drown in it. You're fucking dead, kiddo.\n\n I mean.. uh.. me too."""
]

EMOJIS = [
    "😂","😂","👌","✌","💞","👍","👌","💯","🎶",
    "👀","😂","👓","👏","👐","🍕","💥","🍴","💦","💦",
    "🍑","🍆","😩","😏","👉👌","👀","👅","😩","🚰"
]

UWUS = [
    '(・`ω´・)',';;w;;','owo','UwU','>w<','^w^',r'\(^o\) (/o^)/',
    '( ^ _ ^)∠☆','(ô_ô)','~:o',';____;','(*^*)','(>_','(♥_♥)',
    '*(^O^)*','((+_+))','(づ｡◕‿‿◕｡)づ','(◕‿◕✿)','(｡◕‿‿◕｡)',
    '(｡◕‿◕｡)','(─‿‿─)','(´• ω •`)','(^◕ᴥ◕^)','(^◔ᴥ◔^)',
    '(^˵◕ω◕˵^)','( =ω=)..nyaa','( ; ω ; )'
]

FACEREACTS = [
    "ʘ‿ʘ","ヾ(-_- )ゞ","(っ˘ڡ˘ς)","(´ж｀ς)","( ಠ ʖ̯ ಠ)","(° ͜ʖ͡°)╭∩╮",
    "(ᵟຶ︵ ᵟຶ)","(งツ)ว","ʚ(•｀","(っ▀¯▀)つ","(◠﹏◠)","( ͡ಠ ʖ̯ ͡ಠ)",
    "( ఠ ͟ʖ ఠ)","(∩｀-´)⊃━☆ﾟ.*･｡ﾟ","(⊃｡•́‿•̀｡)⊃","(._.)","{•̃_•̃}",
    "(ᵔᴥᵔ)","♨_♨","⥀.⥀","ح˚௰˚づ ","(҂◡_◡)","ƪ(ړײ)‎ƪ​​","(っ•́｡•́)♪♬",
    "◖ᵔᴥᵔ◗ ♪ ♫ ","(☞ﾟヮﾟ)☞","[¬º-°]¬","(Ծ‸ Ծ)","(•̀ᴗ•́)و ̑̑","ヾ(´〇`)ﾉ♪♪♪",
    "(ง'̀-'́)ง","ლ(•́•́ლ)","ʕ •́؈•̀ ₎","♪♪ ヽ(ˇ∀ˇ )ゞ","щ（ﾟДﾟщ）","( ˇ෴ˇ )",
    "눈_눈","(๑•́ ₃ •̀๑) ","( ˘ ³˘)♥ ","ԅ(≖‿≖ԅ)","♥‿♥","◔_◔",
    "⁽⁽ଘ( ˊᵕˋ )ଓ⁾⁾","乁( ◔ ౪◔)「      ┑(￣Д ￣)┍","( ఠൠఠ )ﾉ","٩(๏_๏)۶",
    "┌(ㆆ㉨ㆆ)ʃ","ఠ_ఠ","(づ｡◕‿‿◕｡)づ","(ノಠ ∩ಠ)ノ彡( \\o°o)\\",
    "“ヽ(´▽｀)ノ”","༼ ༎ຶ ෴ ༎ຶ༽","｡ﾟ( ﾟஇ‸இﾟ)ﾟ｡","(づ￣ ³￣)づ","(⊙.☉)7",
    "ᕕ( ᐛ )ᕗ","t(-_-t)","(ಥ⌣ಥ)","ヽ༼ ಠ益ಠ ༽ﾉ","༼∵༽ ༼⍨༽ ༼⍢༽ ༼⍤༽",
    "ミ●﹏☉ミ","(⊙_◎)","¿ⓧ_ⓧﮌ","ಠ_ಠ","(´･_･`)","ᕦ(ò_óˇ)ᕤ","⊙﹏⊙",
    "(╯°□°）╯︵ ┻━┻",r"¯\_(⊙︿⊙)_/¯","٩◔̯◔۶","°‿‿°","ᕙ(⇀‸↼‶)ᕗ",
    "⊂(◉‿◉)つ","V•ᴥ•V","q(❂‿❂)p","ಥ_ಥ","ฅ^•ﻌ•^ฅ","ಥ﹏ಥ",
    "（ ^_^）o自自o（^_^ ）","ಠ‿ಠ","ヽ(´▽`)/","ᵒᴥᵒ#","( ͡° ͜ʖ ͡°)",
    "┬─┬﻿ ノ( ゜-゜ノ)","ヽ(´ー｀)ノ","☜(⌒▽⌒)☞","ε=ε=ε=┌(;*´Д`)ﾉ",
    "(╬ ಠ益ಠ)","┬─┬⃰͡ (ᵔᵕᵔ͜ )","┻━┻ ︵ヽ(`Д´)ﾉ︵﻿ ┻━┻",r"¯\_(ツ)_/¯",
    "ʕᵔᴥᵔʔ","(`･ω･´)","ʕ•ᴥ•ʔ","ლ(｀ー´ლ)","ʕʘ̅͜ʘ̅ʔ","（　ﾟДﾟ）",
    r"¯\(°_o)/¯","(｡◕‿◕｡)",
]

RUNSREACTS = [
    "Runs to Thanos",
    "Runs far, far away from earth",
    "Running faster than usian bolt coz I'mma Bot",
    "Runs to Marie",
    "This Group is too cancerous to deal with.",
    "Cya bois",
    "Kys",
    "I am a mad person. Plox Ban me.",
    "I go away",
    "I am just walking off, coz me is too fat.",
    "I Fugged off!",
]

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


@register(outgoing=True, pattern="(\w+)say")
@errors_handler
async def univsaye(event): # For .cowsay module, userbot wrapper for cow which says things.
    arg = event.pattern_match.group(1).lower()
    text = event.pattern_match.group(2)

    if arg == "cow":
        arg = "default"
    if arg not in cow.COWACTERS:
        return
    cheese = cow.get_cow(arg)
    cheese = cheese()

    await event.edit(f"`{cheese.milk(text).replace('`', '´')}`")


@register(outgoing=True, pattern="^:/$", custom_regex=True)
@errors_handler
async def kek(event): # Check yourself ;)
    uio = ["/", "\\"]
    for i in range(1, 15):
        time.sleep(0.3)
        await event.edit(":" + uio[i % 2])


@register(outgoing=True, pattern="^-_-$", custom_regex=True)
@errors_handler
async def lol(event): # Ok...
    okay = "-_-"
    for _ in range(10):
        okay = okay[:-1] + "_-"
        await event.edit(okay)


@register(outgoing=True, pattern="cp")
@errors_handler
async def copypasta(event): # Copypasta the famous meme
    textx = await event.get_reply_message()
    message = event.pattern_match.group(1)

    if message:
        pass
    elif textx:
        message = textx.text
    else:
        await event.edit("`😂🅱️IvE👐sOME👅text👅 for✌️Me👌tO👐MAkE👀iT💞funNy!💦`")
        return

    reply_text = choice(EMOJIS)
    # choose a random character in the message to be substituted with 🅱️
    b_char = choice(message).lower()
    for owo in message:
        if owo == " ":
            reply_text += choice(EMOJIS)
        elif owo in EMOJIS:
            reply_text += owo
            reply_text += choice(EMOJIS)
        elif owo.lower() == b_char:
            reply_text += "🅱️"
        else:
            if bool(getrandbits(1)):
                reply_text += owo.upper()
            else:
                reply_text += owo.lower()
    reply_text += choice(EMOJIS)
    await event.edit(reply_text)


@register(outgoing=True, pattern="vapor")
@errors_handler
async def vapor(event): # Vaporize everything!
    reply_text = list()
    textx = await event.get_reply_message()
    message = event.pattern_match.group(1)
    if message:
        pass
    elif textx:
        message = textx.text
    else:
        message = "Gimme some text to vaporize!"

    for charac in message:
        if 0x21 <= ord(charac) <= 0x7F:
            reply_text.append(chr(ord(charac) + 0xFEE0))
        elif ord(charac) == 0x20:
            reply_text.append(chr(0x3000))
        else:
            reply_text.append(charac)

    await event.edit("".join(reply_text))


@register(outgoing=True, pattern="str")
@errors_handler
async def stretch(event): # Stretch it.
    textx = await event.get_reply_message()
    message = event.text
    message = event.pattern_match.group(1)
    if message:
        pass
    elif textx:
        message = textx.text
    else:
        message = "Gib some text to stretch!"

    reply_text = re.sub(r"([aeiouAEIOUａｅｉｏｕＡＥＩＯＵаеиоуюяыэё])",
                        (r"\1" * randint(3, 10)), message)
    await event.edit(reply_text)


@register(outgoing=True, pattern="zal")
@errors_handler
async def zal(event): # Invoke the feeling of chaos.
    reply_text = list()
    textx = await event.get_reply_message()
    message = event.pattern_match.group(1)
    if message:
        pass
    elif textx:
        message = textx.text
    else:
        message = "Gimme text to zalgofy!"

    for charac in message:
        if not charac.isalpha():
            reply_text.append(charac)
            continue

        for _ in range(0, 3):
            charac = charac.strip() + \
                choice(ZALG_LIST[randint(0,2)]).strip()

        reply_text.append(charac)

    await event.edit("".join(reply_text))


@register(outgoing=True, pattern="^hi$", custom_regex=True)
@errors_handler
async def hoi(event): # Greet everyone!
    await event.edit("Hoi!😄")


@register(outgoing=True, pattern="owo")
@errors_handler
async def faces(event): # UwU
    textx = await event.get_reply_message()
    message = event.pattern_match.group(1)
    if message:
        pass
    elif textx:
        message = textx.text
    else:
        message = "I need text to curse with owo!"

    reply_text = re.sub(r"(r|l)", "w", message)
    reply_text = re.sub(r"(R|L)", "W", reply_text)
    reply_text = re.sub(r"n([aeiou])", r"ny\1", reply_text)
    reply_text = re.sub(r"N([aeiouAEIOU])", r"Ny\1", reply_text)
    reply_text = re.sub(r"\!+", " " + choice(UWUS), reply_text)
    reply_text = reply_text.replace("ove", "uv")
    reply_text += " " + choice(UWUS)
    await event.edit(reply_text)


@register(outgoing=True, pattern="react")
@errors_handler
async def react_meme(event): # Make your userbot react to everything.
    await event.edit(choice(FACEREACTS))


@register(outgoing=True, pattern="shg")
@errors_handler
async def shrugger(event): # ¯\_(ツ)_/¯
    await event.edit(r"¯\_(ツ)_/¯")


@register(outgoing=True, pattern="runs")
@errors_handler
async def runner_lol(event): # Run, run, RUNNN!
    index = randint(0, len(RUNSREACTS) - 1)
    reply_text = RUNSREACTS[index]
    await event.edit(reply_text)


@register(outgoing=True, pattern="metoo")
@errors_handler
async def metoo(event): # Haha yes
    await event.edit(choice(METOOSTR))


@register(outgoing=True, pattern="mock")
@errors_handler
async def spongemocktext(event): # Do it and find the real fun.
    textx = await event.get_reply_message()
    message = event.pattern_match.group(1)
    reply_text = ''

    if message:
        data = message
    elif textx:
        data = textx.text
    else:
        data = 'Haha yes, I know how to mock text.'

    for letter in data:
        if len(reply_text) >= 2:
            if reply_text[-1] + reply_text[-2] == reply_text[-1].lower() + reply_text[-2].lower():
                reply_text += letter.upper()
                continue

            if reply_text[-1] + reply_text[-2] == reply_text[-1].upper() + reply_text[-2].upper():
                reply_text += letter.lower()
                continue

        if randint(1, 2) == randint(1, 2):
            reply_text += letter.lower()
        else:
            reply_text += letter.upper()

    await event.edit(reply_text)


@register(outgoing=True, pattern="clap")
@errors_handler
async def claptext(event): # Praise people!
    textx = await event.get_reply_message()
    message = event.pattern_match.group(1)
    if message:
        pass
    elif textx:
        message = textx.text
    else:
        message = "Hah, I don't clap pointlessly!"

    reply_text = "👏 "
    reply_text += message.replace(" ", " 👏 ")
    reply_text += " 👏"
    await event.edit(reply_text)


@register(outgoing=True, pattern="bt")
@errors_handler
async def bluetext(event): # Believe me, you will find this useful.
    await event.edit("/BLUETEXT /MUST /CLICK\n/IM /A /STOOPID /ANIMAL /THATS /ATTRACTED /TO /COLORZ!")


@register(pattern='type')
@errors_handler
async def typewriter(event): # Just a small command to make your keyboard become a typewriter!
    textx = await event.get_reply_message()
    message = event.pattern_match.group(1)
    if message:
        pass
    elif textx:
        message = textx.text
    else:
        message = "Gimme text to type!"

    sleep_time = 0.02
    typing_symbol = "|"
    old_text = ''
    await event.edit(typing_symbol)
    await asyncio.sleep(sleep_time)
    for character in message:
        old_text = old_text + "" + character
        typing_text = old_text + "" + typing_symbol
        await event.edit(typing_text)
        await asyncio.sleep(sleep_time)
        await event.edit(old_text)
        await asyncio.sleep(sleep_time)


CMD_HELP.update({
    "memes":
    "Ask 🅱️ottom🅱️ext🅱️ot (@NotAMemeBot) for that."
})
