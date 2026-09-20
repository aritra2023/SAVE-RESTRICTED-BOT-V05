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

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
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
    
    # Auto-reaction BIG animation ke sath
    try:
        await client.send_reaction(chat_id=message.chat.id, message_id=message.id, emoji="🥰", big=True)
    except:
        pass

    join = await subscribe(client, message)
    if join == 1:
        return
    
    user_id = message.chat.id
    first_name = message.from_user.first_name if message.from_user else "User"

    if len(message.command) <= 1:
        
        # NOTE: Jab image lagani ho, toh is 'image_url' ko uncomment kar dena aur link daal dena
        # image_url = "https://files.catbox.moe/fros5e.jpg" 
        
        # Dark Plan Font for Buttons
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
         
        # Native Telegram Blockquote + Dark Plan Font
        caption = (
            f"> Yᴏᴏ {first_name} !! !! Wᴇʟᴄᴏᴍᴇ Aʙᴏᴀʀᴅ 🥂\n>\n"
            f"> I Cᴀɴ Sᴀᴠᴇ Pᴏsᴛs Fʀᴏᴍ Cʜᴀɴɴᴇʟs ᴏʀ Gʀᴏᴜᴘs Eᴠᴇɴ Wʜᴇɴ Fᴏʀᴡᴀʀᴅɪɴɢ ɪs Dɪsᴀʙʟᴇᴅ (Yᴇᴘ, I'ᴍ Tʜᴀᴛ Pᴏᴡᴇʀғᴜʟ 😎)\n>\n"
            f"> Fᴏʀ Pᴜʙʟɪᴄ Cʜᴀɴɴᴇʟ Jᴜsᴛ Sᴇɴᴅ Tʜᴇ Lɪɴᴋ Oғ Tʜᴇ Pᴏsᴛ & Fᴏʀ Pʀɪᴠᴀᴛᴇ Cʜᴀɴɴᴇʟ Usᴇ /login Fɪʀsᴛ 🔑"
        )
         
        # Abhi sirf text jaayega kyunki image hatane ko bola tha
        await message.reply_text(
            text=caption,
            reply_markup=keyboard
        )

        # -------------------------------------------------------------
        # JAB BHI IMAGE ADD KARNI HO, UPAR WALA "reply_text" DELETE 
        # KARKE NICHE WALA "reply_photo" UNCOMMENT (ENABLE) KAR DENA:
        # -------------------------------------------------------------
        
        # await message.reply_photo(
        #     photo=image_url,
        #     caption=caption,
        #     reply_markup=keyboard
        # )
        
        return  
 
    param = message.command[1] if len(message.command) > 1 else None
    freecheck = await chk_user(message, user_id)
    if freecheck != 1:
        await message.reply("You are a premium user no need of token 😉")
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
    if freecheck != 1:
        await message.reply("You are a premium user no need of token 😉")
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
     
