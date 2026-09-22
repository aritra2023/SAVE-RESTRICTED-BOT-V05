# ---------------------------------------------------
# File Name: main.py
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
# More readable 
# ---------------------------------------------------

import time
import random
import string
import asyncio
from pyrogram import filters, Client
from pyrogram.enums import ParseMode
from devgagan import app, userrbot
from config import API_ID, API_HASH, FREEMIUM_LIMIT, PREMIUM_LIMIT, OWNER_ID, DEFAULT_SESSION
from devgagan.core.get_func import get_msg
from devgagan.core.func import *
from devgagan.core.mongo import db
from pyrogram.errors import FloodWait
from datetime import datetime, timedelta
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import subprocess
from devgagan.modules.shrink import is_user_verified

async def generate_random_name(length=8):
    return ''.join(random.choices(string.ascii_lowercase, k=length))

users_loop = {}
interval_set = {}
batch_mode = {}

async def process_and_upload_link(userbot, user_id, msg_id, link, retry_count, message):
    try:
        await get_msg(userbot, user_id, msg_id, link, retry_count, message)
        try:
            await app.delete_messages(user_id, msg_id)
        except Exception:
            pass
        await asyncio.sleep(15)
    finally:
        pass

# Function to check if the user can proceed
async def check_interval(user_id, freecheck):
    if freecheck != 1 or await is_user_verified(user_id):  # Premium or owner users can always proceed
        return True, None

    now = datetime.now()

    # Check if the user is on cooldown
    if user_id in interval_set:
        cooldown_end = interval_set[user_id]
        if now < cooldown_end:
            remaining_time = (cooldown_end - now).seconds
            # Using <blockquote> for HTML parse mode quotes
            return False, f"<i>Please wait {remaining_time} seconds(s) before sending another link. Alternatively, purchase premium for instant access.</i>\n\n<blockquote><i>Hey 👋 You can use /token to use the bot free for 3 hours without any time limit.</i></blockquote>"
        else:
            del interval_set[user_id]  # Cooldown expired, remove user from interval set

    return True, None

async def set_interval(user_id, interval_minutes=45):
    now = datetime.now()
    # Set the cooldown interval for the user
    interval_set[user_id] = now + timedelta(seconds=interval_minutes)
    

@app.on_message(
    filters.regex(r'https?://(?:www\.)?t\.me/[^\s]+|tg://openmessage\?user_id=\w+&message_id=\d+')
    & filters.private
)
async def single_link(_, message):
    user_id = message.chat.id

    # Check subscription and batch mode
    if await subscribe(_, message) == 1 or user_id in batch_mode:
        return

    # Check if user is already in a loop
    if users_loop.get(user_id, False):
        await message.reply(
            "<i>You already have an ongoing process. Please wait for it to finish or cancel it with /cancel.</i>",
            parse_mode=ParseMode.HTML
        )
        return

    # Check freemium limits
    if await chk_user(message, user_id) == 1 and FREEMIUM_LIMIT == 0 and user_id not in OWNER_ID and not await is_user_verified(user_id):
        await message.reply("<i>Freemium service is currently not available. Upgrade to premium for access or use /token.</i>", parse_mode=ParseMode.HTML)
        return

    # Check cooldown
    can_proceed, response_message = await check_interval(user_id, await chk_user(message, user_id))
    if not can_proceed:
        await message.reply(response_message, parse_mode=ParseMode.HTML)
        return

    # Add user to the loop
    users_loop[user_id] = True

    link = message.text if "tg://openmessage" in message.text else get_link(message.text)
    msg = await message.reply("<i>Processing...</i>", parse_mode=ParseMode.HTML)
    userbot = await initialize_userbot(user_id)
    try:
        if await is_normal_tg_link(link):
            await process_and_upload_link(userbot, user_id, msg.id, link, 0, message)
            await set_interval(user_id, interval_minutes=45)
        else:
            await process_special_links(userbot, user_id, msg, link)
            
    except FloodWait as fw:
        await msg.edit_text(f"<i>Try again after {fw.x} seconds due to floodwait from Telegram.</i>", parse_mode=ParseMode.HTML)
    except Exception as e:
        await msg.edit_text(f"Link: `{link}`\n\n<i>Error: {str(e)}</i>", parse_mode=ParseMode.HTML)
    finally:
        users_loop[user_id] = False
        try:
            await msg.delete()
        except Exception:
            pass


