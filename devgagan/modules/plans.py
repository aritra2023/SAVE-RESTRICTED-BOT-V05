# ---------------------------------------------------
# File Name: plans.py
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

from datetime import timedelta
import pytz
import datetime, time
from devgagan import app
import asyncio
from config import OWNER_ID
from devgagan.core.func import get_seconds
from devgagan.core.mongo import plans_db  
from pyrogram import filters 



@app.on_message(filters.command("rem") & filters.user(OWNER_ID))
async def remove_premium(client, message):
    if len(message.command) == 2:
        user_id = int(message.command[1])  
        user = await client.get_users(user_id)
        data = await plans_db.check_premium(user_id)  
        
        if data and data.get("_id"):
            await plans_db.remove_premium(user_id)
            await message.reply_text("**__User removed successfully!__**")
            await client.send_message(
                chat_id=user_id,
                text=f"> **__ Hey [{user.first_name}](tg://user?id={user_id})!!__**\n\n**__Your premium access has been removed.__**\n**__Thank you for using our service 😊.__**\n\n**__To renew your plan, use__** /plan **__command.__**"
            )
        else:
            await message.reply_text("**__Unable to remove user!\nAre you sure, it was a premium user ID?__**")
    else:
        await message.reply_text("**__Usage :__** `/rem user_id`") 



