# ---------------------------------------------------
# File Name: start.py
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

from pyrogram import filters
from devgagan import app
from config import OWNER_ID
from devgagan.core.func import subscribe
import asyncio
from devgagan.core.func import *
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.raw.functions.bots import SetBotInfo
from pyrogram.raw.types import InputUserSelf

from pyrogram.types import BotCommand, InlineKeyboardButton, InlineKeyboardMarkup
 
@app.on_message(filters.command("set"))
async def set(_, message):
    if message.from_user.id not in OWNER_ID:
        await message.reply("You are not authorized to use this command.")
        return
     
    await app.set_bot_commands([
        BotCommand("start", "🚀 Start the bot"),
        BotCommand("batch", "🫠 Extract in bulk"),
        BotCommand("login", "🔑 Get into the bot"),
        BotCommand("logout", "🚪 Get out of the bot"),
        BotCommand("token", "🎲 Get 3 hours free access"),
        BotCommand("adl", "👻 Download audio from 30+ sites"),
        BotCommand("dl", "💀 Download videos from 30+ sites"),
        BotCommand("freez", "🧊 Remove all expired user"),
        BotCommand("pay", "₹ Pay now to get subscription"),
        BotCommand("status", "⟳ Refresh Payment status"),
        BotCommand("transfer", "💘 Gift premium to others"),
        BotCommand("myplan", "⌛ Get your plan details"),
        BotCommand("add", "➕ Add user to premium"),
        BotCommand("rem", "➖ Remove from premium"),
        BotCommand("session", "🧵 Generate Pyrogramv2 session"),
        BotCommand("settings", "⚙️ Personalize things"),
        BotCommand("stats", "📊 Get stats of the bot"),
        BotCommand("plan", "🗓️ Check our premium plans"),
        BotCommand("terms", "🥺 Terms and conditions"),
        BotCommand("speedtest", "🚅 Speed of server"),
        BotCommand("lock", "🔒 Protect channel from extraction"),
        BotCommand("gcast", "⚡ Broadcast message to bot users"),
        BotCommand("help", "❓ If you're a noob, still!"),
        BotCommand("cancel", "🚫 Cancel batch process")
    ])
 
    await message.reply("✅ Commands configured successfully!")
 
 
 
 
help_pages = [
    (
        "📝 **__Bot Commands Overview (1/2)__**:\n\n"
        "> **1. /add userID**\n"
        "__Add user to premium (Owner only)__\n\n"
        "> **2. /rem userID**\n"
        "__Remove user from premium (Owner only)__\n\n"
        "> **3. /transfer userID**\n"
        "__Transfer premium to your beloved major purpose for resellers (Premium members only)__\n\n"
        "> **4. /get**\n"
        "__Get all user IDs (Owner only)__\n\n"
        "> **5. /lock**\n"
        "__Lock channel from extraction (Owner only)__\n\n"
        "> **6. /dl link**\n"
        "__Download videos (Not available in v3 if you are using)__\n\n"
        "> **7. /adl link**\n"
        "__Download audio (Not available in v3 if you are using)__\n\n"
        "> **8. /login**\n"
        "__Log into the bot for private channel access__\n\n"
        "> **9. /batch**\n"
        "__Bulk extraction for posts (After login)__\n"
    ),
    (
        "📝 **__Bot Commands Overview (2/2)__**:\n\n"
        "> **10. /settings**\n"
        "__01. SetChatID : To directly upload in channel or group or user's dm use it with -100[chatID]__\n"
        "__02. SetRename : To add custom rename tag or username of your channels__\n"
        "__03. Caption : To add custom caption__\n"
        "__04. ReplaceWords : Can be used for words in deleted set via REMOVE WORDS__\n"
        "__05. Reset : To set the things back to default__\n\n"
        "> **__You can set CUSTOM THUMBNAIL, PDF WATERMARK, VIDEO WATERMARK, SESSION-based login, etc. from settings__**\n\n"
        "> **11. /logout**\n"
        "__Logout from the bot__\n\n"
        "> **12. /stats**\n"
        "__Get bot stats__\n\n"
        "> **13. /plan**\n"
        "__Check premium plans__\n\n"
        "> **14. /speedtest**\n"
        "__Test the server speed (not available in v3)__\n\n"
        "> **15. /terms**\n"
        "__Terms and conditions__\n\n"
        "> **16. /cancel**\n"
        "__Cancel ongoing batch process__\n\n"
        "> **17. /myplan**\n"
        "__Get details about your plans__\n\n"
        "> **18. /session**\n"
        "__Generate Pyrogram V2 session__\n\n"
        "> **__Powered by @Itzishan**\n"
    )
]
 
 
async def send_or_edit_help_page(_, message, page_number):
    if page_number < 0 or page_number >= len(help_pages):
        return
 
     
    prev_button = InlineKeyboardButton("◀️ Pʀᴇᴠɪᴏᴜs", callback_data=f"help_prev_{page_number}")
    next_button = InlineKeyboardButton("Nᴇxᴛ ▶️", callback_data=f"help_next_{page_number}")
 
     
    buttons = []
    if page_number > 0:
        buttons.append(prev_button)
    if page_number < len(help_pages) - 1:
        buttons.append(next_button)
 
     
    keyboard = InlineKeyboardMarkup([buttons])
 
     
    await message.delete()
 
     
    await message.reply(
        help_pages[page_number],
        reply_markup=keyboard
    )
 
 
@app.on_message(filters.command("help"))
async def help(client, message):
    join = await subscribe(client, message)
    if join == 1:
        return
 
     
    await send_or_edit_help_page(client, message, 0)
 
 