async def initialize_userbot(user_id): # this ensure the single startup .. even if logged in or not
    data = await db.get_data(user_id)
    if data and data.get("session"):
        try:
            device = 'iPhone 16 Pro' # added gareebi text
            userbot = Client(
                "userbot",
                api_id=API_ID,
                api_hash=API_HASH,
                device_model=device,
                session_string=data.get("session")
            )
            await userbot.start()
            return userbot
        except Exception:
            await app.send_message(user_id, "<i>Login Expired re do login</i>", parse_mode=ParseMode.HTML)
            return None
    else:
        if DEFAULT_SESSION:
            return userrbot
        else:
            return None


async def is_normal_tg_link(link: str) -> bool:
    """Check if the link is a standard Telegram link."""
    special_identifiers = ['t.me/+', 't.me/c/', 't.me/b/', 'tg://openmessage']
    return 't.me/' in link and not any(x in link for x in special_identifiers)
    
async def process_special_links(userbot, user_id, msg, link):
    if userbot is None:
        return await msg.edit_text("<i>Try logging in to the bot and try again.</i>", parse_mode=ParseMode.HTML)
    if 't.me/+' in link:
        result = await userbot_join(userbot, link)
        await msg.edit_text(result)
        return
    special_patterns = ['t.me/c/', 't.me/b/', '/s/', 'tg://openmessage']
    if any(sub in link for sub in special_patterns):
        await process_and_upload_link(userbot, user_id, msg.id, link, 0, msg)
        await set_interval(user_id, interval_minutes=45)
        return
    await msg.edit_text("<b>Invalid link !!</b>", parse_mode=ParseMode.HTML)