@app.on_message(filters.command("myplan"))
async def myplan(client, message):
    user_id = message.from_user.id
    user = message.from_user.first_name
    data = await plans_db.check_premium(user_id)  
    if data and data.get("expire_date"):
        expiry = data.get("expire_date")
        expiry_ist = expiry.astimezone(pytz.timezone("Asia/Kolkata"))
        expiry_date = expiry_ist.strftime("%d-%m-%Y")
        expiry_time = expiry_ist.strftime("%I:%M:%S %p")
        
        current_time = datetime.datetime.now(pytz.timezone("Asia/Kolkata"))
        time_left = expiry_ist - current_time
            
        
        days = time_left.days
        hours, remainder = divmod(time_left.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
            
        
        time_left_str = f"{days} days, {hours} hours, {minutes} minutes"
        await message.reply_text(
            f"**__⚜️ Premium User Data :__**\n\n"
            f"**__👤 User__** : __[{user}](tg://user?id={user_id})__\n"
            f"**__⚡ User ID__** : `{user_id}`\n"
            f"**__⏰ Time Left__** : __{time_left_str}__\n"
            f"**__⌛️ Expiry Date__** : __{expiry_date}__\n"
            f"**__⏱️ Expiry Time__** : __{expiry_time}__"
        )   
    else:
        await message.reply_text(f"**__Hey {user},\n\nYou do not have any active premium plans.__**")
        


@app.on_message(filters.command("check") & filters.user(OWNER_ID))
async def get_premium(client, message):
    if len(message.command) == 2:
        user_id = int(message.command[1])
        user = await client.get_users(user_id)
        data = await plans_db.check_premium(user_id)  
        if data and data.get("expire_date"):
            expiry = data.get("expire_date") 
            expiry_ist = expiry.astimezone(pytz.timezone("Asia/Kolkata"))
            expiry_date = expiry_ist.strftime("%d-%m-%Y")
            expiry_time = expiry_ist.strftime("%I:%M:%S %p")          
            
            current_time = datetime.datetime.now(pytz.timezone("Asia/Kolkata"))
            time_left = expiry_ist - current_time
            
            
            days = time_left.days
            hours, remainder = divmod(time_left.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            
            
            time_left_str = f"{days} days, {hours} hours, {minutes} minutes"
            await message.reply_text(
                f"**__⚜️ Premium User Data :__**\n\n"
                f"**__👤 User__** : __[{user.first_name}](tg://user?id={user_id})__\n"
                f"**__⚡ User ID__** : `{user_id}`\n"
                f"**__⏰ Time Left__** : __{time_left_str}__\n"
                f"**__⌛️ Expiry Date__** : __{expiry_date}__\n"
                f"**__⏱️ Expiry Time__** : __{expiry_time}__"
            )
        else:
            await message.reply_text("**__No premium data for this user was found in the database!__**")
    else:
        await message.reply_text("**__Usage :__** `/check user_id`")


@app.on_message(filters.command("add") & filters.user(OWNER_ID))
async def give_premium_cmd_handler(client, message):
    if len(message.command) == 4:
        time_zone = datetime.datetime.now(pytz.timezone("Asia/Kolkata"))
        join_date = time_zone.strftime("%d-%m-%Y")
        join_time = time_zone.strftime("%I:%M:%S %p")
        
        user_id = int(message.command[1])
        user = await client.get_users(user_id)
        time = message.command[2]+" "+message.command[3]
        seconds = await get_seconds(time)
        if seconds > 0:
            expiry_time_delta = datetime.datetime.now() + datetime.timedelta(seconds=seconds)  
            await plans_db.add_premium(user_id, expiry_time_delta)  
            data = await plans_db.check_premium(user_id)
            expiry = data.get("expire_date")   
            
            expiry_date = expiry.astimezone(pytz.timezone("Asia/Kolkata")).strftime("%d-%m-%Y")
            expiry_time = expiry.astimezone(pytz.timezone("Asia/Kolkata")).strftime("%I:%M:%S %p")
            
            await message.reply_text(
                f"**__Premium added successfully ✅__**\n\n"
                f"**__👤 User__** : __[{user.first_name}](tg://user?id={user_id})__\n"
                f"**__⚡ User ID__** : `{user_id}`\n"
                f"**__⏰ Premium Access__** : `{time}`\n\n"
                f"**__⏳ Joining Date__** : __{join_date}__\n"
                f"**__⏱️ Joining Time__** : __{join_time}__\n\n"
                f"**__⌛️ Expiry Date__** : __{expiry_date}__\n"
                f"**__⏱️ Expiry Time__** : __{expiry_time}__\n\n"
                f"> **__Powered by @Itzishan__**", 
                disable_web_page_preview=True
            )
            
            await client.send_message(
                chat_id=user_id,
                text=(
                    f"> **__ Hey [{user.first_name}](tg://user?id={user_id})!!__**\n\n"
                    f"**__Thank you for purchasing premium.__**\n"
                    f"**__Enjoy !! ✨🎉__**\n\n"
                    f"**__⏰ Premium Access__** : `{time}`\n"
                    f"**__⏳ Joining Date__** : __{join_date}__\n"
                    f"**__⏱️ Joining Time__** : __{join_time}__\n\n"
                    f"**__⌛️ Expiry Date__** : __{expiry_date}__\n"
                    f"**__⏱️ Expiry Time__** : __{expiry_time}__"
                ), 
                disable_web_page_preview=True              
            )
                    
        else:
            await message.reply_text("**__Invalid time format. Please use '1 day', '1 hour', '1 min', '1 month', or '1 year'.__**")
    else:
        await message.reply_text("**__Usage :__** `/add user_id time` **__(e.g., '1 day', '1 hour', '1 month', '1 year')__**")


@app.on_message(filters.command("transfer"))
async def transfer_premium(client, message):
    if len(message.command) == 2:
        new_user_id = int(message.command[1])  # The user ID to whom premium is transferred
        sender_user_id = message.from_user.id  # The current premium user issuing the command
        sender_user = await client.get_users(sender_user_id)
        new_user = await client.get_users(new_user_id)
        
        # Fetch sender's premium plan details
        data = await plans_db.check_premium(sender_user_id)
        
        if data and data.get("_id"):  # Verify sender is already a premium user
            expiry = data.get("expire_date")  
            
            # Remove premium for the sender
            await plans_db.remove_premium(sender_user_id)
            
            # Add premium for the new user with the same expiry date
            await plans_db.add_premium(new_user_id, expiry)
            
            # Convert expiry date to IST format for display
            expiry_date = expiry.astimezone(pytz.timezone("Asia/Kolkata")).strftime("%d-%m-%Y")
            expiry_time = expiry.astimezone(pytz.timezone("Asia/Kolkata")).strftime("%I:%M:%S %p")
            
            time_zone = datetime.datetime.now(pytz.timezone("Asia/Kolkata"))
            current_date = time_zone.strftime("%d-%m-%Y")
            current_time_str = time_zone.strftime("%I:%M:%S %p")
            
            # Confirmation message to the sender
            await message.reply_text(
                f"✅ **__Premium Plan Transferred Successfully!__**\n\n"
                f"**__👤 From__** : __[{sender_user.first_name}](tg://user?id={sender_user_id})__\n"
                f"**__👤 To__** : __[{new_user.first_name}](tg://user?id={new_user_id})__\n"
                f"**__⏳ Expiry Date__** : __{expiry_date}__\n"
                f"**__⏱ Expiry Time__** : __{expiry_time}__\n\n"
                f"> **__Powered by @Itzishan__**"
            )
            
            # Notification to the new user
            await client.send_message(
                chat_id=new_user_id,
                text=(
                    f"> **__ Hey [{new_user.first_name}](tg://user?id={new_user_id})!!__**\n\n"
                    f"**__🎉 Your Premium Plan has been Transferred!__**\n"
                    f"**__🛡️ Transferred From__** : __[{sender_user.first_name}](tg://user?id={sender_user_id})__\n\n"
                    f"**__⏳ Expiry Date__** : __{expiry_date}__\n"
                    f"**__⏱ Expiry Time__** : __{expiry_time}__\n"
                    f"**__📅 Transferred On__** : __{current_date}__\n"
                    f"**__⏱ Transfer Time__** : __{current_time_str}__\n\n"
                    f"**__Enjoy the Service! ✨__**"
                )
            )
        else:
            await message.reply_text("⚠️ **__You are not a Premium user!\n\nOnly Premium users can transfer their plans.__**")
    else:
        await message.reply_text("⚠️ **__Usage :__** `/transfer user_id`\n\n**__Replace `user_id` with the new user's ID.__**")


async def premium_remover():
    all_users = await plans_db.premium_users()
    removed_users = []
    not_removed_users = []

    for user_id in all_users:
        try:
            user = await app.get_users(user_id)
            chk_time = await plans_db.check_premium(user_id)

            if chk_time and chk_time.get("expire_date"):
                expiry_date = chk_time["expire_date"]

                if expiry_date <= datetime.datetime.now():
                    name = user.first_name
                    await plans_db.remove_premium(user_id)
                    await app.send_message(user_id, text=f"**__Hello {name}, your premium subscription has expired.__**")
                    print(f"{name}, your premium subscription has expired.")
                    removed_users.append(f"{name} ({user_id})")
                else:
                    name = user.first_name
                    current_time = datetime.datetime.now()
                    time_left = expiry_date - current_time

                    days = time_left.days
                    hours, remainder = divmod(time_left.seconds, 3600)
                    minutes, seconds = divmod(remainder, 60)

                    if days > 0:
                        remaining_time = f"{days} days, {hours} hours, {minutes} minutes, {seconds} seconds"
                    elif hours > 0:
                        remaining_time = f"{hours} hours, {minutes} minutes, {seconds} seconds"
                    elif minutes > 0:
                        remaining_time = f"{minutes} minutes, {seconds} seconds"
                    else:
                        remaining_time = f"{seconds} seconds"

                    print(f"{name} : Remaining Time : {remaining_time}")
                    not_removed_users.append(f"{name} ({user_id})")
        except:
            await plans_db.remove_premium(user_id)
            print(f"Unknown users captured : {user_id} removed")
            removed_users.append(f"Unknown ({user_id})")

    return removed_users, not_removed_users


@app.on_message(filters.command("freez") & filters.user(OWNER_ID))
async def refresh_users(_, message):
    removed_users, not_removed_users = await premium_remover()
    # Create a summary message
    removed_text = "\n".join(removed_users) if removed_users else "No users removed."
    not_removed_text = "\n".join(not_removed_users) if not_removed_users else "No users remaining with premium."
    summary = (
        f"**__Here is Summary...__**\n\n"
        f"**__Removed Users:__**\n__{removed_text}__\n\n"
        f"**__Not Removed Users:__**\n__{not_removed_text}__"
    )
    await message.reply(summary)
