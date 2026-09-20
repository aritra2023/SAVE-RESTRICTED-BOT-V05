# ---------------------------------------------------
# File Name: func.py
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

import math
import time, re
from pyrogram import enums
from config import CHANNEL_ID, OWNER_ID 
from devgagan.core.mongo.plans_db import premium_users
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import cv2
from pyrogram.errors import FloodWait, InviteHashInvalid, InviteHashExpired, UserAlreadyParticipant, UserNotParticipant
from datetime import datetime as dt
import asyncio, subprocess, os

async def chk_user(message, user_id):
    user = await premium_users()
    if user_id in user or user_id in OWNER_ID:
        return 0
    else:
        return 1

async def gen_link(app,chat_id):
   link = await app.export_chat_invite_link(chat_id)
   return link

async def subscribe(app, message):
    # Dono force channels yahan add kar diye gaye hain
    update_channels = [-1004443016082, -1004298619601]
    
    # Links dynamically export honge
    links = []
    for chat_id in update_channels:
        try:
            link = await app.export_chat_invite_link(chat_id)
            links.append(link)
        except Exception:
            # Agar bot admin nahi hai toh fail-safe link
            links.append("https://t.me/itzishan")

    not_joined = False
    
    for chat_id in update_channels:
        try:
            user = await app.get_chat_member(chat_id, message.from_user.id)
            if user.status in [enums.ChatMemberStatus.BANNED, enums.ChatMemberStatus.RESTRICTED]:
                await message.reply_text("You are Banned. Contact -- @devgaganin")
                return 1
        except UserNotParticipant:
            not_joined = True
            break
        except Exception as e:
            # Bug Fix: Error aane par bhi theek se handle hoga, stuck nahi hoga
            print(f"Force Sub check failed for {chat_id}: {e}")
            not_joined = True
            break

    if not_joined:
        # Custom Bold aur Italic text HTML format mein
        caption = "<b>⊘ Access Denied!</b>\n\n<b><i>To use this bot, you must join our updates channel and group first.</i></b>"
        
        # Dono buttons ek hi row (bagal-bagal) mein set kar diye hain
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("Join Channel 1", url=links[0]),
                InlineKeyboardButton("Join Channel 2", url=links[1])
            ]
        ])
        await message.reply_photo(
            photo="https://telegra.ph/file/e5ef835d0d3bd3bde573a-67046e40dd457fbe1b.jpg",
            caption=caption, 
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.HTML
        )
        return 1
    return 0

async def get_seconds(time_string):
    def extract_value_and_unit(ts):
        value = ""
        unit = ""

        index = 0
        while index < len(ts) and ts[index].isdigit():
            value += ts[index]
            index += 1

        unit = ts[index:].lstrip()

        if value:
            value = int(value)

        return value, unit

    value, unit = extract_value_and_unit(time_string)

    if unit == 's':
        return value
    elif unit == 'min':
        return value * 60
    elif unit == 'hour':
        return value * 3600
    elif unit == 'day':
        return value * 86400
    elif unit == 'month':
        return value * 86400 * 30
    elif unit == 'year':
        return value * 86400 * 365
    else:
        return 0