@app.on_message(filters.command("batch") & filters.private)
async def batch_link(_, message):
    join = await subscribe(_, message)
    if join == 1:
        return
    user_id = message.chat.id
    # Check if a batch process is already running
    if users_loop.get(user_id, False):
        await app.send_message(
            message.chat.id,
            "<i>You already have a batch process running. Please wait for it to complete.</i>",
            parse_mode=ParseMode.HTML
        )
        return

    freecheck = await chk_user(message, user_id)
    if freecheck == 1 and FREEMIUM_LIMIT == 0 and user_id not in OWNER_ID and not await is_user_verified(user_id):
        await message.reply("<i>Freemium service is currently not available. Upgrade to premium for access or use /token.</i>", parse_mode=ParseMode.HTML)
        return

    max_batch_size = FREEMIUM_LIMIT if freecheck == 1 else PREMIUM_LIMIT

    # Start link input (Fixed by using Pyrogram Markdown italics '__')
    for attempt in range(3):
        start = await app.ask(message.chat.id, "__Please send the start link.__\n\n> __Maximum tries 3__")
        start_id = start.text.strip()
        s = start_id.split("/")[-1]
        if s.isdigit():
            cs = int(s)
            break
        await app.send_message(message.chat.id, "<b><i>Invalid link, Please send again !!</i></b>", parse_mode=ParseMode.HTML)
    else:
        await app.send_message(message.chat.id, "<i>Maximum attempts exceeded. Try again later.</i>", parse_mode=ParseMode.HTML)
        return

    # Number of messages input (Fixed by using Pyrogram Markdown italics '__')
    for attempt in range(3):
        num_messages = await app.ask(message.chat.id, f"__How many messages do you want to process?__\n> __Max limit {max_batch_size}__")
        try:
            cl = int(num_messages.text.strip())
            if 1 <= cl <= max_batch_size:
                break
            raise ValueError()
        except ValueError:
            await app.send_message(
                message.chat.id, 
                f"<i>Invalid number. Please enter a number between 1 and {max_batch_size}.</i>",
                parse_mode=ParseMode.HTML
            )
    else:
        await app.send_message(message.chat.id, "<i>Maximum attempts exceeded. Try again later.</i>", parse_mode=ParseMode.HTML)
        return

    # Validate and interval check
    can_proceed, response_message = await check_interval(user_id, freecheck)
    if not can_proceed:
        await message.reply(response_message, parse_mode=ParseMode.HTML)
        return
        
    join_button = InlineKeyboardButton("Join Channel", url="https://t.me/team_spy_pro")
    keyboard = InlineKeyboardMarkup([[join_button]])
    
    # Batch Process Started Text Format (Italic + Bold Italic bottom line)
    pin_msg = await app.send_message(
        user_id,
        f"<i>Batch process started ⚡</i>\n<i>Processing: 0/{cl}</i>\n\n<b><i>Powered by @Itzishan</i></b>",
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML
    )
    await pin_msg.pin(both_sides=True)

    users_loop[user_id] = True
    try:
        normal_links_handled = False
        userbot = await initialize_userbot(user_id)
        # Handle normal links first
        for i in range(cs, cs + cl):
            if user_id in users_loop and users_loop[user_id]:
                url = f"{'/'.join(start_id.split('/')[:-1])}/{i}"
                link = get_link(url)
                # Process t.me links (normal) without userbot
                if 't.me/' in link and not any(x in link for x in ['t.me/b/', 't.me/c/', 'tg://openmessage']):
                    msg = await app.send_message(message.chat.id, f"<i>Processing...</i>", parse_mode=ParseMode.HTML)
                    await process_and_upload_link(userbot, user_id, msg.id, link, 0, message)
                    await pin_msg.edit_text(
                        f"<i>Batch process started ⚡</i>\n<i>Processing: {i - cs + 1}/{cl}</i>\n\n<b><i>Powered by @Itzishan</i></b>",
                        reply_markup=keyboard,
                        parse_mode=ParseMode.HTML
                    )
                    normal_links_handled = True
        if normal_links_handled:
            await set_interval(user_id, interval_minutes=300)
            await pin_msg.edit_text(
                f"<i>Batch completed successfully for {cl} messages 🎉</i>\n\n<b><i>Powered by @Itzishan</i></b>",
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML
            )
            await app.send_message(message.chat.id, "<b><i>Batch completed successfully! 🎉</i></b>", parse_mode=ParseMode.HTML)
            return
            
        # Handle special links with userbot
        for i in range(cs, cs + cl):
            if not userbot:
                await app.send_message(message.chat.id, "<b><i>Login in bot first !!</i></b>", parse_mode=ParseMode.HTML)
                users_loop[user_id] = False
                return
            if user_id in users_loop and users_loop[user_id]:
                url = f"{'/'.join(start_id.split('/')[:-1])}/{i}"
                link = get_link(url)
                if any(x in link for x in ['t.me/b/', 't.me/c/']):
                    msg = await app.send_message(message.chat.id, f"<i>Processing...</i>", parse_mode=ParseMode.HTML)
                    await process_and_upload_link(userbot, user_id, msg.id, link, 0, message)
                    await pin_msg.edit_text(
                        f"<i>Batch process started ⚡</i>\n<i>Processing: {i - cs + 1}/{cl}</i>\n\n<b><i>Powered by @Itzishan</i></b>",
                        reply_markup=keyboard,
                        parse_mode=ParseMode.HTML
                    )

        await set_interval(user_id, interval_minutes=300)
        await pin_msg.edit_text(
            f"<i>Batch completed successfully for {cl} messages 🎉</i>\n\n<b><i>Powered by @Itzishan</i></b>",
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )
        await app.send_message(message.chat.id, "<b><i>Batch completed successfully! 🎉</i></b>", parse_mode=ParseMode.HTML)

    except Exception as e:
        await app.send_message(message.chat.id, f"<i>Error: {e}</i>", parse_mode=ParseMode.HTML)
    finally:
        users_loop.pop(user_id, None)

@app.on_message(filters.command("cancel"))
async def stop_batch(_, message):
    user_id = message.chat.id

    # Check if there is an active batch process for the user
    if user_id in users_loop and users_loop[user_id]:
        users_loop[user_id] = False  # Set the loop status to False
        await app.send_message(
            message.chat.id, 
            "<i>❌Batch processing has been stopped successfully. You can start a new batch now if you want.</i>",
            parse_mode=ParseMode.HTML
        )
    elif user_id in users_loop and not users_loop[user_id]:
        await app.send_message(
            message.chat.id, 
            "<i>The batch process was already stopped. No active batch to cancel.</i>",
            parse_mode=ParseMode.HTML
        )
    else:
        await app.send_message(
            message.chat.id, 
            "<i>No active batch processing is running to cancel.</i>",
            parse_mode=ParseMode.HTML
        )
