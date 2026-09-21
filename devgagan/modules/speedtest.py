# ---------------------------------------------------
# File Name: speedtest.py
# Description: A Pyrogram bot for downloading files from Telegram channels or groups 
#              and uploading them back to Telegram.
# Author: Gagan
# GitHub: https://github.com/devgaganin/
# Telegram: https://t.me/team_spy_pro
# YouTube: https://youtube.com/@dev_gagan
# Created: 2025-01-11
# Last Modified: 2025-01-11
# Version: 2.0.5
# License: MIT License
# ---------------------------------------------------

from time import time
from speedtest import Speedtest
import math
from telethon import events
from devgagan import botStartTime
from devgagan import sex as gagan

SIZE_UNITS = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']

def get_readable_time(seconds: int) -> str:
    result = ''
    (days, remainder) = divmod(seconds, 86400)
    days = int(days)
    if days != 0:
        result += f'{days}d'
    (hours, remainder) = divmod(remainder, 3600)
    hours = int(hours)
    if hours != 0:
        result += f'{hours}h'
    (minutes, seconds) = divmod(remainder, 60)
    minutes = int(minutes)
    if minutes != 0:
        result += f'{minutes}m'
    seconds = int(seconds)
    result += f'{seconds}s'
    return result

def get_readable_file_size(size_in_bytes) -> str:
    if size_in_bytes is None:
        return '0B'
    index = 0
    while size_in_bytes >= 1024:
        size_in_bytes /= 1024
        index += 1
    try:
        return f'{round(size_in_bytes, 2)}{SIZE_UNITS[index]}'
    except IndexError:
        return 'File too large'


@gagan.on(events.NewMessage(incoming=True, pattern='/speedtest'))
async def speedtest(event):
    speed = await event.reply("**__🛜 Running Speed Test.\n💬 Please Wait About Few Seconds.__**")  #edit telethon
    test = Speedtest()
    test.get_best_server()
    test.download()
    test.upload()
    test.results.share()
    result = test.results.dict()
    path = (result['share'])
    currentTime = get_readable_time(time() - botStartTime)
    string_speed = f'''<blockquote><b>⌬<i>  🚀 Speedtest Info</i></b></blockquote>
├ <i>Upload: {speed_convert(result['upload'], False)}</i>
├ <i>Download: {speed_convert(result['download'], False)}</i>
├ <i>Ping: {result['ping']} ms</i>
├ <i>Time: {result['timestamp']}</i>
├ <i>Data Sent: {get_readable_file_size(int(result['bytes_sent']))}</i>
└ <i>Data Received: {get_readable_file_size(int(result['bytes_received']))}</i>

<blockquote><b>⌬<i> 🌐 Speedtest Server</i></b></blockquote>
├ <i>Name: {result['server']['name']}</i>
├ <i>Country: {result['server']['country']}, {result['server']['cc']}</i>
├ <i>Sponsor: {result['server']['sponsor']}</i>
├ <i>Latency: {result['server']['latency']}</i>
├ <i>Latitude: {result['server']['lat']}</i>
└ <i>Longitude: {result['server']['lon']}</i>

<blockquote><b>⌬<i> 👤 Client Details</i></b></blockquote>
├ <i>IP Address: {result['client']['ip']}</i>
├ <i>Latitude: {result['client']['lat']}</i>
├ <i>Longitude: {result['client']['lon']}</i>
├ <i>Country: {result['client']['country']}</i>
├ <i>ISP: {result['client']['isp']}</i>
└ <i>ISP Rating: {result['client']['isprating']}</i>

<blockquote><b><i>Powered by @Itzishan</i></b></blockquote>'''
    try:
        await event.reply(string_speed,file=path,parse_mode='html')
        await speed.delete()
    except Exception as g:
        await speed.delete()
        await event.reply(string_speed,parse_mode='html' )

def speed_convert(size, byte=True):
    if not byte: size = size / 8
    power = 2 ** 10
    zero = 0
    units = {0: "B/s", 1: "KB/s", 2: "MB/s", 3: "GB/s", 4: "TB/s"}
    while size > power:
        size /= power
        zero += 1
    return f"{round(size, 2)} {units[zero]}"
