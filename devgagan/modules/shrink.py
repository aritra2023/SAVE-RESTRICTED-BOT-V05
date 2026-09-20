# ---------------------------------------------------
# File Name: shrink.py
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

import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.enums import ParseMode
import random
import string
import aiohttp
from devgagan import app
from devgagan.core.func import *
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_DB, WEBSITE_URL, AD_API, LOG_GROUP  
 
tclient = AsyncIOMotorClient(MONGO_DB)
tdb = tclient["telegram_bot"]
token = tdb["tokens"]
 
async def create_ttl_index():
    await token.create_index("expires_at", expireAfterSeconds=0)
 
Param = {}
 
async def generate_random_param(length=8):
    """Generate a random parameter."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
 
async def get_shortened_url(deep_link):
    api_url = f"https://{WEBSITE_URL}/api?api={AD_API}&url={deep_link}"
 
    async with aiohttp.ClientSession() as session:
        async with session.get(api_url) as response:
            if response.status == 200:
                data = await response.json()   
                if data.get("status") == "success":
                    return data.get("shortenedUrl")
    return None
 
async def is_user_verified(user_id):
    """Check if a user has an active session."""
    session = await token.find_one({"user_id": user_id})
    return session is not None
 
@app.on_message(filters.command("start"))
async def token_handler(client, message):
    """Handle the /token command."""
    
    # 1. Reaction (Removed 100 emoji)
    emojis = ["👍", "❤️", "🔥", "🥰", "👏", "🎉", "🤩", "⚡", "🏆"]
    try:
        await client.send_reaction(
            chat_id=message.chat.id, 
            message_id=message.id, 
            emoji=random.choice(emojis), 
            big=True
        )
    except Exception:
        pass

    join = await subscribe(client, message)
    if join == 1:
        return
    
    user_id = message.chat.id
    first_name = message.from_user.first_name if message.from_user else "User"

    if len(message.command) <= 1:
        
        # 2. Updated Animated Sticker ID
        sticker_id = "CAACAgQAAxkBAAER7RBqsFFqPO_VzQy0HKNQ9nJpl_VWcAACTBYAAtURSVGPuDSsezeyDz0E"
        try:
            sticker_msg = await client.send_sticker(chat_id=user_id, sticker=sticker_id)
            await asyncio.sleep(2.5) 
            await sticker_msg.delete()
        except Exception:
            pass 
            
        # 3. Main Welcome Message
        image_url = "https://telegra.ph/file/4275f49171b91a3e54846-ba3061bfeca029f934.jpg" 
        
        # 4. Help Button with callback_data="help"
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("Dᴇᴠᴇʟᴏᴘᴇʀ 👨‍💻", url="https://t.me/itzishan"), 
                InlineKeyboardButton("Uᴘᴅᴀᴛᴇs 🚨", url="https://t.me/+BUF3hu-cKn00Y2Q1")       
            ],
            [
                InlineKeyboardButton("Hᴇʟᴘ", callback_data="help"), 
                InlineKeyboardButton("Aʙᴏᴜᴛ Mᴇ 😎", callback_data="about") 
            ]
        ])
         
        caption = (
            f"<blockquote><b><i>Yoo <a href='tg://user?id={user_id}'>{first_name}</a> !! Welcome Aboard</i></b></blockquote>\n"
            f"<blockquote><b><i>I Can Save Posts From Channels or Groups Even When Forwarding is Disabled (Yep, I'm That Powerful 😎) </i></b>\n\n"
            f"<b><i>For Public Channel Just Send the Link of the Post & For Private Channel Use /login First 🔑</i></b></blockquote>"
        )
         
        try:
            # Effect ID integer format mein pass kiya hai
            await message.reply_photo(
                photo=image_url,
                caption=caption,
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML,
                effect_id=5046509860389126442
            )
        except TypeError:
            try:
                await message.reply_photo(
                    photo=image_url,
                    caption=caption,
                    reply_markup=keyboard,
                    parse_mode=ParseMode.HTML
                )
            except Exception:
                await message.reply_text(
                    text=caption,
                    reply_markup=keyboard,
                    parse_mode=ParseMode.HTML
                )
        except Exception:
            await message.reply_text(
                text=caption,
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML
            )
        return  
 
    param = message.command[1] if len(message.command) > 1 else None
    freecheck = await chk_user(message, user_id)
    
    # 5. Bold + Italic Premium user msg
    if freecheck != 1:
        await message.reply("<b><i>You are a Premium User 😉\nSpecial person don't require a Token.</i></b>", parse_mode=ParseMode.HTML)
        return
 
    if param:
        if user_id in Param and Param[user_id] == param:
            await token.insert_one({
                "user_id": user_id,
                "param": param,
                "created_at": datetime.utcnow(),
                "expires_at": datetime.utcnow() + timedelta(hours=3),
            })
            del Param[user_id]   
            await message.reply("✅ You have been verified successfully! Enjoy your session for next 3 hours.")
            return
        else:
            await message.reply("❌ Invalid or expired verification link. Please generate a new token.")
            return
 
@app.on_message(filters.command("token"))
async def smart_handler(client, message):
    user_id = message.chat.id
     
    freecheck = await chk_user(message, user_id)
    
    # 5. Bold + Italic Premium user msg
    if freecheck != 1:
        await message.reply("<b><i>You are a Premium User 😉\nSpecial person don't require a Token.</i></b>", parse_mode=ParseMode.HTML)
        return
        
    if await is_user_verified(user_id):
        await message.reply("✅ Your free session is already active enjoy!")
    else:
        param = await generate_random_param()
        Param[user_id] = param   
 
        deep_link = f"https://t.me/{client.me.username}?start={param}"
 
        shortened_url = await get_shortened_url(deep_link)
        if not shortened_url:
            await message.reply("❌ Failed to generate the token link. Please try again.")
            return
 
        button = InlineKeyboardMarkup(
            [[InlineKeyboardButton("Verify the token now...", url=shortened_url)]]
        )
        await message.reply("Click the button below to verify your free access token: \n\n> What will you get ? \n1. No time bound upto 3 hours \n2. Batch command limit will be FreeLimit + 20 \n3. All functions unlocked", reply_markup=button)
     
