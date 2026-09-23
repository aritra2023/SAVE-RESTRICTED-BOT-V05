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
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
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
        
        sticker_id = "CAACAgQAAxkBAAER7RBqsFFqPO_VzQy0HKNQ9nJpl_VWcAACTBYAAtURSVGPuDSsezeyDz0E"
        try:
            sticker_msg = await client.send_sticker(chat_id=user_id, sticker=sticker_id)
            await asyncio.sleep(1.0)
            await sticker_msg.delete()
        except Exception:
            pass 
            
        image_url = "https://telegra.ph/file/76f4eaf6ea1b69cc110d2-338c7b87a70a7356df.jpg" 
        
        # Help replaced by Premium Button
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("Dᴇᴠᴇʟᴏᴘᴇʀ <tg-emoji emoji-id="6019529817920117353">ðŸ–¥</tg-emoji>👨‍💻", url="https://t.me/itzishan"), 
                InlineKeyboardButton("Uᴘᴅᴀᴛᴇs 🚨", url="https://t.me/+BUF3hu-cKn00Y2Q1")       
            ],
            [
                InlineKeyboardButton("Pʀᴇᴍɪᴜᴍ 💎", url="https://t.me/itzishan?text=I%20Want%20To%20Know%20More%20About%20This%20Plan%20%21%21"), 
                InlineKeyboardButton("Aʙᴏᴜᴛ Mᴇ 😎", callback_data="about") 
            ]
        ])
         
        caption = (
            f"<blockquote><b><i>Yoo <a href='tg://user?id={user_id}'>{first_name}</a> !! Welcome Aboard</i></b></blockquote>\n"
            f"<blockquote><b><i>I Can Save Posts From Channels or Groups Even When Forwarding is Disabled (Yep, I'm That Powerful 😎) </i></b>\n\n"
            f"<b><i>For Public Channel Just Send the Link of the Post & For Private Channel Use /login First 🔑</i></b></blockquote>"
        )
         
        try:
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
            await message.reply("<b><i>✅ You have been verified successfully!</i></b> <i>Enjoy your session for next 3 hours.</i>", parse_mode=ParseMode.HTML)
            return
        else:
            await message.reply("<b><i>❌ Invalid or expired verification link.</i></b> <i>Please generate a new token.</i>", parse_mode=ParseMode.HTML)
            return
 
@app.on_message(filters.command("token"))
async def smart_handler(client, message):
    user_id = message.chat.id
     
    freecheck = await chk_user(message, user_id)
    if freecheck != 1:
        await message.reply("<b><i>You are a Premium User 😉\nSpecial person don't require a Token.</i></b>", parse_mode=ParseMode.HTML)
        return
        
    if await is_user_verified(user_id):
        await message.reply("<b><i>✅ Your free session is already active enjoy !!</i></b>", parse_mode=ParseMode.HTML)
    else:
        param = await generate_random_param()
        Param[user_id] = param   
 
        deep_link = f"https://t.me/{client.me.username}?start={param}"
 
        shortened_url = await get_shortened_url(deep_link)
        if not shortened_url:
            await message.reply("<b><i>❌ Failed to generate the token link. Please try again.</i></b>", parse_mode=ParseMode.HTML)
            return
 
        button = InlineKeyboardMarkup(
            [[InlineKeyboardButton("Vᴇʀɪғʏ Nᴏᴡ...", url=shortened_url)]]
        )
        
        await message.reply(
            "<i>Click the button below to verify your free access token:</i> \n\n"
            "<blockquote><b><i>What will you get ?</i></b></blockquote>\n"
            "<i>1. No time bound upto 3 hours \n"
            "2. Batch command limit will be FreeLimit + 20 \n"
            "3. All functions unlocked</i>", 
            reply_markup=button,
            parse_mode=ParseMode.HTML
        ) 


# --- Callback Handlers for About and Home ---
@app.on_callback_query(filters.regex("about|home"))
async def cb_handler(client, query):
    user_id = query.from_user.id
    first_name = query.from_user.first_name if query.from_user else "User"

    if query.data == "home":
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("Dᴇᴠᴇʟᴏᴘᴇʀ 👨‍💻", url="https://t.me/itzishan"), 
                InlineKeyboardButton("Uᴘᴅᴀᴛᴇs 🚨", url="https://t.me/+BUF3hu-cKn00Y2Q1")       
            ],
            [
                InlineKeyboardButton("Pʀᴇᴍɪᴜᴍ 💎", url="https://t.me/itzishan?text=I%20Want%20To%20Know%20More%20About%20This%20Plan%20%21%21"), 
                InlineKeyboardButton("Aʙᴏᴜᴛ Mᴇ 😎", callback_data="about") 
            ]
        ])
        caption = (
            f"<blockquote><b><i>Yoo <a href='tg://user?id={user_id}'>{first_name}</a> !! Welcome Aboard</i></b></blockquote>\n"
            f"<blockquote><b><i>I Can Save Posts From Channels or Groups Even When Forwarding is Disabled (Yep, I'm That Powerful 😎) </i></b>\n\n"
            f"<b><i>For Public Channel Just Send the Link of the Post & For Private Channel Use /login First 🔑</i></b></blockquote>"
        )
        await query.message.edit_caption(caption=caption, reply_markup=keyboard, parse_mode=ParseMode.HTML)

    elif query.data == "about":
        bot_username = client.me.username if client.me else "itzishan_bot"
        
        # Changed right side to normal fonts but kept it italic + added bot username link
        about_caption = (
            "<blockquote><b>‣ ⁉️ 𝐌𝐘 𝐃𝐄𝐓𝐀𝐈𝐋𝐒 </b></blockquote>\n"
            f"<blockquote><b><i>• Mʏ Nᴀᴍᴇ</i></b> : <a href='https://t.me/{bot_username}'><i>Save restricted content bot</i></a>\n"
            f"<b><i>• Mʏ Bᴇsᴛ Fʀɪᴇɴᴅ</i></b> : <a href='tg://user?id={user_id}'><i>This Sweetie </i></a>\n"
            "<b><i>• Dᴇᴠᴇʟᴏᴘᴇʀ</i></b> : <a href='https://t.me/itzishan'><i>ISHAN</i></a>\n"
            "<b><i>• Lɪʙʀᴀʀʏ</i></b> : <a href='https://docs.pyrogram.org/'><i>Pyrogram</i></a>\n"
            "<b><i>• Lᴀɴɢᴜᴀɢᴇ</i></b> : <a href='https://www.python.org/'><i>Python 3</i></a>\n"
            "<b><i>• DᴀᴛᴀBᴀsᴇ</i></b> : <a href='https://www.mongodb.com/'><i>Mongo DB</i></a>\n"
            "<b><i>• Bᴏᴛ Sᴇʀᴠᴇʀ</i></b> : <a href='https://www.oracle.com/cloud/'><i>VPS</i></a>\n"
            "<b><i>• Bᴜɪʟᴅ Sᴛᴀᴛᴜs</i></b> : <i>v2.7.1 [Stable]</i></blockquote>"
        )
        back_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ Bᴀᴄᴋ", callback_data="home")]
        ])
        await query.message.edit_caption(caption=about_caption, reply_markup=back_keyboard, parse_mode=ParseMode.HTML)