@app.on_callback_query(filters.regex(r"help_(prev|next)_(\d+)"))
async def on_help_navigation(client, callback_query):
    action, page_number = callback_query.data.split("_")[1], int(callback_query.data.split("_")[2])
 
    if action == "prev":
        page_number -= 1
    elif action == "next":
        page_number += 1
 
     
    await send_or_edit_help_page(client, callback_query.message, page_number)
 
     
    await callback_query.answer()
 
 
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
 
@app.on_message(filters.command("terms") & filters.private)
async def terms(client, message):
    terms_text = (
        "> 📜 **__TERMS & CONDITIONS__**\n"
        "__Users Are Solely Responsible For Their Actions And Content. The Service Does Not Promote Or Support Copyrighted Or Illegal Activity.__\n\n"
        "> **__Service Availability__**\n"
        "__Purchase Of Any Plan Does Not Guarantee Service Availability, Uptime, Or Continuity. The Service May Be Modified Or Discontinued At Any Time Without Notice.__\n\n"
        "> **__Authorization & Access Control__**\n"
        "__User Access, Authorization, Or Banning Is Entirely At The Service Provider’s Discretion.__\n\n"
        "> **__Payments & Feature Access__**\n"
        "__Payment Does Not Guarantee Access To Any Feature, Including The /Batch Command. All decisions regarding authorization are made by our mood.__\n\n"
        "> **__No Right of Claim__**\n"
        "__No Refunds, Compensation, Or Claims May Be Made For Denied Access, Service Interruptions, Or Account Restrictions.__\n"
    )
     
    buttons = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("📋 Sᴇᴇ Pʟᴀɴs", callback_data="see_plan")],
            [InlineKeyboardButton("💬 Cᴏɴᴛᴀᴄᴛ Nᴏᴡ", url="https://t.me/itzishan")],
        ]
    )
    await message.reply_text(terms_text, reply_markup=buttons)
 
 
@app.on_message(filters.command("plan") & filters.private)
async def plan(client, message):
    plan_text = (
        "> 💳 **__Premium Plan__**\n"
        "__Our Plan Start from 4$ or 350₹ and can be accepted via Google Pay, PhonePe or PayPal. ( Terms & Conditions applied )__\n\n"
        "> 📥 **__Download Limit__**\n"
        "__Users can download up to 10,000 files in a single batch command.__\n\n"
        "> 📦 **__Batch Command__**\n"
        "__You will get /batch command unlocked for your bulk files extraction.__\n\n"
        "> ♻️ **__Keep Patience__**\n"
        "__Users are advised to wait for the process to automatically cancel before proceeding with any downloads or uploads.__\n\n"
        "> 📜 **__Terms & Conditions__**\n"
        "__For further details and to read our terms and conditions, send /terms or click See Terms below ⬇️__\n"
    )
     
    buttons = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("📜 Sᴇᴇ Tᴇʀᴍs", callback_data="see_terms")],
            [InlineKeyboardButton("💬 Cᴏɴᴛᴀᴄᴛ Nᴏᴡ", url="https://t.me/itzishan")],
        ]
    )
    await message.reply_text(plan_text, reply_markup=buttons)
 
 
@app.on_callback_query(filters.regex("see_plan"))
async def see_plan(client, callback_query):
    plan_text = (
        "> 💳 **__Premium Plan__**\n"
        "__Our Plan Start from 4$ to 350₹ and can be accepted via Google Pay, PhonePe or PayPal. ( Terms & Conditions applied )__\n\n"
        "> 📥 **__Download Limit__**\n"
        "__Users can download up to 10,000 files in a single batch command.__\n\n"
        "> 📦 **__Batch Command__**\n"
        "__You will get /batch command unlocked for your bulk files extraction.__\n\n"
        "> ♻️ **__Keep Patience__**\n"
        "__Users are advised to wait for the process to automatically cancel before proceeding with any downloads or uploads.__\n\n"
        "> 📜 **__Terms & Conditions__**\n"
        "__For further details and to read our terms and conditions, send /terms or click See Terms below __\n"
    )
     
    buttons = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("📜 Sᴇᴇ Tᴇʀᴍs", callback_data="see_terms")],
            [InlineKeyboardButton("💬 Cᴏɴᴛᴀᴄᴛ Nᴏᴡ", url="https://t.me/itzishan")],
        ]
    )
    await callback_query.message.edit_text(plan_text, reply_markup=buttons)
 
 
@app.on_callback_query(filters.regex("see_terms"))
async def see_terms(client, callback_query):
    terms_text = (
        "> 📜 **__TERMS & CONDITIONS__**\n"
        "__Users Are Solely Responsible For Their Actions And Content. The Service Does Not Promote Or Support Copyrighted Or Illegal Activity.__\n\n"
        "> **__Service Availability__**\n"
        "__Purchase Of Any Plan Does Not Guarantee Service Availability, Uptime, Or Continuity. The Service May Be Modified Or Discontinued At Any Time Without Notice.__\n\n"
        "> **__Authorization & Access Control__**\n"
        "__User Access, Authorization, Or Banning Is Entirely At The Service Provider’s Discretion.__\n\n"
        "> **__Payments & Feature Access__**\n"
        "__Payment Does Not Guarantee Access To Any Feature, Including The /Batch Command. All decisions regarding authorization are made by our mood.__\n\n"
        "> **__No Right of Claim__**\n"
        "__No Refunds, Compensation, Or Claims May Be Made For Denied Access, Service Interruptions, Or Account Restrictions.__\n"
    )
     
    buttons = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("📋 Sᴇᴇ Pʟᴀɴs", callback_data="see_plan")],
            [InlineKeyboardButton("💬 Cᴏɴᴛᴀᴄᴛ Nᴏᴡ", url="https://t.me/itzishan")],
        ]
    )
    await callback_query.message.edit_text(terms_text, reply_markup=buttons)
