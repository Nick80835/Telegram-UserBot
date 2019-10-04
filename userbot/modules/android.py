# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#
""" Userbot module containing commands related to android"""

import re
from requests import get
from bs4 import BeautifulSoup
from userbot import CMD_HELP, CMDPREFIX
from userbot.events import register, errors_handler

GITHUB = 'https://github.com'
DEVICES_DATA = 'https://raw.githubusercontent.com/androidtrackers/' \
               'certified-android-devices/master/devices.json'


@register(outgoing=True, pattern="magisk")
@errors_handler
async def magisk(event):
    # for .magisk command, give links to the latest releases
    url = 'https://raw.githubusercontent.com/topjohnwu/magisk_files/master/'
    urlCanary = 'https://raw.githubusercontent.com/topjohnwu/magisk_files/canary/'

    releases = 'Latest Magisk Releases:\n'

    for variant in ['stable', 'beta']: # stable and beta builds
        data = get(url + variant + '.json').json()
        name = variant.title()
        releases += f'{name}: [ZIP v{data["magisk"]["version"]}]({data["magisk"]["link"]}) | ' \
                    f'[APK v{data["app"]["version"]}]({data["app"]["link"]}) | ' \
                    f'[Uninstaller]({data["uninstaller"]["link"]})\n'
    for variant in ['release']: # canary builds
        data = get(urlCanary + variant + '.json').json()
        name = 'Canary'
        releases += f'{name}: [ZIP v{data["magisk"]["version"]}]({data["magisk"]["link"]}) | ' \
                    f'[APK v{data["app"]["version"]}]({data["app"]["link"]}) | ' \
                    f'[Uninstaller]({data["uninstaller"]["link"]})\n'

    await event.edit(releases)


@register(outgoing=True, pattern="device")
@errors_handler
async def device_info(event):
    # for .device command, search for a device based on name, codename, model
    textx = await event.get_reply_message()
    device = "".join(event.pattern_match.groups())
    if device:
        pass
    elif textx:
        device = textx.text
    else:
        await event.edit("`Usage: .device <codename> / <model> / <name>`")
        return
    found = [
        i for i in get(DEVICES_DATA).json()
        if i["device"].lower() == device.lower() or
            i["model"].lower() == device.lower() or
            i["name"].lower() == device.lower() or
            f'{i["brand"]} {i["name"]}'.lower() == device.lower()
    ]
    if found:
        reply = f'Search results for {device}:\n'
        for item in found:
            brand = item['brand']
            name = item['name']
            codename = item['device']
            model = item['model']
            reply += f'{brand} {name}\n' \
                f'**Codename**: `{codename}`\n' \
                f'**Model**: {model}\n\n'
    else:
        reply = f"`Couldn't find info about {device}!`\n"
    await event.edit(reply)


@register(outgoing=True, pattern="specs")
@errors_handler
async def devices_specifications(event):
    # for .specs command, list the specs for a given device
    textx = await event.get_reply_message()
    try:
        brand = event.pattern_match.groups()[0].split()[0].lower()
        device = ' '.join(event.pattern_match.groups()[0].split()[1:]).lower()
    except:
        brand = None
        device = None
    if brand and device:
        pass
    elif textx:
        brand = textx.text.split(' ')[0]
        device = ' '.join(textx.text.split(' ')[1:])
    else:
        await event.edit("`Usage: .specs <brand> <device>`")
        return
    all_brands = BeautifulSoup(
        get('https://www.devicespecifications.com/en/brand-more').content,
        'lxml').find('div', {
            'class': 'brand-listing-container-news'
        }).findAll('a')
    brand_page_url = None
    try:
        brand_page_url = [
            i['href'] for i in all_brands
            if brand == i.text.strip().lower()
        ][0]
    except IndexError:
        await event.edit(f'`{brand} is unknown brand!`')
    devices = BeautifulSoup(get(brand_page_url).content, 'lxml') \
        .findAll('div', {'class': 'model-listing-container-80'})
    device_page_url = None
    try:
        device_page_url = [
            i.a['href']
            for i in BeautifulSoup(str(devices), 'lxml').findAll('h3')
            if device in i.text.strip().lower()
        ]
    except IndexError:
        await event.edit(f"`can't find {device}!`")
    if len(device_page_url) > 2:
        device_page_url = device_page_url[:2]
    reply = ''
    for url in device_page_url:
        info = BeautifulSoup(get(url).content, 'lxml')
        reply = '\n' + info.title.text.split('-')[0].strip() + '\n'
        info = info.find('div', {'id': 'model-brief-specifications'})
        specifications = re.findall(r'<b>.*?<br/>', str(info))
        for item in specifications:
            title = re.findall(r'<b>(.*?)</b>', item)[0].strip()
            data = re.findall(r'</b>: (.*?)<br/>', item)[0]\
                .replace('<b>', '').replace('</b>', '').strip()
            reply += f'**{title}**: {data}\n'
    
    if reply or reply != "":
        await event.edit(reply)
    else:
        await event.edit(f"`Spec search failed for query: {brand} {device}`")


@register(outgoing=True, pattern="twrp")
@errors_handler
async def twrp(event):
    # for .twrp command, get a link to twrp for a given device
    textx = await event.get_reply_message()
    device = event.pattern_match.group(1)
    if device:
        pass
    elif textx:
        device = textx.text.split(' ')[0]
    else:
        await event.edit("`Usage: .twrp <codename>`")
        return
    url = get(f'https://dl.twrp.me/{device}/')
    if url.status_code == 404:
        reply = f"`Couldn't find twrp downloads for {device}!`\n"
        await event.edit(reply)
        return
    page = BeautifulSoup(url.content, 'lxml')
    download = page.find('table').find('tr').find('a')
    dl_link = f"https://dl.twrp.me{download['href']}"
    dl_file = download.text
    size = page.find("span", {"class": "filesize"}).text
    date = page.find("em").text.strip()
    reply = f'**Latest TWRP for {device}:**\n' \
        f'[{dl_file}]({dl_link}) - __{size}__\n' \
        f'**Updated:** __{date}__\n'
    await event.edit(reply)


CMD_HELP.update({
    "magisk":
    "Get latest Magisk releases"
})
CMD_HELP.update({
    "device":
    ".device <codename>\nUsage: Get info about android device codename or model."
})
CMD_HELP.update({
    "specs":
    ".specs <brand> <device>\nUsage: Get device specifications info."
})
CMD_HELP.update({
    "twrp":
    ".twrp <codename>\nUsage: Get latest twrp download for android device."
})