async def progress_bar(current, total, ud_type, message, start):
    now = time.time()
    diff = now - start
    if round(diff % 10.00) == 0 or current == total:
        percentage = current * 100 / total
        speed = current / diff if diff > 0 else 0
        elapsed_time = round(diff) * 1000
        time_to_completion = round((total - current) / speed) * 1000 if speed > 0 else 0
        estimated_total_time = elapsed_time + time_to_completion

        elapsed_time = TimeFormatter(milliseconds=elapsed_time)
        estimated_total_time = TimeFormatter(milliseconds=estimated_total_time)

        completed_blocks = int(percentage // 10)
        remaining_blocks = 10 - completed_blocks
        progress = "■" * completed_blocks + "□" * remaining_blocks

        clean_ud_type = ud_type.split('\n')[0].strip() if '\n' in ud_type else ud_type.strip()
        if "Down" in clean_ud_type or "down" in clean_ud_type:
            clean_ud_type = "Downloading ..."
        else:
            clean_ud_type = "Uploading ..."

        # Fixed Markdown for clickable progress bar
        tmp = (
            f"╭───────────⌬\n"
            f"┟─[[  📥 **{clean_ud_type}**  ]]\n"
            f"├────────⌬\n"
            f"┟ [{progress}](https://t.me/itzishan)\n"
            f"┟ **Completed:** __{humanbytes(current)}/{humanbytes(total)}__\n"
            f"┟ **Bytes:** __{round(percentage, 2)}%__\n"
            f"┟ **Speed:** __{humanbytes(speed)}/s__\n"
            f"┖ **ETA:** __{estimated_total_time if estimated_total_time != '' else '0 s'}__"
        )
        try:
            await message.edit(
                text=tmp,
                disable_web_page_preview=True
            )             
        except:
            pass

def humanbytes(size):
    if not size:
        return ""
    power = 2**10
    n = 0
    Dic_powerN = {0: ' ', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
    while size > power:
        size /= power
        n += 1
    return str(round(size, 2)) + " " + Dic_powerN[n] + 'B'

def TimeFormatter(milliseconds: int) -> str:
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = ((str(days) + "d, ") if days else "") + \
        ((str(hours) + "h, ") if hours else "") + \
        ((str(minutes) + "m, ") if minutes else "") + \
        ((str(seconds) + "s, ") if seconds else "") + \
        ((str(milliseconds) + "ms, ") if milliseconds else "")
    return tmp[:-2] 

def convert(seconds):
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60      
    return "%d:%02d:%02d" % (hour, minutes, seconds)

async def userbot_join(userbot, invite_link):
    try:
        await userbot.join_chat(invite_link)
        return "Successfully joined the Channel"
    except UserAlreadyParticipant:
        return "User is already a participant."
    except (InviteHashInvalid, InviteHashExpired):
        return "Could not join. Maybe your link is expired or Invalid."
    except FloodWait:
        return "Too many requests, try again later."
    except Exception as e:
        print(e)
        return "Could not join, try joining manually."

def get_link(string):
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    url = re.findall(regex,string)   
    try:
        link = [x[0] for x in url][0]
        if link:
            return link
        else:
            return False
    except Exception:
        return False

def video_metadata(file):
    default_values = {'width': 1, 'height': 1, 'duration': 1}
    try:
        vcap = cv2.VideoCapture(file)
        if not vcap.isOpened():
            return default_values  

        width = round(vcap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = round(vcap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = vcap.get(cv2.CAP_PROP_FPS)
        frame_count = vcap.get(cv2.CAP_PROP_FRAME_COUNT)

        if fps <= 0:
            return default_values  

        duration = round(frame_count / fps)
        if duration <= 0:
            return default_values  

        vcap.release()
        return {'width': width, 'height': height, 'duration': duration}

    except Exception as e:
        print(f"Error in video_metadata: {e}")
        return default_values

def hhmmss(seconds):
    return time.strftime('%H:%M:%S',time.gmtime(seconds))

async def screenshot(video, duration, sender):
    if os.path.exists(f'{sender}.jpg'):
        return f'{sender}.jpg'
    time_stamp = hhmmss(int(duration)/2)
    out = dt.now().isoformat("_", "seconds") + ".jpg"
    cmd = ["ffmpeg",
           "-ss",
           f"{time_stamp}", 
           "-i",
           f"{video}",
           "-frames:v",
           "1", 
           f"{out}",
           "-y"
          ]
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    x = stderr.decode().strip()
    y = stdout.decode().strip()
    if os.path.isfile(out):
        return out
    else:
        None  

last_update_time = time.time()
async def progress_callback(current, total, progress_message):
    percent = (current / total) * 100
    global last_update_time
    current_time = time.time()

    if current_time - last_update_time >= 10 or percent % 10 == 0:
        completed_blocks = int(percent // 10)
        remaining_blocks = 10 - completed_blocks
        progress = "■" * completed_blocks + "□" * remaining_blocks
        
        current_mb = current / (1024 * 1024)  
        total_mb = total / (1024 * 1024)      
        
        # Fixed Markdown for clickable progress bar
        tmp = (
            f"╭───────────────────⌬\n"
            f"┟─[[  📥 **Uploading ...**  ]]\n"
            f"├──────────────⌬\n"
            f"┟ [{progress}](https://t.me/itzishan)\n"
            f"┟ **Completed:** __{current_mb:.2f} MB/{total_mb:.2f} MB__\n"
            f"┟ **Bytes:** __{percent:.2f}%__\n"
            f"┖ **ETA:** __Calculating...__"
        )
        try:
            await progress_message.edit(
                text=tmp,
                disable_web_page_preview=True
            )
            last_update_time = current_time
        except:
            pass

async def prog_bar(current, total, ud_type, message, start):
    now = time.time()
    diff = now - start
    if round(diff % 10.00) == 0 or current == total:
        percentage = current * 100 / total
        speed = current / diff if diff > 0 else 0
        elapsed_time = round(diff) * 1000
        time_to_completion = round((total - current) / speed) * 1000 if speed > 0 else 0
        estimated_total_time = elapsed_time + time_to_completion

        elapsed_time = TimeFormatter(milliseconds=elapsed_time)
        estimated_total_time = TimeFormatter(milliseconds=estimated_total_time)

        completed_blocks = int(percentage // 10)
        remaining_blocks = 10 - completed_blocks
        progress = "■" * completed_blocks + "□" * remaining_blocks

        clean_ud_type = ud_type.split('\n')[0].strip() if '\n' in ud_type else ud_type.strip()
        if "Down" in clean_ud_type or "down" in clean_ud_type:
            clean_ud_type = "Downloading ..."
        else:
            clean_ud_type = "Uploading ..."

        # Fixed Markdown for clickable progress bar
        tmp = (
            f"╭─────────────────⌬\n"
            f"┟─[[  📥 **{clean_ud_type}**  ]]\n"
            f"├──────────────⌬\n"
            f"┟ [{progress}](https://t.me/itzishan)\n"
            f"┟ **Completed:** __{humanbytes(current)}/{humanbytes(total)}__\n"
            f"┟ **Bytes:** __{round(percentage, 2)}%__\n"
            f"┟ **Speed:** __{humanbytes(speed)}/s__\n"
            f"┖ **ETA:** __{estimated_total_time if estimated_total_time != '' else '0 s'}__"
        )
        try:
            await message.edit_text(
                text=tmp,
                disable_web_page_preview=True
            )             
        except:
            pass
            
